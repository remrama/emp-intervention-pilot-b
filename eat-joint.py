import os
import matplotlib.pyplot as plt
import seaborn as sns
import utils


df, sidecar = utils.load_all_data()

export_path = os.path.join(utils.load_config().bids_root,
    "derivatives", "matplotlib", "task-eat_intrvXattention.png")

g = sns.lmplot(data=df, x="attention_location_2",
    y="actor_correlation-mean_delta",
    hue="intervention",
)

g.axes.flat[0].set_xlabel("Attention to audio prompt")
g.axes.flat[0].set_ylabel(r"Empathic accuracy, $f_{R}$")

plt.tight_layout()

plt.savefig(export_path)
plt.close()