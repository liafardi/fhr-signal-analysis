import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from scipy.stats import skew, kurtosis, ttest_ind
import matplotlib.pyplot as plt


# -----------------------------
# Load Data
# -----------------------------
def load_data(file_path):
    """
    Load dataset from CSV file.
    """
    return pd.read_csv(file_path)


# -----------------------------
# Preprocessing
# -----------------------------
def preprocess_signal(signal):
    """
    Clean and preprocess FHR signal:
    - Remove invalid values
    - Interpolate missing values using PCHIP
    """
    signal = np.array(signal)

    # Keep only physiologically valid values
    valid_mask = (signal >= 50) & (signal <= 200)
    signal = signal[valid_mask]

    if len(signal) < 50:
        return None

    # Interpolation
    x = np.arange(len(signal))
    interpolator = PchipInterpolator(x, signal)
    signal_interp = interpolator(x)

    return signal_interp


# -----------------------------
# Feature Extraction
# -----------------------------
def extract_features(signal):
    """
    Extract statistical features from signal.
    """
    return {
        "mean": np.mean(signal),
        "std": np.std(signal),
        "skewness": skew(signal),
        "kurtosis": kurtosis(signal),
        "rms": np.sqrt(np.mean(signal**2)),
        "entropy": shannon_entropy(signal)
    }


def shannon_entropy(signal):
    """
    Compute Shannon entropy of signal.
    """
    hist, _ = np.histogram(signal, bins=50, density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))


# -----------------------------
# Statistical Analysis
# -----------------------------
def perform_statistical_analysis(df):
    """
    Perform t-test between normal and abnormal groups.
    """
    normal = df[df["pH"] >= 7.20]
    abnormal = df[df["pH"] < 7.20]

    results = {}

    for col in ["mean", "std", "skewness", "kurtosis", "rms", "entropy"]:
        stat, p = ttest_ind(normal[col], abnormal[col], nan_policy='omit')
        results[col] = p

    return results


# -----------------------------
# Plot
# -----------------------------
def plot_entropy(df):
    """
    Create boxplot for entropy comparison.
    """
    normal = df[df["pH"] >= 7.20]["entropy"]
    abnormal = df[df["pH"] < 7.20]["entropy"]

    plt.figure(figsize=(6, 4))
    plt.boxplot([normal, abnormal],
                labels=["Normal pH ≥ 7.20", "Abnormal pH < 7.20"])

    plt.title("Shannon Entropy Distribution")
    plt.ylabel("Entropy")

    plt.savefig("entropy_plot.png")
    plt.close()


# -----------------------------
# Main Pipeline
# -----------------------------
def main():
    df = load_data("data.csv")  # <-- βάλε το σωστό όνομα

    features_list = []

    for _, row in df.iterrows():
        signal = preprocess_signal(row["FHR_signal"])

        if signal is None:
            continue

        features = extract_features(signal)
        features["pH"] = row["pH"]

        features_list.append(features)

    features_df = pd.DataFrame(features_list)

    # Statistical analysis
    results = perform_statistical_analysis(features_df)

    print("Statistical Test Results (p-values):")
    for k, v in results.items():
        print(f"{k}: {v:.5f}")

    # Plot
    plot_entropy(features_df)


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    main()                
