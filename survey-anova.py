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
export_path_anova = export_path_plot.replace("matplotlib", "pingouin").replace(".png", "_anova.tsv")
export_path_pwise = export_path_plot.replace("matplotlib", "pingouin").replace(".png", "_pwise.tsv")

df, sidecar = utils.load_all_data()

var_columns = [ c for c in df if c.startswith(f"{var}_") ]

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
plt.savefig(export_path_plot)
plt.close()