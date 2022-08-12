"""========================================================
plot a "map" of all presses/accuracy/rt/responses
for each participant individually

- each participant gets their own "row"
- each press response (space/down/right) gets its own shape
    - also size is impacted, spaces and rights are bigger bc they end "cycles"
- each press accuracy (correct/miscount/reset) gets its own color

Draw a big descriptive plot
showing *every press* from every participant.
and another descriptive plot showing timecourse (for troubleshooting mostly)
"""
import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import utils

utils.load_matplotlib_settings()
participant_palette = utils.load_participant_palette()



export_filepath = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-bct_presses.png")
utils.make_pathdir_if_not_exists(export_filepath)

df = utils.stack_raw_task_data("bct")

df["rt_cumsum"] = df.groupby("participant_id")["response_time"].transform("cumsum")

############ Data wrangling.
# # flip to a dataframe with RTs in columns and press count as index.
# # we need, for each participant and press,
# # the RT, the response, and the press accuracy
# table = df.pivot(
#     columns="participant_id",
#     index="pc",
#     values=["rt", "press_correct", "response"],
#     # values=["rt_sum","press_correct"],
#     ).sort_index(axis="index").sort_index(axis="columns")


# # Convert RTs to seconds and cumulative sum them.
# table["rt"] = table["rt"].div(1000).cumsum()

df["press_accuracy"] = df["press_accuracy"].replace({
        "overshoot": "incorrect",
        "undershoot": "incorrect",
        "selfcaught": "reset",
    })
df["press_correct"] = df["press_accuracy"].eq("correct")



RESPONSE_MARKERS = dict(left="v", right="o", space="s")
RESPONSE_SIZES = dict(left=2, right=30, space=10)
ACC_PALETTE = dict(correct="forestgreen", incorrect="indianred", space="gray")

EXP_LENGTH = 10 # minutes, for xmax

SCATTER_KWARGS = dict(alpha=.7, linewidths=0, clip_on=False)
BARH_KWARGS = dict(color="white", clip_on=False, edgecolor="black", linewidth=1, height=.8)
GRIDSPEC_KWARGS = dict(top=.7, bottom=.25, left=.1, right=.9,
    width_ratios=[10, 1], wspace=.1)

n_participants = df.index.nunique()
figsize = (6.5, .5*n_participants)

fig, (ax, axright) = plt.subplots(ncols=2, figsize=figsize,
    gridspec_kw=GRIDSPEC_KWARGS, sharey=True,
    constrained_layout=False)

for i, (_, subj_df) in enumerate(df.groupby("participant_id")):
    for (resp, correct), _subj_df in subj_df.groupby(["response", "press_correct"]):
        if resp == "space":
            color = ACC_PALETTE[resp]
        else:
            color = ACC_PALETTE["correct"] if correct else ACC_PALETTE["incorrect"]
        xvals = _subj_df["rt_cumsum"].values
        yvals = np.repeat(i, xvals.size)
        ax.scatter(xvals, yvals, c=color,
            s=RESPONSE_SIZES[resp], marker=RESPONSE_MARKERS[resp],
            **SCATTER_KWARGS)
    # second axis correct frequencies
    subj_accuracy = subj_df.groupby("cycle")["press_correct"].last().mean()
    axright.barh(i, subj_accuracy, **BARH_KWARGS)

ax.set_xlim(0, EXP_LENGTH*60*1000)
msec2min = lambda x, pos: int(x/1000/60)
ax.xaxis.set(major_locator=plt.MaxNLocator(10), # 10 minutes
    major_formatter=msec2min)
# ax.yaxis.set(major_locator=plt.MultipleLocator(1))
ax.set_yticks(range(n_participants))
ax.set_yticklabels(df.index.unique())
ax.set_xlabel("Time during Breath Counting Task\n(minutes)")
ax.set_ylabel("Participant ID")
ax.set_ylim(-.5, n_participants-.5)
ax.invert_yaxis()
ax.grid(False)
for spine in ax.spines.values():
    spine.set_position(("outward", 5))

axright.grid(False)
axright.tick_params(which="both", top=False, left=False, right=False)
axright.set_xlabel("Accuracy")
axright.set_xlim(0, 1)
axright.xaxis.set(major_locator=plt.MultipleLocator(1),
    minor_locator=plt.MultipleLocator(.5),
    major_formatter=plt.matplotlib.ticker.PercentFormatter(xmax=1))
for side, spine in axright.spines.items():
    if side in ["top", "right"]:
        spine.set_visible(False)
    elif side == "bottom":
        spine.set_position(("outward", 5))



## need 2 legends, one for the button press type and one for accuracy
button_legend_elements = [ plt.matplotlib.lines.Line2D([0], [0],
        label=x, marker=m, markersize=6, color="white",
        markerfacecolor="white", markeredgecolor="black")
    for x, m in RESPONSE_MARKERS.items() ]
legend1 = ax.legend(handles=button_legend_elements,
    loc="lower left", bbox_to_anchor=(0, 1),
    title="button press", ncol=3)

accuracy_legend_elements = [ plt.matplotlib.patches.Patch(
        label="reset" if x=="space" else x,
        facecolor=c, edgecolor="white")
    for x, c in ACC_PALETTE.items() ]
legend2 = ax.legend(handles=accuracy_legend_elements,
    loc="lower right", bbox_to_anchor=(1, 1),
    title="accuracy", ncol=3)

ax.add_artist(legend1)
ax.add_artist(legend2)


fig.align_xlabels()

utils.save_matplotlib(export_filepath)