import os
import pyreadstat
import pandas as pd
import utils

bids_root = utils.load_config().bids_root
import_filepath = os.path.join(bids_root, "sourcedata", "qualtrics.sav")
export_filepath = os.path.join(bids_root, "phenotype", "debriefing.tsv")
utils.make_pathdir_if_not_exists(export_filepath)


## Start the sidecar with general info but extract the column info from file metadata.
sidecar = {
    "MeasurementToolMetadata": {
        "Description": "Custom debriefing survey",
        "TermURL": "put qualtrics link here or somewhere"
    }
}


# Load all data and metadata.
df, meta = pyreadstat.read_sav(import_filepath)

# Remove development trials
df = df[df["participant_ID"].lt(900)]




###########
########### Make sure default Quatrics stuff looks normal and then remove it.
###########
# assert len(df) == 4, "Only 4 raters should be there."
assert df["Finished"].all(), "Everyone should have finished."
assert df["DistributionChannel"].eq("anonymous").all(), "All responses should come through the anonymous survey link."
assert df["ResponseId"].is_unique, "These should all be unique."
assert df["UserLanguage"].eq("EN").all(), "All languages should be English."
QUALTRICS_COLUMNS = ["IPAddress", "RecipientLastName", "RecipientFirstName",
    "RecipientEmail", "ExternalReference", "ResponseId", "UserLanguage",
    "DistributionChannel", "StartDate", "EndDate", "RecordedDate",
    "Status", "Progress", "Finished", "LocationLatitude", "LocationLongitude",
    "Duration__in_seconds_"]
df = df.drop(columns=QUALTRICS_COLUMNS)

# df["task_condition"] = df["participant_ID"].map(lambda x: "svp" if x%2==0 else "bct")

# meta.variable_value_labels # column-to-int2label mapping
# meta.column_names_to_labels # column2probe mapping

for column_name in df:
    column_info = {}
    if column_name.startswith("AS"):
        column_info["Description"] = "Affective Slider"
        column_info["TermURL"] = "https://www.cognitiveatlas.org/task/id/trm_5586ff878155d"
    elif column_name.startswith("SES"):
        column_info["Description"] = "State Empathy Scale"
    elif column_name.startswith("SMS"):
        column_info["Description"] = "State Mindfulness Scale"
    if column_name in meta.column_names_to_labels:
        column_info["Probe"] = meta.column_names_to_labels[column_name]
    if column_name in meta.variable_value_labels:
        column_info["Levels"] = meta.variable_value_labels[column_name]
    sidecar[column_name] = column_info


# ########### Convert text responses to ordinal variables.
# for column in df:
#     if meta.variable_measure[column] == "scale":
#         df[column] = pd.Categorical(df[column], ordered=True)


# Add 0 to meditation frequency (people that said "no" to any prior exp didn't see this).
# df["Meditation_Freq_1"] = df["Meditation_Freq_1"].fillna(0)
# meditation_columns = [ c for c in df if c.startswith("Meditation") ]
df.loc[df["Meditation_Prior"].eq(1), ["Meditation_Freq_1", "Meditation_Current"]] = 0
df.loc[df["Meditation_Current"].eq(1), ["Meditation_Freq2", "Meditation_Freq3"]] = 0

# Score State Empathy Scale
AFFECTIVE_PROBES = [1, 2, 3, 4]
COGNITIVE_PROBES = [5, 6, 7, 8]
ASSOCIATIVE_PROBES = [9, 10, 11, 12]
affective_columns = [ f"SES_{x}" for x in AFFECTIVE_PROBES ]
cognitive_columns = [ f"SES_{x}" for x in COGNITIVE_PROBES ]
associative_columns = [ f"SES_{x}" for x in ASSOCIATIVE_PROBES ]
df["state_affective_empathy"] = df[affective_columns].sub(1).mean(axis=1, skipna=True)
df["state_cognitive_empathy"] = df[cognitive_columns].sub(1).mean(axis=1, skipna=True)
df["state_associative_empathy"] = df[associative_columns].sub(1).mean(axis=1, skipna=True)

df = df.drop(columns=affective_columns+cognitive_columns+associative_columns)


# Score State Mindfulness Scale
MIND_PROBES = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 15, 16, 17, 19, 20]
BODY_PROBES = [8, 9, 13, 14, 18, 21]
mind_columns = [ f"SMS_{x}" for x in MIND_PROBES ]
body_columns = [ f"SMS_{x}" for x in BODY_PROBES ]
df["state_mind_mindfulness"] = df[mind_columns].mean(axis=1, skipna=True)
df["state_body_mindfulness"] = df[body_columns].mean(axis=1, skipna=True)

df = df.drop(columns=mind_columns+body_columns)

df = df.rename(columns={"participant_ID": "participant_id"})
df["participant_id"] = df["participant_id"].astype(int)
# df["participant_id"] = df["participant_id"].map(lambda x: f"sub-{x:03d}")


df.to_csv(export_filepath, sep="\t", index=False, na_rep="NA", float_format="%.2f")
utils.pretty_sidecar_export(sidecar, export_filepath)