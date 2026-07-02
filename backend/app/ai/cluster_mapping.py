"""
Cluster Mapping.
Mengubah hasil cluster prediction menjadi learning type yang human-readable.

User tidak boleh melihat "Cluster 0".
User harus melihat "Active Learner".
"""


# ─── Cluster Mapping Definition ───────────────────────────────
# Mapping HARUS sesuai dengan hasil analisis notebook modelling.
CLUSTER_MAP = {
    1: {
        "learning_type": "Active Learner",
        "insight_text": (
            "User memiliki aktivitas belajar tinggi dan progress yang aktif. "
            "Kamu memiliki pola belajar yang sangat aktif dan konsisten. "
            "Skor quiz kamu tinggi dan kamu menyelesaikan banyak materi secara teratur. "
            "Pertahankan momentum ini!"
        ),
    },
    2: {
        "learning_type": "Moderate Learner",
        "insight_text": (
            "User memiliki aktivitas belajar cukup stabil tetapi masih perlu meningkatkan konsistensi. "
            "Kamu memiliki pola belajar yang cukup konsisten. "
            "Skor quiz menunjukkan pemahaman yang baik, tapi masih ada ruang untuk peningkatan. "
            "Coba lebih sering review materi."
        ),
    },
    0: {
        "learning_type": "Passive Learner",
        "insight_text": (
            "User memiliki aktivitas belajar rendah dan membutuhkan motivasi tambahan. "
            "Pola belajar kamu menunjukkan potensi yang besar, tapi masih perlu lebih banyak latihan. "
            "Cobalah untuk lebih konsisten dalam menyelesaikan materi dan mengerjakan quiz."
        ),
    },
}

# Default fallback jika cluster tidak ditemukan di mapping
DEFAULT_CLUSTER = {
    "learning_type": "Unknown Learner",
    "insight_text": "Tipe belajar belum dapat ditentukan. Terus tingkatkan aktivitas belajarmu!",
}


def map_cluster(cluster_id: int) -> dict:
    """
    Mengubah cluster ID menjadi learning type dan insight text.

    Args:
        cluster_id: Hasil prediksi dari model clustering (0, 1, atau 2).

    Returns:
        Dictionary berisi:
        - learning_type: Nama tipe belajar (human-readable)
        - insight_text: Deskripsi insight untuk user
    """
    cluster_info = CLUSTER_MAP.get(cluster_id, DEFAULT_CLUSTER)

    return {
        "cluster_id": cluster_id,
        "learning_type": cluster_info["learning_type"],
        "insight_text": cluster_info["insight_text"],
    }