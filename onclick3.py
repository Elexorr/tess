import matplotlib.pyplot as plt
import matplotlib.lines as lines

# Create a list to store the line objects
lines_list = []

def onclick(event):
    x, y = event.xdata, event.ydata
    if x is not None and y is not None:
        ax = plt.gca()
        line = lines.Line2D([x, x + 0.1], [y, y + 0.1], color='blue')
        ax.add_artist(line)
        lines_list.append(line)
        plt.draw()

fig = plt.figure()
ax = fig.add_subplot(111)

# Connect the click event to the onclick function
fig.canvas.mpl_connect('button_press_event', onclick)

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.show()