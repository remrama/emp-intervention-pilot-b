"""Plot all raw timecourses.
It's not the most optimal but it's not a big deal.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

import utils

import colorcet as cc
import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


export_fname = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-eat_timecourses.png")

setA_video_ids = utils.load_config(False)["SetA_video_ids"]
setB_video_ids = utils.load_config(False)["SetB_video_ids"]
video_id_list = setA_video_ids + setB_video_ids
participants = utils.load_participant_file()

participant_palette = utils.load_participant_palette()

df = utils.stack_raw_task_data("eat")


SAMPLE_RATE = .5
FIGSIZE = (4, 6)

fig, axes = plt.subplots(nrows=5, ncols=2, figsize=FIGSIZE,
    sharex=True, sharey=True, constrained_layout=True)

for video_id in video_id_list:
    if video_id in setA_video_ids:
        col = 0
        row = setA_video_ids.index(video_id)
    elif video_id in setB_video_ids:
        col = 1
        row = setB_video_ids.index(video_id)
    ax = axes[row, col]
    actor_ratings, crowd_ratings = utils.get_true_timecourses(video_id)
    actor_ratings = stats.zscore(actor_ratings, nan_policy="raise")
    crowd_ratings = stats.zscore(crowd_ratings, nan_policy="raise")
    # plot the actor and crowd nice and bold
    xvals1 = np.arange(0, len(actor_ratings)*SAMPLE_RATE, SAMPLE_RATE)
    xvals2 = np.arange(0, len(crowd_ratings)*SAMPLE_RATE, SAMPLE_RATE)
    ax.plot(xvals1, actor_ratings, label="actor", color="k", alpha=1, lw=1, ls="solid", zorder=3)
    ax.plot(xvals2, crowd_ratings, label="crowd", color="k", alpha=1, lw=1, ls="dashed", zorder=2)
    ax.text(1, 0, video_id, ha="right", va="bottom", transform=ax.transAxes,
        fontsize=6)
    # loop over all the subjects
    for participant_id in participants.index:
        color = participant_palette[participant_id]
        participant_ratings = df.query(f"stimulus=='{video_id}'").loc[participant_id, "response"].tolist()
        participant_ratings = stats.zscore(participant_ratings, nan_policy="raise")
        xvals = np.arange(0, len(participant_ratings)*SAMPLE_RATE, SAMPLE_RATE)
        ax.plot(xvals, participant_ratings, color=color, alpha=.25, lw=1, ls="solid", zorder=1)

    # ax.set_xbound(lower=0)
    class CustomTicker(plt.matplotlib.ticker.LogFormatterSciNotation):
        # https://stackoverflow.com/a/43926354
        def __call__(self, x, pos=None):
            # if x not in [0.1,1,10]:
            if abs(x) > 3:
                return plt.matplotlib.ticker.LogFormatterSciNotation.__call__(self, x, pos=None)
            else:
                return "{x:g}".format(x=x)

    SYMLOG_THRESH = 3
    major_yticks = np.linspace(-SYMLOG_THRESH, SYMLOG_THRESH, SYMLOG_THRESH*2+1)
    major_yticks = np.concatenate([[-10], major_yticks, [10]])
    minor_yticks = np.arange(SYMLOG_THRESH+1, 10)
    minor_yticks = np.append(minor_yticks, 20)
    minor_yticks = np.append(-1*minor_yticks[::-1], minor_yticks)
    # yticks = np.linspace(-10, 10, 21)
    # yticks = np.append(yticks, 20)
    ax.set_ylim(-20, 20)
    ax.set_yscale("symlog", linthresh=SYMLOG_THRESH)
    major_locator = plt.FixedLocator(major_yticks)
    minor_locator = plt.FixedLocator(minor_yticks)
    # major_formatter = plt.ScalarFormatter()
    # major_formatter.set_scientific(True)
    # major_formatter.set_powerlimits((-SYMLOG_THRESH, SYMLOG_THRESH))
    major_formatter = CustomTicker()
    ax.yaxis.set(major_locator=major_locator, minor_locator=minor_locator,
        major_formatter=major_formatter)
    # ax.set_yticks(yticks)
    ax.axhline(-SYMLOG_THRESH, color="black", linewidth=1, linestyle="solid")
    ax.axhline(SYMLOG_THRESH, color="black", linewidth=1, linestyle="solid")
    # ax.grid(visible=True, axis="y", which="major",
    #     linewidth=1, alpha=1, color="gainsboro")
    ax.set_axisbelow(True)
    # major_ticks = plt.matplotlib.ticker.SymmetricalLogLocator(base=10, linthresh=SYMLOG_THRESH)
    # minor_ticks = plt.matplotlib.ticker.SymmetricalLogLocator(base=10, linthresh=SYMLOG_THRESH, subs=np.linspace(.1, .9, 9))
    # ax.yaxis.set(major_locator=major_ticks, minor_locator=minor_ticks)
    # major_formatter=plt.LogFormatter(base=10, labelOnlyBase=True,
    #     linthresh=symlog_lthresh),)

    # xmajor_formatter = "{x} seconds"
    xmajor_formatter = lambda x, pos: "Video\nstart" if x==0 else "{:.0f} min".format(x/60)
    # xmajor_formatter = plt.FuncFormatter(utils.no_leading_zeros)
    ax.xaxis.set(major_locator=plt.MultipleLocator(60),
                 minor_locator=plt.MultipleLocator(10),
                 major_formatter=xmajor_formatter)
    # ax.yaxis.set(major_locator=plt.MultipleLocator(1),
    #              minor_locator=plt.MultipleLocator(.1),
    #              major_formatter=plt.FuncFormatter(utils.no_leading_zeros))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", which="both", top=False, bottom=False)
    if not ax.get_subplotspec().is_last_row():
        ax.spines["bottom"].set_visible(False)
    if ax.get_subplotspec().is_first_col() and ax.get_subplotspec().is_last_row():
        # ax.set_xlabel("Video length")
        ylabel = r"Emotion rating, $z$-scored"
        ylabel += "\n" + r"negative$\leftarrow$   $\rightarrow$positive"
        ax.set_ylabel(ylabel)
        legend = ax.legend(bbox_to_anchor=(1, 1), loc="upper right",
            # title="Rater",
            fontsize=8,
            borderaxespad=0, frameon=False,
            handlelength=1,
            ncol=2,
            columnspacing=1,
            labelspacing=.2,  # vertical space between entries
            handletextpad=.2) # space between legend markers and labels
        # legend._legend_box.align = "left"

plt.savefig(export_fname)
plt.close()