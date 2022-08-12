"""correlate EAT and dream empathy/recall
"""
import os
import numpy as np
import pandas as pd

import utils

import matplotlib.pyplot as plt
utils.load_matplotlib_settings()


import_filepath_pre = os.path.join(utils.load_config().bids_root,
    "derivatives", "pandas", "task-eat_acq-pre_agg-sub_corrs.tsv")
import_filepath_survey = os.path.join(utils.load_config().bids_root,
    "phenotype", "debriefing.tsv")

export_filepath = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-eatXdreams.png")


# load data
df_eat = pd.read_csv(import_filepath_pre, sep="\t")

df_survey = pd.read_csv(import_filepath_survey, sep="\t")
df_survey["participant_id"] = df_survey["participant_id"].map(lambda x: f"sub-{x:03d}")

df = df_eat.merge(df_survey, on="participant_id")
# df = df.rename(columns={"actor_correlation-mean": "empathic_accuracy"})

column_names = [
    "actor_correlation-mean",
    # "actor_correlation-std",
    "Meditation_Prior",
    # "Meditation_Freq_1", "Meditation_Current",
    # "Meditation_Freq2", "Meditation_Freq3",
    # "DRF", "LDRF", "NMRF", "NMD",
    # "Dream_Emo_Tone", "Dream_Emo_Intensity",
    "Dream_Sharing", "Dream_Receiving",
    "state_affective_empathy", "state_cognitive_empathy", "state_associative_empathy",
    "state_mind_mindfulness", "state_body_mindfulness",
]

column_names = [ s.replace("_", "\n") for s in column_names ]
df.columns = df.columns.str.replace("_", "\n")

import seaborn as sea
sea.pairplot(df, vars=column_names, height=1, kind="reg")

plt.savefig(export_filepath)