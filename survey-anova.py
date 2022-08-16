"""Used to make a variety of simple barplots.
Common script to melt and plot with seaborn for informal stuff.
"""
import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
import pingouin as pg
import seaborn as sns
import utils

plt.rcParams["savefig.dpi"] = 600
# plt.rcParams["interactive"] = True
plt.rcParams["figure.constrained_layout.use"] = True

config = utils.load_config()

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--var", default="SES",
    choices=["SES", "SMS", "attention", "AS"])
args = parser.parse_args()

var = args.var

if var in ["SMS", "attention"]:
    task_id = "bct"
else:
    task_id = "eat"

var_lower = var.lower()
export_name = f"task-{task_id}_intrvX{var_lower}.png"
export_path_plot = os.path.join(config.bids_root, "derivatives", "matplotlib", export_name)
export_path_plot2 = export_path_plot.replace(".png", "_slop.png")
export_path_anova = export_path_plot.replace("matplotlib", "pingouin").replace(".png", "_anova.tsv")
export_path_pwise = export_path_plot.replace("matplotlib", "pingouin").replace(".png", "_pwise.tsv")

df, sidecar = utils.load_all_data()

var_columns = sorted([ c for c in df if c.startswith(f"{var}_") ])
## needs to stay sorted for now

if var in ["SES", "SMS"]:
    ymin, ymax = 1, 5
elif var == "attention":
    ymin, ymax = 0, 100

value_name = f"{var}_score"
var_name = f"{var}_factor"

df_long = df.melt(
    value_vars=var_columns,
    id_vars=["intervention", "participant_id"],
    value_name=value_name, var_name=var_name,
)

anova = pg.mixed_anova(data=df_long, dv=value_name, within=var_name,
    between="intervention", subject="participant_id")

pwise = pg.pairwise_tests(data=df_long, dv=value_name, within=var_name,
    between="intervention", subject="participant_id")


ax = sns.barplot(data=df_long,
    x=var_name, y=value_name, hue="intervention",
    order=var_columns,
    hue_order=["svp", "bct"],
)

anova.to_csv(export_path_anova, sep="\t", index=False)
pwise.to_csv(export_path_pwise, sep="\t", index=False)
plt.savefig(export_path_plot2)
plt.close()


###### better plot


utils.load_matplotlib_settings()


subj_jitter = 0.05    
xlim_edgebuffer = .5
xlim_gapbuffer = .5

intervention_order = ["svp", "bct"]
intrv_palette = utils.load_config(False)["intervention_colors"]
intrv_labels = dict(svp="Attention\ntask", bct="Compassion\nmeditation")
participant_palette = utils.load_participant_palette()
xticklabels = [ intrv_labels[x] for x in intervention_order ]

summary_df = df.groupby("intervention")[var_columns].agg(["mean", "sem"]
    ).stack(0).swaplevel().rename_axis(["variable", "intervention"]
    ).sort_index(ascending=(True, False)).reset_index()


summary_df["color"] = summary_df["intervention"].map(intrv_palette)
summary_df["xloc"] = np.arange(len(summary_df))
summary_df["xloc"] = summary_df["xloc"].add(xlim_gapbuffer * (summary_df["xloc"] // 2))



n_vars = len(var_columns)

figsize = (1.25*n_vars, 3)

bar_kwargs = dict(width=1, edgecolor="black", linewidth=1,
    error_kw=dict(capsize=0, ecolor="black", elinewidth=1))
plot_kwargs = dict(alpha=1, markeredgewidth=.5, markeredgecolor="white",
    linewidth=.5, markersize=4, clip_on=False)

fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

bars = ax.bar("xloc", "mean", yerr="sem", color="color",
    data=summary_df, **bar_kwargs)
bars.errorbar.lines[2][0].set_capstyle("round")

np.random.seed(1)
xvals = summary_df["xloc"].to_numpy()
for _, row in df.iterrows():
    pid = row["participant_id"]
    c = participant_palette[pid]
    yvals = row[var_columns]
    xstart = intervention_order.index(row["intervention"])
    xvals_ = xvals[xstart::2]
    jittered_xvals = xvals_ + np.random.normal(loc=0, scale=subj_jitter)
    ax.plot(jittered_xvals, yvals, "o", color=c, **plot_kwargs)


if var == "attention":
    var_labels = {}
    for c in var_columns:
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
        var_labels[c] = label
elif var == "AS":
    var_labels = { s: s.split("_")[1].capitalize() for s in var_columns }
else:
    var_labels = { s: s.replace("_", "\n") for s in var_columns }

if var == "attention":
    xlabel = "Where was your attention focused during the middle task?"
elif var == "SES":
    xlabel = "State Empathy Scale factor"
elif var == "AS":
    xlabel = "Affective dimension"
elif var == "SMS":
    xlabel = "State Mindfulness Questionnaire factor"


xticks = [ (a+b)/2 for a, b in zip(xvals[::2], xvals[1::2]) ]
xticklabels = [ var_labels[x] for x in var_columns ]
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlabel(xlabel)
ax.set_ylabel(var)

for x, att in zip(xticks, var_columns):
    t, p = pwise.set_index(var_name).loc[att, ["T", "p-unc"]]
    txt_col = "black" if p < .1 else "gainsboro"
    txt = f"t = {t:.1f}\np = {p:.3f}"
    ax.text(x, 1, txt, color=txt_col, ha="center", va="bottom", transform=ax.get_xaxis_transform())


plt.savefig(export_path_plot)
plt.close()