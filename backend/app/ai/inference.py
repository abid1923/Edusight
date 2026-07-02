"""AI model inference pipeline for predicting user learning types."""

import logging
import os

import joblib

from sqlalchemy.orm import Session

from app.ai.cluster_mapping import map_cluster
from app.ai.feature_engineering import FEATURE_COLUMNS, extract_features
from app.ai.preprocessing import preprocess_features

logger = logging.getLogger(__name__)

# ─── Singleton Model & Scaler ─────────────────────────────────
_model = None
_scaler = None
_model_loaded = False

# Path ke file model (relatif dari working directory)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_BASE_DIR, "clustering_model.pkl")
SCALER_PATH = os.path.join(_BASE_DIR, "scaler.pkl")


def load_model():
    """Load the K-Means clustering model and MinMaxScaler scaler from files."""
    global _model, _scaler, _model_loaded

    if _model_loaded:
        logger.info("Model sudah di-load sebelumnya, skip.")
        return

    # Load clustering model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Clustering model tidak ditemukan: {MODEL_PATH}. "
            "Pastikan file clustering_model.pkl ada di folder app/ai/"
        )

    logger.info(f"Loading clustering model dari {MODEL_PATH}...")
    _model = joblib.load(MODEL_PATH)
    logger.info(f"Clustering model berhasil di-load: {type(_model).__name__}")

    # Load scaler
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(
            f"Scaler tidak ditemukan: {SCALER_PATH}. "
            "Pastikan file scaler.pkl ada di folder app/ai/"
        )

    logger.info(f"Loading scaler dari {SCALER_PATH}...")
    _scaler = joblib.load(SCALER_PATH)
    logger.info(f"Scaler berhasil di-load: {type(_scaler).__name__}")

    _model_loaded = True
    logger.info("✅ AI Model & Scaler berhasil di-load!")


def is_model_loaded() -> bool:
    """Check apakah model dan scaler sudah di-load."""
    return _model_loaded


def predict_learning_type(user_id: int, db: Session) -> dict:
    """Predict the learning type cluster for a user in real-time."""
    if not _model_loaded:
        raise RuntimeError(
            "AI model belum di-load. Pastikan load_model() dipanggil saat startup."
        )

    # Step 1: Feature Engineering — extract dari database
    features = extract_features(user_id, db)
    logger.info(f"Features untuk user {user_id}: {features}")

    # Step 2: Preprocessing — DataFrame + Scaling
    scaled_features = preprocess_features(features, _scaler)
    logger.info(f"Scaled features shape: {scaled_features.shape}")

    # Step 3: Predict Cluster
    cluster_id = int(_model.predict(scaled_features)[0])
    logger.info(f"Predicted cluster untuk user {user_id}: {cluster_id}")

    # Step 4: Map ke Learning Type
    result = map_cluster(cluster_id)
    logger.info(f"Learning type untuk user {user_id}: {result['learning_type']}")

    # Tambahkan raw features ke result untuk transparansi
    result["features"] = features

    return result
