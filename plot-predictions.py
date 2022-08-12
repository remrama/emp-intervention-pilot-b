"""Hypothesized results
"""
import os
import argparse
import numpy as np
import utils
import matplotlib.pyplot as plt
utils.load_matplotlib_settings()

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True

config = utils.load_config()

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--which", type=str, default="sleep",
    choices=["sleep", "learning"], help="Choose which prediction to plot")
args = parser.parse_args()

WHICH = args.which

export_fname = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib",  f"task-eat_prediction-{WHICH}.png")
utils.make_pathdir_if_not_exists(export_fname)

# ylabel = r"Empathic accuracy, $r_{E}$"
ylabel = "Empathic accuracy"

if WHICH == "sleep":
    xlabel = "Cue condition"
    colors = ["white", "purple"]
    xticklabels = ["Uncued", "Cued"]
    legend_labels = ["Pre-sleep", "Post-sleep"]
    yvals = [.5, .5, .5, .7]
elif WHICH == "learning":
    xlabel = "Intervention"
    colors = ["white", "gainsboro"]
    xticklabels = ["Attention\ntask", "Compassion\nintervention"]
    legend_labels = ["Pre-intervention", "Post-intervention"]
    yvals = [.5, .5, .5, .7]

n_variables = len(yvals)


XLIM_EDGEBUFFER = .5
XLIM_GAPBUFFER = .5
xvals = np.array([0., 1, 2, 3])
xvals[2:] += XLIM_GAPBUFFER
colors *= 2

FIGSIZE = (2.5, 3.5)

BAR_KWARGS = {
    "width": .8,
    "linewidth": 2,
    "edgecolor": "black",
}

with plt.xkcd():

    _, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

    ax.bar(xvals, yvals, color=colors, **BAR_KWARGS)

    ax.axhline(0, linewidth=1, linestyle="solid", color="black")
    ax.set_xticks([xvals[:2].mean(), xvals[2:].mean()])
    ax.set_xticklabels(xticklabels)
    #ylabel += "\n" + r"$\rightarrow$ perfect agreement"
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.tick_params(bottom=False, top=False, right=False, which="both", axis="both")
    xmin = xvals[0] - BAR_KWARGS["width"]/2 - XLIM_EDGEBUFFER
    xmax = xvals[-1] + BAR_KWARGS["width"]/2 + XLIM_EDGEBUFFER
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-.2, 1.4)
    ax.yaxis.set_major_locator(plt.NullLocator())
    # ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
    #     minor_locator=plt.MultipleLocator(.1))
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)


    legend_handles = [ plt.matplotlib.patches.Patch(
            facecolor=c, label=l, edgecolor="black", linewidth=2,
        ) for c, l in zip(colors[:2], legend_labels) ]
    legend = ax.legend(handles=legend_handles, frameon=False,
        bbox_to_anchor=(.05, 1.05), loc="upper left",
        labelspacing=.2)
    legend._legend_box.align = "left"

plt.savefig(export_fname)
plt.close()