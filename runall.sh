
set -e # set script to exit if any command fails

python plot-predictions.py -w sleep
python plot-predictions.py -w learning

python source2raw-bct.py
python source2raw-eat.py
python source2raw-survey.py

python eat-descr_correlations.py
python eat-merge_acqs.py
python eat-interaction.py
python eat-dreams.py
python eat-plot_timecourses.py

python bct-descr_respirationrate.py
python bct-plot_presses.py
python bct-plot_respirationrate.py
