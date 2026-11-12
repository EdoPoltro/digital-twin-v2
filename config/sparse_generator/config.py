from config.common.config import *
from pathlib import Path

MAX_KEYPOINTS: int = 8192
MAX_RESIZE: int = 2048
KEYPOINTS_THRESHOLD: int = 0.0
OVERLAP: int = 12

DATA_SPARSE_GENERATOR: Path = DATA / 'sparse_generator'

FEATURES: Path = DATA_SPARSE_GENERATOR / '01_features'

MATCHES: Path = DATA_SPARSE_GENERATOR / '02_matches'

SPARSE: Path = DATA_SPARSE_GENERATOR / '03_sparse'

UNDISTORTED: Path = DATA_SPARSE_GENERATOR / '04_undistorted'

