"""
Preprocessing Pipeline.
Melakukan preprocessing sebelum prediction.

Steps:
1. Numeric conversion
2. DataFrame formatting (urutan kolom HARUS sama dengan training)
3. Scaling menggunakan scaler dari training
4. Feature ordering validation
"""

import pandas as pd

from app.ai.feature_engineering import FEATURE_COLUMNS


def preprocess_features(features: dict, scaler) -> pd.DataFrame:
    """
    Preprocessing features sebelum prediction.

    IMPORTANT: Urutan feature HARUS sama dengan notebook modelling.
    Scaler yang digunakan HARUS sama dengan scaler training.

    Args:
        features: Dictionary dari feature_engineering.extract_features().
        scaler: Fitted scaler dari file scaler.pkl.

    Returns:
        Scaled DataFrame siap untuk model.predict().
        Returns DataFrame (bukan numpy array) agar feature names terjaga.
    """
    # Step 1: Buat DataFrame dengan urutan kolom yang SAMA dengan training
    df = pd.DataFrame([features], columns=FEATURE_COLUMNS)

    # Step 2: Pastikan semua nilai numeric
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # Step 3: Scaling menggunakan scaler yang sama dengan training
    # Kembalikan sebagai DataFrame agar feature names terjaga untuk model.predict()
    scaled_array = scaler.transform(df)
    scaled_df = pd.DataFrame(scaled_array, columns=FEATURE_COLUMNS)

    return scaled_df

