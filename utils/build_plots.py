import matplotlib.pyplot as plt
import pandas as pd


def series_plot(s, pathname):
    fig, ax = plt.subplots(figsize=[4, 2])

    color1 = "xkcd:salmon"

    data.a.plot(ax=ax, style=".-", color=color1)

    ax.spines["bottom"].set_color(color1)
    ax.spines["top"].set_color(color1)
    ax.spines["right"].set_color(color1)
    ax.spines["left"].set_color(color1)
    ax.tick_params(axis="x", colors=color1)
    ax.tick_params(axis="y", colors=color1)

    plt.savefig(pathname, transparent=True)


data = pd.DataFrame({"a": [0, 1, 2, 2.5, 3, 3.1, 4]})

series_plot(data.a, pathname="mkdocs/assets/img/plots/test.svg")
