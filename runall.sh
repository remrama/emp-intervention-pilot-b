
set -e # set script to exit if any command fails

# python plot-predictions.py -w sleep
# python plot-predictions.py -w learning

# python source2raw-bct.py
# python source2raw-eat.py
# python source2raw-survey.py

# python eat-descr_correlations.py
# python eat-merge_acqs.py
# python eat-plot_timecourses.py
# python eat-strategy.py
# python eat-joint.py
# python eat-interaction.py
# python eat-outcomes.py

# python bct-descr_respirationrate.py
# python bct-plot_presses.py
# python bct-plot_respirationrate.py
# python bct-plot_respirationrate_joint.py
# python bct-correlations.py
# python bct-attention.py

# python meditation.py
# python dreams.py
python dreamsXempathy.py
python survey-anova.py -v SES
python survey-anova.py -v SMS
python survey-anova.py -v attention
python survey-anova.py -v AS
