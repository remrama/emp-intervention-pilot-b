import os
import matplotlib.pyplot as plt
import seaborn as sns
import utils


df, sidecar = utils.load_all_data()

export_path = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-bct_rrate_desc_joint.png")

g = sns.jointplot(kind="reg", data=df, x="rrate-mean", y="rrate-std", height=3, space=.1)

g.ax_joint.set_xlabel(r"Respiration rate, $f_{R}$")
g.ax_joint.set_ylabel(r"Respiration rate variability, $\sigma_{R}$")

plt.tight_layout()

plt.savefig(export_path)
plt.close()