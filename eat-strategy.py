"""Visualize the results of what strategy participants
reported using to perform the Empathic Accuracy Task.

We asked about these wrt while watching the BOTH video sets...
* EAT strategy
    - Actor's emotion while talking                 (0, 1)
    - Actor's emotion while experiencing            (0, 1)
    - Self's emotion while listening                (0, 1)
    - Self's predicted emotion while experiencing   (0, 1)
"""
import os
import matplotlib.pyplot as plt
import utils

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["figure.constrained_layout.use"] = True
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 8
plt.rcParams["axes.titlesize"] = 8
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["axes.linewidth"] = 0.8 # edge line width


export_path = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-eat_strategy.png")

df, sidecar = utils.load_all_data()

strategy_cols = [ c for c in df if c.startswith("empathy_location") ]

table = df.set_index(["intervention", "participant_id"])[strategy_cols].fillna(0).sort_index()

fig, axes = plt.subplots(nrows=2, ncols=1,
    figsize=(2, 4), constrained_layout=True)

probe = "What information did you use\nto rate the speaker's emotions?"

xticklabels = []
for k in strategy_cols:
    selection_text = sidecar[k]["Levels"]["1"]
    if selection_text == "The emotion of the speaker while they were telling the story.":
        label = "Actor's present emotion"
    elif selection_text == "The emotion of the speaker while they were initially experiencing the event.":
        label = "Actor's predicted emotion"
    elif selection_text == "The emotion that you felt while listening to the story.":
        label = "Self's present emotion"
    elif selection_text == "The emotion that you think you would've felt if the story happened to you.":
        label = "Self's predicted emotion"
    xticklabels.append(label)

for intrv, intrv_table in table.groupby("intervention"):
    ax = axes[0] if intrv == "svp" else axes[1]
    ax.imshow(intrv_table, cmap="binary", aspect="auto")
    yticklabels = intrv_table.index.get_level_values("participant_id")
    ax.set_yticks(range(len(yticklabels)))
    ax.set_yticklabels(yticklabels)

    ylabel = "Attention participants" if intrv == "svp" else "Meditation participants"
    ax.set_ylabel(ylabel)

    if ax.get_subplotspec().is_first_row():
        ax.xaxis.set_major_formatter(plt.matplotlib.ticker.NullFormatter())
        ax.tick_params(bottom=False)
    else:
        ax.set_xticks(range(len(xticklabels)))
        ax.set_xticklabels(xticklabels, rotation=33, ha="right")
        ax.set_xlabel(probe, ha="right")


plt.savefig(export_path)
plt.close()