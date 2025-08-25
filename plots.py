import matplotlib.pyplot as plt
import numpy as np
from load_lookUpTable import load_general_config  

def plot_hist_Q(data, detector=1, verbose=False):
    general_config = load_general_config("lookUpTable_general.txt")
    n_of_rpcs = general_config["general"]["n_of_rpcs"]

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
def plot_hist_T(data, detector=1, verbose=False):
    general_config = load_general_config("lookUpTable_general.txt")
    n_of_rpcs = general_config["general"]["n_of_rpcs"]

    if isinstance(detector, int) and 1 <= detector <= n_of_rpcs:
        # --- RPC mode ---
        tf_key = f"TF_RPC{detector}"
        tb_key = f"TB_RPC{detector}"

        if tf_key in data and tb_key in data:
            tf_data = np.array(data[tf_key])
            tb_data = np.array(data[tb_key])

            fig, axes = plt.subplots(2, 4, figsize=(16, 8))
            for i in range(4):
                axes[0, i].hist(tf_data[:, i], bins=50, alpha=0.7, color='red')
                axes[0, i].set_title(f"TF RPC{detector} Strip {i+1}")
                axes[0, i].set_xlabel("Time")
                axes[0, i].set_ylabel("Count")
                axes[0, i].grid(True)

                axes[1, i].hist(tb_data[:, i], bins=50, alpha=0.7, color='brown')
                axes[1, i].set_title(f"TB RPC{detector} Strip {i+1}")
                axes[1, i].set_xlabel("Time")
                axes[1, i].set_ylabel("Count")
                axes[1, i].grid(True)

            plt.tight_layout()
            plt.show()
        else:
            print(f"Missing data for RPC {detector}: {tf_key} or {tb_key}")

    elif detector == "scint":
        key = "TF_scint"
        if key in data:
            scint_data = np.array(data[key])
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            for i in range(4):
                ax = axes[i // 2, i % 2]
                ax.hist(scint_data[:, i], bins=50, alpha=0.7, color='coral')
                ax.set_title(f"TF scint {i+1}")
                ax.set_xlabel("Time")
                ax.set_ylabel("Count")
                ax.grid(True)

            plt.tight_layout()
            plt.show()
        else:
            print("Missing data: TF_scint")

    elif detector == "crew":
        key = "TF_crew"
        if key in data:
            crew_data = np.array(data[key])
            fig, axes = plt.subplots(1, 4, figsize=(16, 4))
            for i in range(4):
                axes[i].hist(crew_data[:, i], bins=50, alpha=0.7, color='orchid')
                axes[i].set_title(f"TF crew {i+1}")
                axes[i].set_xlabel("Time")
                axes[i].set_ylabel("Count")
                axes[i].grid(True)

            plt.tight_layout()
            plt.show()
        else:
            print("Missing data: TF_crew")

    else:
        print(f"Invalid detector argument: {detector}. Must be 1–{n_of_rpcs}, 'scint', or 'crew'.")


########################################################

def plot_diffT(data: dict):
    #maybe TO DO small scintilators 3 and 4, other detectors? 
    """
    Plots histogram of T_S1 - T_S2 time differences from scintillators.
    """

    try:
        T_S1 = data["TF_scint"][:, 0]
        T_S2 = data["TF_scint"][:, 1]
        T_S3 = data["TF_scint"][:, 2]
        T_S4 = data["TF_scint"][:, 3]

        diff = T_S1- T_S2

        plt.hist(diff, bins=100, edgecolor='black')
        plt.title("T_S1 - T_S2 Distribution")
        plt.xlabel("Time Difference (ns)")
        plt.ylabel("Counts")
        plt.grid(True)
        plt.show()

    except KeyError as e:
        print(f"Missing expected data key: {e}")


#########################################################


def plot_heatmap(XY, binsX, binsY, rpc, name): 
    """
    Parameters:
    - XY: 2D numpy array (e.g. Qmedian in XY bins)
    - binsX: 1D numpy array of bin edges for X
    - binsY: 1D numpy array of bin edges for Y
    - rpc: int, RPC detector number (used to calculate voltage)
    - name: str, label to use in plot title
    """
    plt.imshow(
        XY.T, 
        origin='lower', 
        aspect='auto',
        extent=[binsX[0], binsX[-1], binsY[0], binsY[-1]],
        cmap='viridis'
    )
    plt.colorbar(label=f'{name}')
    plt.xlabel('X position (mm)')
    plt.ylabel('Y position (mm)')
    plt.title(f'{name}: Heatmap for RPC {rpc}')
    plt.tight_layout()
    plt.show()

#########################################################


def plot_efficiency_vs_time(all_results, label=None, title="Efficiency vs Time"):
    #times = np.array(times)
    for rpc in [1, 2, 3]:  # Or use config
        effs = []
        errs = []
        times = []
        for result in all_results:
            t = result.get(f'time_start_RPC{rpc}', np.nan)
            eff = result.get(f'efficiency_RPC{rpc}', np.nan)
            err = result.get(f'efficiency_error_RPC{rpc}', np.nan)
            effs.append(eff)
            errs.append(err)
            times.append(t) 
        if not np.all(np.isnan(effs)):
            plt.errorbar(times, effs, yerr=errs, fmt='o', label=f'RPC{rpc}')  
    plt.xlabel("Time")
    plt.ylabel("Efficiency")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_volatage_vs_time(all_results, label=None, title="Voltage vs Time"):
    #times = np.array(times)
    for rpc in [1, 2, 3]:  # Or use config
        voltages = []
        times = []
        for result in all_results:
            t = result.get(f'time_start_RPC{rpc}', np.nan)
            V = result.get(f'mean_HV_RPC{rpc}', np.nan)
            voltages.append(V)
            times.append(t) 
        if not np.all(np.isnan(voltages)):
            plt.errorbar(times, voltages, fmt='o', label=f'RPC{rpc}')  
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_temp_vs_time(all_results, label=None, title="Temperature vs Time"):
    #times = np.array(times)
    for rpc in [1, 2, 3]:  # Or use config
        temps = []
        times = []
        for result in all_results:
            t = result.get(f'time_start_RPC{rpc}', np.nan)
            Temp = result.get(f'mean_Temp_RPC{rpc}', np.nan)
            temps.append(Temp)
            times.append(t) 
        if not np.all(np.isnan(temps)):
            plt.errorbar(times, temps, fmt='o', label=f'RPC{rpc}')  
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_humidity_vs_time(all_results, label=None, title="Humidity vs Time"):
    #times = np.array(times)
    for rpc in [1, 2, 3]:  # Or use config
        hums = []
        times = []
        for result in all_results:
            t = result.get(f'time_start_RPC{rpc}', np.nan)
            hum = result.get(f'mean_Hum_RPC{rpc}', np.nan)
            times.append(t) 
            hums.append(hum)
        if not np.all(np.isnan(hums)):
            plt.errorbar(times, hums, fmt='o', label=f'RPC{rpc}')  
    plt.xlabel("Time")
    plt.ylabel("Humidity")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_pressure_vs_time(all_results, label=None, title="Pressure vs Time"):
    #times = np.array(times)
    for rpc in [1, 2, 3]:  # Or use config
        pressures = []
        times = []
        for result in all_results:
            t = result.get(f'time_start_RPC{rpc}', np.nan)
            press = result.get(f'mean_Press_RPC{rpc}', np.nan)
            pressures.append(press)
            times.append(t) 
        if not np.all(np.isnan(pressures)):
            plt.errorbar(times, pressures, fmt='o', label=f'RPC{rpc}')  
    plt.xlabel("Time")
    plt.ylabel("Pressure")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()




def plot_efficiency_vs_voltage(all_results, label=None, title="Efficiency vs Voltage"):
    for rpc in [1, 2, 3]:  # Or use config
        effs = []
        errs = []
        voltages = []
        for result in all_results:
            V = result.get(f'mean_HV_RPC{rpc}', np.nan)
            eff = result.get(f'efficiency_RPC{rpc}', np.nan)
            err = result.get(f'efficiency_error_RPC{rpc}', np.nan)
            effs.append(eff)
            errs.append(err)
            voltages.append(V) 
        if not np.all(np.isnan(effs)):
            plt.errorbar(voltages, effs, yerr=errs, fmt='o', label=f'RPC{rpc}')  
    plt.xlabel("Voltage (V)")
    plt.ylabel("Efficiency")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

def reduced_electric_field  (V, d, P, T):

    #P in hPa
    #d in mm
    #V in V
    #T in Celsius

    kb = 0.13806  # 10^{-22) J/K Boltzmann constant 

    # Convert temperature from Celsius to Kelvin
    T_K = T + 273.15
    
    # Calculate E/N using the formula
    E_N = (kb * V * T_K )/ (P*d) #*10^-21 V*m^2 or TB
    
    return E_N

#print(reduced_electric_field(5000, 1, 1013, 30))


def plot_efficiency_vs_reduced_field(all_results, label=None, title="Efficiency vs E/N"):
    for rpc in [1, 2, 3]:  # Or use config
        effs = []
        errs = []
        E_N= []
        for result in all_results:
            V = result.get(f'mean_HV_RPC{rpc}', np.nan)
            press = result.get(f'mean_Press_RPC{rpc}', np.nan)
            Temp = result.get(f'mean_Temp_RPC{rpc}', np.nan)
            eff = result.get(f'efficiency_RPC{rpc}', np.nan)
            err = result.get(f'efficiency_error_RPC{rpc}', np.nan)
            effs.append(eff)
            errs.append(err)
            E_N.append(reduced_electric_field(V, 1, press, Temp))
        if not np.all(np.isnan(effs)):
            plt.errorbar(E_N, effs, yerr=errs, fmt='o', label=f'RPC{rpc}')
    plt.xlabel("E/N (Td)")
    plt.ylabel("Efficiency")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

########################################################
#TEST
# dataset_file = "sweap4/sest25184133338.mat"
# data = read_data(dataset_file, verbose =1 )
# plot_hist_Q(data, detector=1)
# plot_hist_Q(data, detector="scint")
# plot_hist_Q(data, detector="crew")
# plot_hist_T(data, detector=1)
# plot_hist_T(data, detector="scint")
# plot_hist_T(data, detector="crew")

########################################################