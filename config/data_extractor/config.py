from config.common.config import *
from pathlib import Path

MARGIN_OFFSET: int = 20
OFFSET_CAMERA_UNO: int = None
OFFSET_CAMERA_DUE: int = None

DATA_DATA_EXTRACTOR: Path = DATA / 'data_extractor'

RAW: Path = DATA_DATA_EXTRACTOR / '01_raw'
RAW_CAMERA_UNO: Path = RAW / 'camera_uno'
RAW_CAMERA_DUE: Path = RAW / 'camera_due'

FRAMES: Path = DATA_DATA_EXTRACTOR / '02_frames'
FRAMES_CAMERA_UNO: Path = FRAMES / 'camera_uno'
FRAMES_CAMERA_DUE: Path = FRAMES / 'camera_due'

