# PEACE empathy study - behavioral pilot

This repo has display and analysis code for a behavioral pilot (in-lab) study. We were testing if a brief mindfulness intervention could increase empathy. The data, documents, stimuli, and a code backup are [on OSF](https://osf.io/upa7t/).


## Display scripts

* `config.json` - configuration file for global variables
* `psychopy.yml` - conda environment file for display/psychopy
* `game.py` - base class for task displays
* `eat.py` - Empathic Accuracy Task display class
* `bct.py` - Breath Counting Task display class
* `svp.py` - Serial Visual Presentation Task display class
* `runall.py` - runs all task in sequence for a single participant


## Analysis

* `config.json` - configuration file for global variables
* `utils.py` - file with python functions useful in multiple scripts
* `runall.sh` - run all analyses in sequence


### Converting source data to raw (minimally processed)

```bash
# Visualize predictions.
python plot-predictions.py -w sleep     # => matplotlib/task-eat_prediction-sleep.png
python plot-predictions.py -w learning  # => matplotlib/task-eat_prediction-learning.png
```
```bash
python source2raw-bct.py
python source2raw-eat.py
# Exports BIDS-formatted behavioral files for each participant:
# sub-001/beh/
#   |---------- sub-001_task-bct_beh.json
#   |---------- sub-001_task-bct_beh.tsv
#   |---------- sub-001_task-eat_acq-post_beh.json
#   |---------- sub-001_task-eat_acq-post_beh.tsv
#   |---------- sub-001_task-eat_acq-pre_beh.json
#   |---------- sub-001_task-eat_acq-pre_beh.tsv

# The Qualtrics data goes into one file.
python source2raw-survey.py         # => phenotype/debriefing.tsv
```

### Empathic Accuracy Task analyses

```bash
# Get descriptives for empathic accuracy (correlations).
python eat-descr_correlations.py    # => pandas/task-eat_acq-pre_agg-sub_corrs.tsv
                                    # => pandas/task-eat_acq-pre_agg-sub_corrs_descr.tsv
                                    # => pandas/task-eat_acq-post_agg-sub_corrs.tsv
                                    # => pandas/task-eat_acq-post_agg-sub_corrs_descr.tsv

# Merge the pre and post empathy task data into one file.
python eat-merge_acqs.py            # => pandas/task-eat_agg-sub_corrs.tsv

# Analyze/visualize the interaction between acquisition (pre, post) and intervention (svp/bct).
python eat-interaction.py -s actor -m mean  # => pingouin/task-eat_acqXint_anova.tsv
                                            # => pingouin/task-eat_acqXint_pwise.tsv
                                            # => matplotlib/task-eat_acqXint_metric-mean_source-actor.png
python eat-interaction.py -s actor -m std
python eat-interaction.py -s crowd -m mean
python eat-interaction.py -s crowd -m std

# Visualize lots of correlations between empathy and dreams.
python eat-dreams.py                # => matplotlib/task-eatXdreams.png

# Visualize the raw empathy accuracy task timecourses.
python eat-plot_timecourses.py      # => matplotlib/task-eat_timecourses.png

# Visualize the reported empathic accuracy strategy of each participant.
python eat-strategy.py              # => matplotlib/task-eat_strategy.png
```

### Breath Counting Task analyses

```bash
# Get descriptives for breath counting task accuracy.
python bct-descr_respirationrate.py # => pandas/task-bct_acq-pre_agg-sub_rrate_descr.tsv
                                    # => pandas/task-bct_acq-post_agg-sub_rrate_descr.tsv
                                    # => pandas/task-bct_agg-sub_rrate.tsv
                                    # => pandas/task-bct_agg-sub_rrate_descr.tsv

# Visualize the presses over time as presses and respiration rate.
python bct-plot_presses.py          # => matplotlib/task-bct_presses.png
python bct-plot_respirationrate.py  # => matplotlib/task-bct_rrate.png
                                    # => pandas/task-bct_rrate.tsv
```