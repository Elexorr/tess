import os
from PIL import Image, ImageDraw, ImageFont

input_dir = "images"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()

for filename in os.listdir(input_dir):
    if filename.lower().endswith(".png"):
        filepath = os.path.join(input_dir, filename)

        img = Image.open(filepath)
        draw = ImageDraw.Draw(img)

        text = os.path.splitext(filename)[0]

        # veľkosť textu
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # umiestnenie
        padding = 10
        x = img.width - text_width - 2 * padding
        y = 10

        # biely podklad
        draw.rectangle(
            [(x - padding, y - padding),
             (x + text_width + padding, y + text_height + padding)],
            fill="white"
        )

        # čierny text
        draw.text(
            (x, y),
            text,
            font=font,
            fill="black"
        )

        img.save(os.path.join(output_dir, filename))

print("Hotovo – obrázky s čiernym textom na bielom pozadí sú v priečinku output/")