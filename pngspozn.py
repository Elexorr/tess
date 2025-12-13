import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# ---------- nastavenia ----------
input_dir = "pics"
output_dir = "output2"
oc_dir = "o-c"

excel_path = "final_poznamky.xlsx"
txt_path = "final_info-oc.txt"

font_size_title = 40
font_size_notes = 24
line_spacing = 6
top_margin = 20
column_gap = 40
max_text_width_frac = 0.9

oc_width_frac = 0.175      # šírka vloženého o-c diagramu (relatívna)
oc_bottom_margin = 20     # odsadenie od spodného okraja
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

excel_notes = {}

for _, row in df.iterrows():
    key = str(row[key_col]).strip()
    if not key:
        continue

    notes = [str(row[c]).strip() for c in note_cols if str(row[c]).strip()]
    excel_notes[key.lower()] = notes

# ---------- TXT ----------
txt_notes = {}

if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 3:
                continue

            key = f"{parts[0]} {parts[1]}".lower()
            note = " ".join(parts[2:]).strip()

            if note:
                txt_notes.setdefault(key, []).append(f"o-c: {note}")

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
    col_width = (total_width - column_gap) // 2

    x_left = (img.width - total_width) // 2
    x_right = x_left + col_width + column_gap

    # ---------- text ----------
    title_lines = wrap_text(draw_tmp, object_name, title_font, total_width)

    excel_lines = []
    for n in excel_notes.get(lookup, []):
        excel_lines += wrap_text(draw_tmp, n, notes_font, col_width)

    txt_lines = []
    for n in txt_notes.get(lookup, []):
        txt_lines += wrap_text(draw_tmp, n, notes_font, col_width)

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    y = top_margin

    for line in title_lines:
        w, h = draw.textbbox((0, 0), line, font=title_font)[2:]
        draw.text(((img.width - w) // 2, y), line,
                  font=title_font, fill=(0, 0, 0, 255))
        y += h + line_spacing

    y += line_spacing * 2

    y_left = y
    y_right = y

    for line in excel_lines:
        _, h = draw.textbbox((0, 0), line, font=notes_font)[2:]
        draw.text((x_left, y_left), line,
                  font=notes_font, fill=(0, 0, 0, 255))
        y_left += h + line_spacing

    for line in txt_lines:
        _, h = draw.textbbox((0, 0), line, font=notes_font)[2:]
        draw.text((x_right, y_right), line,
                  font=notes_font, fill=(0, 0, 0, 255))
        y_right += h + line_spacing

    combined = Image.alpha_composite(img, overlay)

    # ---------- vloženie o-c diagramu ----------
    oc_path = None
    for ext in (".png", ".jpg", ".jpeg"):
        test = os.path.join(oc_dir, base_name + ext)
        if os.path.exists(test):
            oc_path = test
            break

    if oc_path:
        oc_img = Image.open(oc_path).convert("RGBA")

        new_w = int(img.width * oc_width_frac)
        scale = new_w / oc_img.width
        new_h = int(oc_img.height * scale)

        oc_img = oc_img.resize((new_w, new_h), Image.LANCZOS)

        x_oc = int(img.width * 0.75 - new_w / 2)
        y_oc = img.height - new_h - oc_bottom_margin

        combined.paste(oc_img, (x_oc, y_oc), oc_img)

    combined.convert("RGB").save(os.path.join(output_dir, filename))

print("Hotovo — o-c diagramy vložené, ak existujú")
