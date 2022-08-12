"""Plot the aggregate correlation results and run stats.
"""
import os
import numpy as np
import pandas as pd
import pingouin as pg

import utils

import matplotlib.pyplot as plt

utils.load_matplotlib_settings()


import_filepath = os.path.join(utils.load_config().bids_root,
    "derivatives", "pandas", "task-eat_acq-pre_agg-sub_corrs.tsv")

export_filepath_plot = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-eat_acqXint.png")
export_filepath_anova = export_filepath_plot.replace("matplotlib", "pingouin").replace(".png", "_anova.tsv")
export_filepath_pwise = export_filepath_plot.replace("matplotlib", "pingouin").replace(".png", "_pwise.tsv")

utils.make_pathdir_if_not_exists(export_filepath_plot)
utils.make_pathdir_if_not_exists(export_filepath_anova)

# load data
df_pre = pd.read_csv(import_filepath, sep="\t")
df_post = pd.read_csv(import_filepath.replace("-pre", "-post"), sep="\t")
df_pre["acquisition_id"] = "pre"
df_post["acquisition_id"] = "post"
df = pd.concat([df_pre, df_post], ignore_index=True)
# anova_stats = pd.read_csv(import_fname2)
# pairwise_stats = pd.read_csv(import_fname3)

df["intervention"] = df["participant_id"].apply(lambda x: "svp" if int(x.split("-")[1])%2 == 0 else "bct")

df = df.rename(columns={"actor_correlation-mean": "empathic_accuracy"})



################ run stats

anova_stats = pg.mixed_anova(data=df,
    dv="empathic_accuracy",
    between="intervention",
    within="acquisition_id",
    subject="participant_id",
    effsize="np2", correction="auto")

pwise_stats = pg.pairwise_tests(data=df,
    dv="empathic_accuracy",
    within="acquisition_id",
    between="intervention",
    subject="participant_id",
    effsize="hedges", correction="auto",
    parametric=False, marginal=True, padjust="none",
    return_desc=False, interaction=True, within_first=False)

anova_stats.to_csv(export_filepath_anova, sep="\t", index=False, na_rep="NA", float_format="%.5f")
pwise_stats.to_csv(export_filepath_pwise, sep="\t", index=False, na_rep="NA", float_format="%.5f")



###################### Plot


FIGSIZE = (2.5, 3.5)
BAR_KWARGS = dict(width=1, edgecolor="black", linewidth=1,
    error_kw=dict(capsize=0, ecolor="black", elinewidth=1))
PLOT_KWARGS = dict(alpha=1, markeredgewidth=.5, markeredgecolor="white",
    linewidth=.5, markersize=4)

SUBJ_JITTER = 0.05    
XLIM_EDGEBUFFER = .5
XLIM_GAPBUFFER = .5
xvals = np.array([0., 1, 2, 3])
xvals[2:] += XLIM_GAPBUFFER

INTERVENTION_ORDER = ["svp", "bct"]
ACQUISITION_ORDER = ["pre", "post"]
COLORS = dict(pre="white", post="gainsboro")
INTERVENTION_LABELS = dict(svp="Attention\ntask", bct="Compassion\nmeditation")
participant_palette = utils.load_participant_palette()
xticklabels = [ INTERVENTION_LABELS[x] for x in INTERVENTION_ORDER ]
# xticklabels = [ x.upper() + "\nintervention" for x in TASK_ORDER ]

ordered_indx = pd.MultiIndex.from_product([INTERVENTION_ORDER, ACQUISITION_ORDER],
    names=["intervention", "acquisition_id"])

summary_df = df.groupby(["intervention", "acquisition_id"]
    )["empathic_accuracy"].agg(["mean", "sem"]
    ).reindex(index=ordered_indx)

summary_df["color"] = summary_df.index.map(lambda x: COLORS[x[1]])
summary_df["xloc"] = xvals


# draw
fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

bars = ax.bar("xloc", "mean", yerr="sem", color="color",
    data=summary_df, **BAR_KWARGS)
bars.errorbar.lines[2][0].set_capstyle("round")

np.random.seed(1)
for p, p_df in df.groupby("participant_id"):
    c = participant_palette[p]
    data = p_df.set_index(["intervention", "acquisition_id"]
        ).reindex(index=ordered_indx
        )["empathic_accuracy"].values
    jittered_xvals = xvals + np.random.normal(loc=0, scale=SUBJ_JITTER)
    ax.plot(jittered_xvals, data, "-o", color=c, **PLOT_KWARGS)

ax.axhline(0, linewidth=1, linestyle="solid", color="black")
ax.set_xticks([xvals[:2].mean(), xvals[2:].mean()])
ax.set_xticklabels(xticklabels)
ylabel = r"Empathic accuracy, $r_{E}$"
#ylabel += "\n" + r"$\rightarrow$ perfect agreement"
ax.set_ylabel(ylabel)
ax.set_xlabel("Intervention")
ax.tick_params(bottom=False, top=False, right=False, which="both", axis="both")
xmin = xvals[0] - BAR_KWARGS["width"]/2 - XLIM_EDGEBUFFER
xmax = xvals[-1] + BAR_KWARGS["width"]/2 + XLIM_EDGEBUFFER
ax.set_xlim(xmin, xmax)
ax.set_ylim(-.2, 2)
ax.yaxis.set(major_locator=plt.MultipleLocator(.5),
    minor_locator=plt.MultipleLocator(.1))
# ax.spines["top"].set_visible(False)
# ax.spines["right"].set_visible(False)
ax.grid(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)


# legend
LEGEND_LABELS = dict(pre="Pre", post="Post")
legend_handles = [ plt.matplotlib.patches.Patch(
        edgecolor="black", linewidth=.5, facecolor=c,
        label=LEGEND_LABELS[l]+"-intervention"
    ) for l, c in COLORS.items() ]
legend = ax.legend(handles=legend_handles,
    # title="Intervention task",
    bbox_to_anchor=(.05, 1.05), loc="upper left")
legend._legend_box.align = "left"


# significance text
sigcolor = lambda p: "black" if p < .1 else "gainsboro"
for test in ["Interaction", "bct", "svp"]:
    ytxt = .84 # in axis coordinates
    TEXT_VBUFF = .01
    if test == "Interaction":
        pval = anova_stats.set_index("Source").loc[test, "p-unc"]
        xtxt = xvals[1:3].mean()
        ax.scatter([xtxt], [ytxt], s=15, marker="x",
            transform=ax.get_xaxis_transform(),
            color=sigcolor(pval), linewidth=.5)
        ax.scatter([xtxt], [ytxt], s=30, marker="o",
            transform=ax.get_xaxis_transform(),
            facecolor="none", edgecolor=sigcolor(pval), linewidth=.5)
    else:
        pval = pwise_stats.set_index("intervention").loc[test, "p-unc"]
        xindx = INTERVENTION_ORDER.index(test)
        xmin, xmax = xvals[2*xindx:2*xindx+2]
        xtxt = xvals[2*xindx:2*xindx+2].mean()
        ax.hlines(y=ytxt, xmin=xmin, xmax=xmax,
            linewidth=1, color=sigcolor(pval), capstyle="round",
            transform=ax.get_xaxis_transform())
    # sigchars = "*" * sum([ pval<cutoff for cutoff in [.05, .01, .001] ])
    ptxt = r"p<0.001" if pval < .001 else fr"$p={pval:.2f}$"
    ptxt = ptxt.replace("0", "", 1)
    ax.text(xtxt, ytxt+TEXT_VBUFF, ptxt, color=sigcolor(pval),
        transform=ax.get_xaxis_transform(), ha="center", va="bottom")


utils.save_matplotlib(export_filepath_plot)