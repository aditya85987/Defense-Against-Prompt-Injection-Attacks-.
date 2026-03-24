import pandas as pd
import numpy as np
import math
import os
import joblib
from sklearn.ensemble import IsolationForest

def calculate_shannon_entropy(text):
    if not text:
        return 0.0
    from collections import Counter
    counts = Counter(text)
    length = len(text)
    entropy = -sum((count / length) * math.log2(count / length) for count in counts.values())
    return entropy

def extract_features(text):
    """
    Converts raw text into a numerical array of three features:
    1. Length: Total character count.
    2. Shannon Entropy: Character-level entropy.
    3. Special Character Ratio: Non-alphanumeric chars / total length.
    """
    text = str(text)
    length = len(text)
    if length == 0:
        return [0.0, 0.0, 0.0]
        
    entropy = calculate_shannon_entropy(text)
    
    # Count non-alphanumeric characters (excluding spaces)
    special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
    special_ratio = special_chars / length
    
    return [length, entropy, special_ratio]

def main():
    print("Loading Dataset...")
    csv_path = os.path.join(os.path.dirname(__file__), "prompts_dataset.csv")
    df = pd.read_csv(csv_path)
    
    print("Extracting Features...")
    # Apply extraction to format the feature matrix X
    X = np.array([extract_features(text) for text in df["text"]])
    
    print(f"Feature Matrix X shape: {X.shape}")
    
    # Train IsolationForest
    # Note: Contamination implies the expected proportion of anomalies in the dataset.
    print("Training sklearn IsolationForest...")
    model = IsolationForest(n_estimators=100, contamination=0.5, random_state=42)
    model.fit(X)
    
    model_path = os.path.join(os.path.dirname(__file__), "anomaly_detector.joblib")
    joblib.dump(model, model_path)
    print(f"Model successfully saved to {model_path}")

if __name__ == "__main__":
    main()
