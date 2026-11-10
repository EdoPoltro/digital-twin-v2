# Common data
from pathlib import Path
from typing import Literal

MODULES: list[str] = ["data_extractor", "sparse_generator", "splat_generator"]
ASK_TO_CONTINUE: bool = True
MODE: Literal['stereo', 'mono'] = 'stereo'
OUTPUT: bool = True

DATA: Path = Path('data')
