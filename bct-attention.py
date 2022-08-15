"""Visualize relationship between reported location of attention
during the intervention tasks.

We asked about these wrt while performing the intervention task...
* Attention
    - on numbers        (0-100)
    - on audio prompt   (0-100)
    - on mind-wandering (0-100)
    - on breathing      (0-100)
    - on nothing        (0-100)
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pingouin as pg
import utils

plt.rcParams["savefig.dpi"] = 600
# plt.rcParams["interactive"] = True
plt.rcParams["figure.constrained_layout.use"] = True
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 8
plt.rcParams["axes.titlesize"] = 8
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8
plt.rcParams["axes.linewidth"] = 0.8 # edge line width

config = utils.load_config()

export_path = os.path.join(config.bids_root,
    "derivatives", "matplotlib", "task-bct_attention_detailed.png")

df, sidecar = utils.load_all_data()

columns = [ c for c in df if c.startswith("attention_location") ]
column_labels = {}
for c in columns:
    probe = sidecar[c]["Probe"]
    choice = probe.split(" - ", 1)[1]
    if choice == "The numbers involved in the task":
        label = "Task numbers"
    elif choice == "The topics of the audio prompt played before the task":
        label = "Audio prompt"
    elif choice == "Mind-wandering (i.e., things unrelated to the experiment)":
        label = "Mind-wandering"
    elif choice == "Your breathing":
        label = "Breathing"
    elif choice == "Nothing":
        label = "Nothing"
    column_labels[c] = label

n_vars = len(columns)
figsize = (.9*n_vars, .9*n_vars)
fig, axes = plt.subplots(nrows=n_vars, ncols=n_vars,
    figsize=figsize, sharex="col", sharey=False)

def get_bins(var):
    if var.startswith("attention_location"):
        return np.arange(0, 101, 10)
    else:
        levels = [ int(k) for k in sidecar[var]["Levels"] ]
        low_lim = min(levels) - .5
        high_lim = max(levels) + .5
        return np.linspace(low_lim, high_lim, len(levels)+1)

hist1d_kwargs = dict(alpha=.3, edgecolor="black", linewidth=0, clip_on=False)
hist2d_kwargs = dict(clip_on=False)

for c in range(n_vars):
    xvar = columns[c]
    xbins = get_bins(xvar)

    for r in range(n_vars):
        yvar = columns[r]
        ybins = get_bins(yvar)

        ax = axes[r, c]
        ax.set_aspect("auto")

        if c == r:
            svp_vals = df.query("intervention=='svp'")[xvar].values
            bct_vals = df.query("intervention=='bct'")[xvar].values
            ax.hist(svp_vals, bins=xbins, color="Red", **hist1d_kwargs)
            ax.hist(bct_vals, bins=xbins, color="Blue", **hist1d_kwargs)
        elif c < r:
            xvals = df.query("intervention=='svp'")[xvar].values
            yvals = df.query("intervention=='svp'")[yvar].values
        else:
            xvals = df.query("intervention=='bct'")[xvar].values
            yvals = df.query("intervention=='bct'")[yvar].values

        if r == c:
            stats = pg.mwu(svp_vals, bct_vals)
            sval, p = stats.loc["MWU", ["U-val", "p-val"]]
        else:
            stats = pg.corr(xvals, yvals, method="kendall")
            sval, p = stats.loc["kendall", ["r", "p-val"]]
            cmap = "Reds" if c < r else "Blues"
            ax.hist2d(xvals, yvals, bins=(xbins, ybins), cmap=cmap, **hist2d_kwargs)
            ax.set_ylim(ybins.min(), ybins.max())
            if yvar.endswith("_recall"):
                ax.invert_yaxis()
            if ax.get_subplotspec().is_first_col():
                ax.set_ylabel(column_labels[yvar])

        ax.set_xlim(xbins.min(), xbins.max())
        if xvar.endswith("_recall"):
            ax.invert_xaxis()
        if ax.get_subplotspec().is_last_row():
            ax.set_xlabel(column_labels[xvar])
            minor_dist = np.diff(xbins)[0] # should all be the same
            x_minorlocator = plt.matplotlib.ticker.MultipleLocator(minor_dist)
            x_majorlocator = plt.matplotlib.ticker.FixedLocator(
                [xbins.min(), xbins.max()])
            ax.xaxis.set_minor_locator(x_minorlocator)
            ax.xaxis.set_major_locator(x_majorlocator)

        if r == c:
            ax.spines[["left", "top", "right"]].set_visible(False)
        if ax.get_subplotspec().is_first_row() or not ax.get_subplotspec().is_first_col():
            ax.yaxis.set_major_formatter(plt.matplotlib.ticker.NullFormatter())
            ax.tick_params(left=False)
        else:
            minor_dist = np.diff(ybins)[0] # should all be the same
            y_minorlocator = plt.matplotlib.ticker.MultipleLocator(minor_dist)
            y_majorlocator = plt.matplotlib.ticker.FixedLocator(
                [ybins.min(), ybins.max()])
            ax.yaxis.set_minor_locator(y_minorlocator)
            ax.yaxis.set_major_locator(y_majorlocator)

        if r == c:
            text = f"U = {sval:.0f}\np = {p:.3f}".replace("0.", ".")
        else:
            text = f"r = {sval:.2f}\np = {p:.3f}".replace("0.", ".")
        color = "black" if p < .1 else "gainsboro"
        ax.text(.95, .05, text, color=color,
            va="bottom", ha="right", transform=ax.transAxes)

fig.align_labels()

plt.savefig(export_path)
plt.close()