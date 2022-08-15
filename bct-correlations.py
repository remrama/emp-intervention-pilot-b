import os
import matplotlib.pyplot as plt
import numpy as np
import pingouin as pg
import utils

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True
plt.rcParams["figure.constrained_layout.use"] = True
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = "Times New Roman"
plt.rcParams["mathtext.cal"] = "Times New Roman"
plt.rcParams["mathtext.it"] = "Times New Roman:italic"
plt.rcParams["mathtext.bf"] = "Times New Roman:bold"
plt.rcParams["font.size"] = 8
plt.rcParams["axes.titlesize"] = 8
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["axes.linewidth"] = 0.8 # edge line width


root_dir = utils.load_config().bids_root
export_name = "task-bct_correlations.png"
export_path = os.path.join(root_dir, "derivatives", "matplotlib", export_name)

df, sidecar = utils.load_all_data()

columns = [
    "cycle_correct",
    # "cycle_response_time-mean",
    # "cycle_response_time-std",
    "rrate-mean",
    "rrate-std",
    "actor_correlation-mean_pre",
    "actor_correlation-mean_delta",
    "actor_correlation-std_delta",
    "attention_location_2",
    # "SMS_mind",
    # "SES_affective",
    # "AS_arousal_1",
    # "AS_pleasure_1",
]

column_labels = {
    "cycle_correct": "BCT %",
    "rrate-mean": r"$\bar{f_{R}}$",
    "rrate-std": r"$\sigma_{\bar{f_{R}}}$",
    "actor_correlation-mean_pre": r"Empathy $r_{pre}$",
    "actor_correlation-mean_delta": r"$r_{post}-r_{pre}$",
    "actor_correlation-std_delta": r"$\sigma_{\bar{r_{post}}}-\sigma_{\bar{r_{pre}}}$",
    "attention_location_2": "Audio\nfocus",
}

n_vars = len(columns)
figsize = (.8*n_vars, .8*n_vars)

fig, axes = plt.subplots(nrows=n_vars, ncols=n_vars,
    figsize=figsize, sharex=False, sharey=False)

scatter_kwargs = dict(s=30, alpha=.75, linewidth=.5, edgecolor="white", clip_on=False)
hist_kwargs = dict(density=True, histtype="stepfilled", color="white",
    clip_on=False, edgecolor="black", linewidth=1)
rug_kwargs = dict(ymax=.1, alpha=.75, linewidth=2)

palette = utils.load_participant_palette()
df["color"] = df["participant_id"].map(palette)

for r in range(n_vars):
    for c in range(n_vars):
        ax = axes[r, c]
        ax.set_box_aspect(1)
        xvar = columns[c]
        yvar = columns[r]

        if r == c:
            data = df[xvar].values
            n, bins, patches = ax.hist(data, **hist_kwargs)
        
        elif r < c:
            ax.axis("off")
        elif r > c:
            ax.scatter(xvar, yvar, data=df, color="color", **scatter_kwargs)
            
        if r > c:
            a, b = df[[xvar, yvar]].dropna().values.T
            stats = pg.corr(a, b, method="spearman")
            rval, pval = stats.loc["spearman", ["r", "p-val"]]
            r_txt = fr"$r={rval:.2f}$".replace("0.", ".")
            sigchars = "*" * sum([ pval < x for x in (.05, .01, .001) ])
            r_txt = sigchars + r_txt
            txt_color = "black" if pval < .1 else "gainsboro"
            ax.text(.95, .05, r_txt, color=txt_color,
                transform=ax.transAxes, ha="right", va="bottom")

        if ax.get_subplotspec().is_first_col() and not ax.get_subplotspec().is_first_row():
            ax.set_ylabel(column_labels[yvar], labelpad=1)
        if ax.get_subplotspec().is_last_row() and not ax.get_subplotspec().is_last_col():
            ax.set_xlabel(column_labels[xvar], labelpad=1)
        
        if r == c:
            ax.tick_params(left=False, top=False, right=False, bottom=False, labelleft=False, labelbottom=False)
        else:
            ax.tick_params(left=False, top=False, right=False, bottom=False, labelleft=False, labelbottom=False)
            if ax.get_subplotspec().is_first_col():
                ax.tick_params(left=True, labelleft=True)
            if ax.get_subplotspec().is_last_row():
                ax.tick_params(bottom=True, labelbottom=True)

fig.align_labels()

plt.savefig(export_path)