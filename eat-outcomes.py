"""Inspecting the effect of intervention on a few outcomes.
"""
import os
import numpy as np
import pandas as pd
import pingouin as pg

import utils

import matplotlib.pyplot as plt
import seaborn as sns

df, sidecar = utils.load_all_data()

config = utils.load_config()

export_name = "task-eat_intrvXoutcomes.png"
export_path_plot = os.path.join(config.bids_root, "derivatives", "matplotlib", export_name)
# export_path_anova = export_path_plot.replace("matplotlib", "pingouin").replace(".png", "_anova.tsv")
# export_path_pwise = export_path_plot.replace("matplotlib", "pingouin").replace(".png", "_pwise.tsv")

outcome_vars = [
    "actor_correlation-mean_delta",
    "actor_correlation-std_delta",
    "crowd_correlation-mean_delta",
    "crowd_correlation-std_delta",
    "SES_affective",
    "AS_pleasure_1",
]

value_name = "score"
var_name = "metric"
df_long = df.melt(
    value_vars=outcome_vars,
    id_vars=["intervention", "participant_id"],
    value_name=value_name, var_name=var_name,
)

pwise = pg.pairwise_tests(data=df_long, dv=value_name, within=var_name,
    between="intervention", subject="participant_id")

ax = sns.catplot(kind="bar",
    data=df_long,
    x="intervention", y=value_name,
    col=var_name,
    order=["svp", "bct"],
    col_order=outcome_vars,
    sharey=False,
)

# anova.to_csv(export_path_anova, sep="\t", index=False)
# pwise.to_csv(export_path_pwise, sep="\t", index=False)
plt.savefig(export_path_plot)
plt.close()