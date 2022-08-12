import os
import argparse
import numpy as np
import pandas as pd
from scipy import stats

import utils

import colorcet as cc
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


parser = argparse.ArgumentParser()
parser.add_argument("--show", action="store_true", help="Play don't save")
args = parser.parse_args()


export_fname = os.path.join(utils.load_config().bids_root, "derivatives",
    "matplotlib", "task-eat_animation_demo.gif")


participant_list = utils.load_participant_file().index.tolist()
participant_palette = utils.load_participant_palette()

df = utils.stack_raw_task_data("eat")


SAMPLE_RATE = .5
FIGSIZE = (4, 3)
VIDEO_ID = "ID113_vid3"

actor_ratings, crowd_ratings = utils.get_true_timecourses(VIDEO_ID)
actor_ratings = stats.zscore(actor_ratings, nan_policy="raise")
crowd_ratings = stats.zscore(crowd_ratings, nan_policy="raise")
xvals = np.arange(0, len(actor_ratings)*SAMPLE_RATE, SAMPLE_RATE)
frames = range(0, len(xvals))
p1_ratings = df.query(f"stimulus=='{VIDEO_ID}'").loc["sub-001", "response"].tolist()
p2_ratings = df.query(f"stimulus=='{VIDEO_ID}'").loc["sub-002", "response"].tolist()
p3_ratings = df.query(f"stimulus=='{VIDEO_ID}'").loc["sub-003", "response"].tolist()
p4_ratings = df.query(f"stimulus=='{VIDEO_ID}'").loc["sub-004", "response"].tolist()

fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

# xmajor_formatter = lambda x, pos: "Video\nstart" if x==0 else "{:.0f} min".format(x/60)
# ax.xaxis.set(major_locator=plt.MultipleLocator(60),
#              minor_locator=plt.MultipleLocator(10),
#              major_formatter=xmajor_formatter)
ax.set_xticks([0])
ax.set_xticklabels(["Video\nstart"])
ax.yaxis.set(major_locator=plt.MultipleLocator(1),
             minor_locator=plt.MultipleLocator(.2))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.grid(visible=True, axis="y", which="major",
    linewidth=1, alpha=1, color="gainsboro")
ax.grid(visible=True, axis="y", which="minor",
    linewidth=.3, alpha=1, color="gainsboro")
ax.set_axisbelow(True)
ax.tick_params(axis="both", which="both", top=False, bottom=False)
ylabel = r"Emotion rating, $z$-scored"
ylabel += "\n" + r"negative$\leftarrow$   $\rightarrow$positive"
ax.set_ylabel(ylabel)
ax.axhline(0, color="black", linewidth=1, linestyle="solid")

PLOT_KWARGS = dict(alpha=1, lw=2, zorder=3)
actor_xdata, actor_ydata = [], []
crowd_xdata, crowd_ydata = [], []
p1_xdata, p1_ydata = [], []
p2_xdata, p2_ydata = [], []
p3_xdata, p3_ydata = [], []
p4_xdata, p4_ydata = [], []
actor_line, = plt.plot([], [], color="k", ls="solid", **PLOT_KWARGS)
crowd_line, = plt.plot([], [], color="k", ls="dashed", **PLOT_KWARGS)
p1_line, = plt.plot([], [], color=participant_palette["sub-001"], ls="dashed", **PLOT_KWARGS)
p2_line, = plt.plot([], [], color=participant_palette["sub-002"], ls="dashed", **PLOT_KWARGS)
p3_line, = plt.plot([], [], color=participant_palette["sub-003"], ls="dashed", **PLOT_KWARGS)
p4_line, = plt.plot([], [], color=participant_palette["sub-004"], ls="dashed", **PLOT_KWARGS)


def init():
    ax.set_xlim(xvals[0], xvals[-1])
    ax.set_ylim(-3, 3)
    return actor_line, crowd_line, p1_line, p2_line, p3_line, p4_line

def update(i):
    actor_xdata.append(xvals[i])
    crowd_xdata.append(xvals[i])
    p1_xdata.append(xvals[i])
    p2_xdata.append(xvals[i])
    p3_xdata.append(xvals[i])
    p4_xdata.append(xvals[i])
    actor_ydata.append(actor_ratings[i])
    crowd_ydata.append(crowd_ratings[i])
    p1_ydata.append(p1_ratings[i])
    p2_ydata.append(p2_ratings[i])
    p3_ydata.append(p3_ratings[i])
    p4_ydata.append(p4_ratings[i])
    actor_line.set_data(actor_xdata, actor_ydata)
    if i > 20:
        crowd_line.set_data(crowd_xdata, crowd_ydata)
    # if i > 40:
    #     p1_line.set_data(p1_xdata, p1_ydata)
    #     p2_line.set_data(p2_xdata, p2_ydata)
    #     p3_line.set_data(p3_xdata, p3_ydata)
    #     p4_line.set_data(p4_xdata, p4_ydata)

    return actor_line, crowd_line, p1_line, p2_line, p3_line, p4_line

ani = FuncAnimation(fig, update,
    frames=frames,
    init_func=init, blit=True)

if args.show:
    plt.show()
else:
    ani.save(export_fname, writer=PillowWriter(fps=int(1/SAMPLE_RATE)))
