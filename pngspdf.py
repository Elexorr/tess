import os
from PIL import Image, ImageOps

input_dir = "output2"       # priečinok so vstupnými obrázkami
output_pdf = "output.pdf"  # výsledný PDF súbor
os.makedirs(os.path.dirname(output_pdf) or ".", exist_ok=True)

# A4 300 DPI (na výšku)
PAGE_WIDTH = 2480   # px
PAGE_HEIGHT = 3508  # px

# rozloženie: 2 stĺpce x 5 riadkov = 10 obrázkov na stranu
COLS = 2
ROWS = 5
IMAGES_PER_PAGE = COLS * ROWS

# medzera / okraj (nastav na 0 ak chceš bez medzier)
PADDING = 20

# veľkosť bunky
cell_w = (PAGE_WIDTH - (COLS + 1) * PADDING) // COLS
cell_h = (PAGE_HEIGHT - (ROWS + 1) * PADDING) // ROWS

# načítanie súborov (zoradené)
files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
pages = []

for i in range(0, len(files), IMAGES_PER_PAGE):
    batch = files[i:i+IMAGES_PER_PAGE]
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")

    for idx, filename in enumerate(batch):
        img_path = os.path.join(input_dir, filename)
        img = Image.open(img_path).convert("RGB")

        # vytvoríme bielu kartu bunky, do ktorej vložíme zachované náhľady
        cell = Image.new("RGB", (cell_w, cell_h), "white")

        # zmenšíme obrázok tak, aby sa vmestil do bunky bez deformácie (contain zachová pomer strán)
        thumb = ImageOps.contain(img, (cell_w, cell_h), method=Image.LANCZOS)

        # centrovanie náhľadu v bunke
        paste_x = (cell_w - thumb.width) // 2
        paste_y = (cell_h - thumb.height) // 2
        cell.paste(thumb, (paste_x, paste_y))

        # vypočítame pozíciu bunky na stránke
        row = idx // COLS
        col = idx % COLS
        x = PADDING + col * (cell_w + PADDING)
        y = PADDING + row * (cell_h + PADDING)

        page.paste(cell, (x, y))

    pages.append(page)

# uložiť všetky stránky do jedného PDF
if pages:
    pages[0].save(output_pdf, save_all=True, append_images=pages[1:])

print(f"Hotovo — PDF vytvorené: {output_pdf}")