import matplotlib.pyplot as plt

# Vytvorte si prázdny graf
fig, ax = plt.subplots()

# Definujte funkciu na reakciu na kliknutie myšou
def on_mouse_click(event):
    if event.button == 1:  # Kontrola, či bola stlačená ľavá myš
        x, y = event.xdata, event.ydata  # Získanie súradníc kliku myšou
        ax.plot(x, y, 'ro')  # Kreslenie červeného bodu na mieste kliku
        plt.draw()  # Aktualizácia grafu

# Pripojte funkciu k udalostiam myši
fig.canvas.mpl_connect('button_press_event', on_mouse_click)

# Zobrazte graf
plt.show()