import matplotlib.pyplot as plt
import numpy as np
from read_data import read_data

def plot_hist_Q(dataset_file, detector=1, verbose=False):
    n_of_rpcs = 3
    data = read_data(dataset_file, verbose)

    if isinstance(detector, int) and 1 <= detector <= n_of_rpcs:
        # --- RPC mode ---
        qf_key = f"QF_RPC{detector}"
        qb_key = f"QB_RPC{detector }"

        if qf_key in data and qb_key in data:
            qf_data = np.array(data[qf_key])
            qb_data = np.array(data[qb_key])

            fig, axes = plt.subplots(2, 4, figsize=(16, 8))
            for i in range(4):
                axes[0, i].hist(qf_data[:, i], bins=50, alpha=0.7, color='blue')
                axes[0, i].set_title(f"QF RPC{detector} Strip {i+1}")
                axes[0, i].set_xlabel("Charge")
                axes[0, i].set_ylabel("Count")
                axes[0, i].grid(True)

                axes[1, i].hist(qb_data[:, i], bins=50, alpha=0.7, color='green')
                axes[1, i].set_title(f"QB RPC{detector} Strip {i+1}")
                axes[1, i].set_xlabel("Charge")
                axes[1, i].set_ylabel("Count")
                axes[1, i].grid(True)

            plt.tight_layout()
            plt.show()
        else:
            print(f"Missing data for RPC {detector}: {qf_key} or {qb_key}")

    elif detector == "scint":
        key = "QF_scint"
        if key in data:
            scint_data = np.array(data[key])
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            for i in range(4):
                ax = axes[i // 2, i % 2]
                ax.hist(scint_data[:, i], bins=50, alpha=0.7, color='orange')
                ax.set_title(f"QF scint {i+1}")
                ax.set_xlabel("Charge")
                ax.set_ylabel("Count")
                ax.grid(True)

            plt.tight_layout()
            plt.show()
        else:
            print("Missing data: QF_scint")

    elif detector == "crew":
        key = "QF_crew"
        if key in data:
            crew_data = np.array(data[key])
            fig, axes = plt.subplots(1, 4, figsize=(16, 4))
            for i in range(4):
                axes[i].hist(crew_data[:, i], bins=50, alpha=0.7, color='purple')
                axes[i].set_title(f"QF crew {i+1}")
                axes[i].set_xlabel("Charge")
                axes[i].set_ylabel("Count")
                axes[i].grid(True)

            plt.tight_layout()
            plt.show()
        else:
            print("Missing data: QF_crew")

    else:
        print(f"Invalid detector argument: {detector}. Must be 1–{n_of_rpcs}, 'scint', or 'crew'.")



########################################################
#TEST

# plot_hist_Q("sweap4/sest25184133338.mat", detector=1)
# plot_hist_Q("sweap4/sest25184133338.mat", detector="scint")
# plot_hist_Q("sweap4/sest25184133338.mat", detector="crew")

########################################################
