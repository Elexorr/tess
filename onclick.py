import matplotlib.pyplot as plt
import numpy as np

# Generate some data
x = np.random.rand(100)
y = np.random.rand(100)

def onclick(event):
    ix, iy = event.xdata, event.ydata
    print(f'x = {ix}, y = {iy}')

cid = plt.gcf().canvas.mpl_connect('button_press_event', onclick)
# Create a scatter plot
plt.scatter(x, y)
plt.show()

