from config.common.config import *
from pathlib import Path

MAX_WORKERS = 4

DATA_SPLAT_GENERATOR: Path = DATA / 'splat_generator'

TRANSFORMS: Path = DATA_SPLAT_GENERATOR / '01_transforms'

TRAINED: Path = DATA_SPLAT_GENERATOR / '02_trained'

SPLAT: Path = DATA_SPLAT_GENERATOR / '03_splat'