"""Exploring effects of prior meditation experience.
- Did the two intervention groups have different amounts of meditation experience?
- Did meditation experience predict BCT performance?
- Did meditation experience predict EAT change, separately for conditions?
"""
import os
import numpy as np
import pandas as pd
import pingouin as pg

import utils

import matplotlib.pyplot as plt
import seaborn as sns

utils.load_matplotlib_settings()


root_dir = utils.load_config().bids_root
export_name = "meditation_prior.png"
export_path = os.path.join(root_dir, "derivatives", "matplotlib", export_name)

df, sidecar = utils.load_all_data()

levels = sidecar["Meditation_Prior"]["Levels"]
levels, labels = zip(*levels.items())
levels = [ int(s) for s in levels ]

intrv_palette = utils.load_config(False)["intervention_colors"]
intrv_order = ["svp", "bct"]
intrv_labels = ["Attention\ntask", "Compassion\nmeditation"]

fig, ax = plt.subplots(figsize=(2, 2.5))

# Compare meditation frequency between the two conditions.
a, b = df.groupby("intervention")["Meditation_Prior"].apply(np.array)
stats = pg.mwu(a, b)
u, p = stats.loc["MWU", ["U-val", "p-val"]]
sns.barplot(ax=ax, data=df, y="Meditation_Prior", x="intervention", order=intrv_order, palette=intrv_palette)
sns.swarmplot(ax=ax, data=df, y="Meditation_Prior", x="intervention", order=intrv_order, palette=intrv_palette, linewidth=.5, edgecolor="white")
ax.set_xlabel("Intervention")
ax.set_ylabel("Meditation frequency")
ax.set_xticks(range(len(intrv_labels)))
ax.set_xticklabels(intrv_labels)
ax.set_yticks(levels)
ax.set_yticklabels(labels)
txt = f"U = {u:.1f}\np = {p:.3f}".replace(".0", ".")
txt_color = "black" if p < .1 else "gainsboro"
ax.text(.7, .8, txt, color=txt_color, transform=ax.transAxes, ha="right")

plt.savefig(export_path)
plt.close()