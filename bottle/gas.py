import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import linregress

# Path to where your log files are stored
log_dir = Path("/home/lidka/SWGO/bottle")

# Find all files that match the pattern
files = sorted(log_dir.glob("scale-*.log"))

data = []

# Read each file
for f in files:
    with open(f) as file:
        line = file.readline().strip()
        if line:
            # Split into timestamp and value
            timestamp_str, value_str = line.split()
            data.append((pd.to_datetime(timestamp_str), float(value_str)))

# Create DataFrame
df = pd.DataFrame(data, columns=["timestamp", "value"])

# Sort by timestamp
df = df.sort_values("timestamp")


# Convert timestamps to numeric for regression (in days)
x = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds() / (24*3600)
y = df["value"]

# Fit a straight line: y = slope*x + intercept
slope, intercept, r_value, p_value, std_err = linregress(x, y)

# Generate fitted values
df["fit"] = slope * x + intercept

# Plot the data and fitted line
plt.figure(figsize=(10, 5))
plt.scatter(df["timestamp"], df["value"], color="blue", label="Data")
plt.plot(df["timestamp"], df["fit"], color="red", linewidth=2, label=f"Fit (slope={slope:.3f})")
plt.title("Scale Data with Linear Fit")
plt.xlabel("Date")
plt.ylabel("Value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Print regression stats
print(f"Slope: {slope:.4f} units/day")
print(f"Intercept: {intercept:.4f}")
print(f"R²: {r_value**2:.4f}")