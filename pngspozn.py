import os
import textwrap
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# ---------- nastavenia ----------
input_dir = "images"
output_dir = "output2"
excel_path = "final_poznamky.xlsx"
font_size_title = 40
font_size_notes = 24
line_spacing = 6
bg_opacity = 0           # 0 = úplne priehľadné pozadie
top_margin = 20          # odsadenie od horného okraja
max_text_width_frac = 0.8  # šírka textu ako zlomok šírky obrázka
# ---------------------------------

os.makedirs(output_dir, exist_ok=True)

try:
    title_font = ImageFont.truetype("arial.ttf", font_size_title)
    notes_font = ImageFont.truetype("arial.ttf", font_size_notes)
except Exception:
    title_font = ImageFont.load_default()
    notes_font = ImageFont.load_default()

# načítanie excelu
df = pd.read_excel(excel_path, engine="openpyxl", dtype=str).fillna("")
cols = list(df.columns)
key_col = cols[0]
note_cols = cols[1:]
notes_map = {}
for _, row in df.iterrows():
    key = str(row[key_col]).strip()
    if not key:
        continue
    notes = [str(row[c]).strip() for c in note_cols if str(row[c]).strip()]
    notes_map[key.lower()] = notes

def wrap_text_to_pixels(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = cur + " " + w
        bbox = draw.textbbox((0,0), test, font=font)
        w_px = bbox[2] - bbox[0]
        if w_px <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

# spracovanie obrázkov
for filename in sorted(os.listdir(input_dir)):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue
    filepath = os.path.join(input_dir, filename)
    img = Image.open(filepath).convert("RGBA")

    base_name = os.path.splitext(filename)[0]
    lookup = base_name.lower()

    max_text_width = int(img.width * max_text_width_frac)

    # pripravíme text
    draw_tmp = ImageDraw.Draw(img)
    text_lines = wrap_text_to_pixels(draw_tmp, base_name, title_font, max_text_width)
    notes = notes_map.get(lookup, [])
    for note in notes:
        text_lines += wrap_text_to_pixels(draw_tmp, note, notes_font, max_text_width)

    # overlay pre text
    overlay = Image.new("RGBA", img.size, (255,255,255,0))
    draw = ImageDraw.Draw(overlay)

    # začneme z horného okraja
    y0 = top_margin

    for i, line in enumerate(text_lines):
        font = title_font if i < len(wrap_text_to_pixels(draw_tmp, base_name, title_font, max_text_width)) else notes_font
        bbox = draw.textbbox((0,0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = (img.width - line_w) // 2  # horizontálne centrované
        draw.text((x, y0), line, font=font, fill=(0,0,0,255))
        line_h = bbox[3] - bbox[1]
        y0 += line_h + line_spacing

    # zlúčime overlay s obrázkom
    combined = Image.alpha_composite(img, overlay).convert("RGB")
    out_path = os.path.join(output_dir, filename)
    combined.save(out_path)

print("Hotovo — text je čierny a horizontálne centrovaný hore")
