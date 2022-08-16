"""Correlate dream sharing with empathy measures."""
import os
import matplotlib.pyplot as plt
import numpy as np
import pingouin as pg
import seaborn as sns
import utils

plt.rcParams["savefig.dpi"] = 600
plt.rcParams["interactive"] = True


root_dir = utils.load_config().bids_root
export_name = "dreamsXempathy.png"
export_path_plot = os.path.join(root_dir, "derivatives", "matplotlib", export_name)
export_path_stats = export_path_plot.replace("matplotlib", "pingouin").replace(".png", ".tsv")

df, sidecar = utils.load_all_data()

# df = df.query("intervention=='bct'")

predictor_var = "Dream_Sharing"

outcome_vars = [
    # "DRF",
    "SES_affective", "SES_cognitive", "SES_associative",
    "actor_correlation-mean_pre",
    # "actor_correlation-std_pre",
]


stats = pg.pairwise_corr(df, [[predictor_var], outcome_vars])


var_label = "Empathy metric"
value_label = "Empathy score"

df_long = df.melt(
    value_vars=outcome_vars,
    id_vars=["participant_id", predictor_var],
    var_name=var_label,
    value_name=value_label,
)

labels = {
    "Dream_Sharing": "Dream\nsharing",
    "DRF": "Dream recall",
    "SES_affective": "State Empathy\naffective",
    "SES_cognitive": "State Empathy\ncognitive",
    "SES_associative": "State Empathy\nassociative",
    "actor_correlation-mean_pre": "Empathic task\naccuracy",
    "actor_correlation-std_pre": "Empathic task\nvariability",
}

df_long[var_label] = df_long[var_label].map(labels)

g = sns.lmplot(
    data=df_long,
    x=value_label,
    y=predictor_var,
    col=var_label,
    facet_kws=dict(sharex=False, sharey=True),
    height=2, aspect=.8,
)

g.set_titles(col_template="{col_name}", row_template="{row_name}")
g.set(xlabel="")
g.axes.flat[0].invert_yaxis()

g.tight_layout()

stats.to_csv(export_path_stats, index=False, sep="\t")
plt.savefig(export_path_plot)