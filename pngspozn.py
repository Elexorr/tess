import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# ---------- nastavenia ----------
input_dir = "pics"
output_dir = "output2"

excel_path = "final_poznamky.xlsx"

font_size_title = 40
font_size_notes = 24
line_spacing = 6
top_margin = 5        # blízko horného okraju
left_margin = 5       # blízko ľavého okraju
max_text_width_frac = 0.9
# ---------------------------------

os.makedirs(output_dir, exist_ok=True)

# ---------- fonty ----------
try:
    title_font = ImageFont.truetype("arial.ttf", font_size_title)
    notes_font = ImageFont.truetype("arial.ttf", font_size_notes)
except Exception:
    title_font = ImageFont.load_default()
    notes_font = ImageFont.load_default()

# ---------- EXCEL ----------
df = pd.read_excel(excel_path, engine="openpyxl", dtype=str).fillna("")
cols = list(df.columns)
key_col = cols[0]
note_cols = cols[1:]

# prefixovanie podľa názvu stĺpca
def get_prefix(col_name):
    col_lower = col_name.lower()
    if "zmeny na lc" in col_lower:
        return "LC: "
    elif "zmeny na oc" in col_lower:
        return "O-C: "
    elif "simbad" in col_lower:
        return "simbad: "
    else:
        return ""

excel_notes = {}

for _, row in df.iterrows():
    key = str(row[key_col]).strip()
    if not key:
        continue

    notes = []
    for c in note_cols:
        val = str(row[c]).strip()
        if val:
            notes.append(f"{get_prefix(c)}{val}")
    excel_notes[key.lower()] = notes

# ---------- zalamovanie ----------
def wrap_text(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    cur = words[0]

    for w in words[1:]:
        test = cur + " " + w
        w_px = draw.textbbox((0, 0), test, font=font)[2]
        if w_px <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w

    lines.append(cur)
    return lines

# ---------- hlavná slučka ----------
for filename in sorted(os.listdir(input_dir)):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    img = Image.open(os.path.join(input_dir, filename)).convert("RGBA")
    draw_tmp = ImageDraw.Draw(img)

    base_name = os.path.splitext(filename)[0]
    object_name = base_name.replace("_", " ")
    lookup = object_name.lower()

    total_width = int(img.width * max_text_width_frac)
    x_left = left_margin  # úplne vľavo pre poznámky

    # ---------- text ----------
    title_lines = wrap_text(draw_tmp, object_name, title_font, total_width)

    excel_lines = []
    for n in excel_notes.get(lookup, []):
        excel_lines += wrap_text(draw_tmp, n, notes_font, total_width)

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # nastavenie y tak, aby názov aj poznámky začínali hore
    y = top_margin

    # najprv nakreslíme názov objektu v strede
    y_title = y
    for line in title_lines:
        w, h = draw.textbbox((0, 0), line, font=title_font)[2:]
        draw.text(((img.width - w) // 2, y_title), line, font=title_font, fill=(0, 0, 0, 255))
        y_title += h + line_spacing

    # potom poznámky vľavo na úrovni hornej časti názvu
    y_notes = top_margin
    for line in excel_lines:
        _, h = draw.textbbox((0, 0), line, font=notes_font)[2:]
        draw.text((x_left, y_notes), line, font=notes_font, fill=(0, 0, 0, 255))
        y_notes += h + line_spacing

    combined = Image.alpha_composite(img, overlay)
    combined.convert("RGB").save(os.path.join(output_dir, filename))

print("Hotovo — názov hore v strede, poznámky vľavo hore")
