from config.common.config import *
from pathlib import Path

MAX_KEYPOINTS = 4096
KEYPOINTS_THRESHOLD = 0.0
OVERLAP = 5

DATA_SPARSE_GENERATOR: Path = DATA / 'sparse_generator'

FEATURES: Path = DATA_SPARSE_GENERATOR / '01_features'

MATCHES: Path = DATA_SPARSE_GENERATOR / '02_matches'

SPARSE: Path = DATA_SPARSE_GENERATOR / '03_sparse'

UNDISTORTED: Path = DATA_SPARSE_GENERATOR / '04_undistorted'

