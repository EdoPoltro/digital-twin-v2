from src.common.exceptions import FExtractorError
from src.common.utils import *
import shutil
from hloc import extract_features
from pathlib import Path
import os

class FExtractor(Logger):
    def __init__(
        self,
        mode: str,
        output: bool,
        frames_camera_uno: Path,
        features: Path,
        frames_camera_due: Path | None = None,
        max_keypoints: int = 4096,
        keypoints_threshold: float = 0.0
    ):
        self.log_name = 'F EXTRACTOR'
        self.mode = mode
        self.output = output
        self.frames_camera_uno = frames_camera_uno
        self.frames_camera_due = frames_camera_due
        self.features = features

        self.conf = extract_features.confs['superpoint_aachen'].copy()
        self.conf['model']['max_keypoints'] = max_keypoints
        self.conf['model']['keypoint_threshold'] = keypoints_threshold

        if self.mode == 'stereo':
            if not self.frames_camera_due:
                raise FExtractorError("Percorso camera due mancante")

    def start(self):
        self.log('Inizio estrazione')
    
        if self.mode == 'stereo':
            self._stereo()
        elif self.mode == 'mono':
            self._mono()

        self.log("Estrazione conclusa")

    def _stereo(self):
        # fase 1, controllo dati e pulizia
        num_frame_uno = data_detection(self.frames_camera_uno, FExtractorError)
        num_frame_due = data_detection(self.frames_camera_due, FExtractorError)

        if num_frame_uno != num_frame_due:
            raise FExtractorError('Numero diverso di frame nelle due cartelle')
        
        if self.output:
            self.log(f'Frame trovati : {num_frame_uno}')

        # fase 2, cleaning output
        folder_cleaning(self.features, FExtractorError)
        target = self.features / 'features.h5'

        # fase 3, estrazione 
        self._extraction(self.conf, self.frames_camera_uno.parent, target)
    
    def _mono(self):

        # fase 1, controllo dati e pulizia
        num_frame = data_detection(self.frames_camera_uno, FExtractorError)
        if self.output:
            self.log(f'Frame trovati : {num_frame}')

        # fase 2, cleaning output
        folder_cleaning(self.features, FExtractorError)
        target = self.features / 'features.h5'

        # fase 3, estrazione 
        self._extraction(self.conf, self.frames_camera_uno, target)

    def _extraction(self, conf, images: Path, target: Path):
        try:
            extract_features.main(
                conf=conf,
                image_dir=images,
                feature_path=target
            )
        except Exception:
            raise FExtractorError("L'estrazione e' fallita")
        