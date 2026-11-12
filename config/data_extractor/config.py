from config.common.config import *
from pathlib import Path

MARGIN_OFFSET: int = 60
MAX_FRAME_GAP: int = 15 
OFFSET_CAMERA_UNO: int | None = None
OFFSET_CAMERA_DUE: int | None = None
FORCE_FLASH_DETECTION: bool = True
FLOW_FILTER: int = 55
BLUR_FILTER: int = 55
ANALYSIS_SCALE: float = 0.5

DATA_DATA_EXTRACTOR: Path = DATA / 'data_extractor'

RAW: Path = DATA_DATA_EXTRACTOR / '01_raw'
RAW_CAMERA_UNO: Path = RAW / 'camera_uno'
RAW_CAMERA_DUE: Path = RAW / 'camera_due'

FRAMES: Path = DATA_DATA_EXTRACTOR / '02_frames'
FRAMES_CAMERA_UNO: Path = FRAMES / 'camera_uno'
FRAMES_CAMERA_DUE: Path = FRAMES / 'camera_due'

