"""Exploring effects of prior meditation experience.
"""
import os
import numpy as np
import pandas as pd

import utils

import matplotlib.pyplot as plt
import seaborn as sns

root_dir = utils.load_config().bids_root
export_name = "meditation_prior.png"
export_path = os.path.join(root_dir, "derivatives", "matplotlib", export_name)

df, sidecar = utils.load_all_data()

levels = sidecar["Meditation_Prior"]["Levels"]

ymin = min(map(int, levels))
ymax = max(map(int, levels))

fig, axes = plt.subplots(ncols=3, figsize=(8, 3))

sns.barplot(ax=axes[0], data=df, x="intervention", y="Meditation_Prior", order=["svp", "bct"])
sns.regplot(ax=axes[1], data=df, x="Meditation_Prior", y="actor_correlation-mean_pre")
sns.regplot(ax=axes[2], data=df, x="Meditation_Prior", y="cycle_correct")

plt.savefig(export_path)
plt.close()