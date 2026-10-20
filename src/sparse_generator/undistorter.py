from src.common.exceptions import UndistorterError
from src.common.utils import *
import shutil
import pycolmap
from pathlib import Path

class Undistorter(Logger):
    def __init__(
        self,
        mode: str,
        output: bool,
        sparse: Path,
        undistorted: Path,
        frames_camera_uno: Path,
        frames_camera_due: Path | None = None,
    ):
        self.log_name = 'UNDISTORTER'
        self.mode = mode
        self.output = output
        self.sparse = sparse
        self.undistorted = undistorted
        self.frames_camera_uno = frames_camera_uno
        self.frames_camera_due = frames_camera_due

        self.cameras_file = self.sparse / 'cameras.bin'
        self.images_file = self.sparse / 'images.bin'
        self.points_file = self.sparse / 'points3D.bin'

        self.images = self.undistorted / 'images'
        self.sparse_out = self.undistorted / 'sparse'
        self.model_out = self.sparse_out / '0'

        if self.mode == 'stereo' and not self.frames_camera_due:
            raise UndistorterError("Percorso camera due mancante")

    def start(self):
        self.log('Inizio undistortion')

        # fase 1, controllo input
        file_detection(self.cameras_file, UndistorterError)
        file_detection(self.images_file, UndistorterError)
        file_detection(self.points_file, UndistorterError)

        # fase 2, pulizia output
        folder_cleaning(self.undistorted, UndistorterError)
        self.undistorted.mkdir(parents=True, exist_ok=True)

        # fase 3, undistortion
        self._undistortion(self._image_root())

        # fase 4, struttura output (sparse/0)
        arrange_model(self.model_out, self.sparse_out, UndistorterError)

        self.log('Undistortion completata')

    def _image_root(self) -> Path:
        if self.mode == 'stereo':
            return self.frames_camera_uno.parent
        return self.frames_camera_uno

    def _undistortion(self, image_root: Path) -> None:
        try:
            pycolmap.undistort_images(
                str(self.undistorted),
                str(self.sparse),
                str(image_root),
            )
        except Exception as e:
            raise UndistorterError(f"Undistortion fallita: {e}") from e

        if self.output:
            self.log(f'Immagini raddrizzate salvate in: {self.images}')