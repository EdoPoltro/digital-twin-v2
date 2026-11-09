from src.common.exceptions import GSplatterError
from src.common.utils import *
from pathlib import Path

class GSplatter(Logger):
    def __init__(
        self,
        mode: str,
        output: bool,
        undistorted: Path,
        transforms: Path,
        trained: Path,
        splat: Path,
        max_workers: int | None = None
    ):
        self.log_name = 'G SPLATTER'
        self.mode = mode
        self.output = output
        self.undistorted = undistorted
        self.transforms = transforms
        self.trained = trained
        self.splat = splat
        self.max_workers = max_workers

    def start(self):
        self.log('Inizio splatting')

        # fase 1, data detaction
        if self.mode == 'stereo':
            num_frame_uno = data_detection(self.undistorted / 'images' / 'camera_uno', GSplatterError)
            num_frame_due = data_detection(self.undistorted / 'images' / 'camera_due', GSplatterError)

            if num_frame_uno != num_frame_due:
                raise GSplatterError('Numero diverso di frame nelle due cartelle')

        else:
            num_frame_uno = data_detection(self.undistorted / 'images', GSplatterError)

        if self.output:
            self.log(f'Frames trovati: {num_frame_uno}')

        # fase 2, cleaning output
        folder_cleaning(self.transforms, GSplatterError)
        folder_cleaning(self.trained, GSplatterError)
        folder_cleaning(self.splat, GSplatterError)

        # fase 3, transforming
        result = self._transforming(self.undistorted, self.transforms)
        if self.output:
            self.log(f"Importazione terminata, output salvato in: {result}")

        # fase 4, training
        result = self._training(self.undistorted, self.transforms, self.trained)
        if self.output:
            self.log(f"Training terminato, output salvato in: {result}")

        # fase 5, exporting
        result = self._exporting(result, self.splat)
        if self.output:
            self.log(f'Esportazione terminata, output salvato in: {result}')

        self.log('Fine splatting')

    def _transforming(self, input: Path, output: Path) -> Path:
        try:
            command = [
                'ns-process-data', 'images',
                '--data', str(input / 'images'),
                '--output-dir', str(output),
                '--skip-colmap', '--skip-image-processing',
                '--colmap-model-path', str(input / 'colmap' / 'sparse' / '0')
            ]
            run_command(command)

            result = output / 'transforms.json'
            if not result.exists():
                raise Exception('File transforms.json non trovato')
            return result
        
        except Exception as e:
            raise GSplatterError(f'Importing fallito: {e}')

    def _training(self, input_images: Path, input_transforms: Path, output: Path) -> Path:
        try:
            symlink_path = input_transforms / 'images'
            if not symlink_path.exists():
                symlink_path.symlink_to(input_images / 'images')

            command = [
                'ns-train', 'splatfacto',
                '--data', str(input_transforms),
                '--output-dir', str(output),
                '--viewer.quit-on-train-completion', 'True',
                '--vis', 'tensorboard'
            ]

            if self.max_workers:
                command += ['--pipeline.datamanager.num-workers', str(self.max_workers)]
            run_command(command)

            target = (output / input_transforms.name / 'splatfacto')
            if not target.exists():
                raise Exception(f'cartella {target} mancante')
            result = max([d for d in target.iterdir() if d.is_dir()], key=lambda p: p.stat().st_mtime)
            return result

        except Exception as e:
            raise GSplatterError(f"Training fallito: {e}")

    def _exporting(self, input: Path, output: Path) -> Path:
        try:
            command = [
                'ns-export', 'gaussian-splat', 
                '--load-config', str(input / 'config.yml'),
                '--output-dir', str(output)
            ]
            run_command(command)

            result = output / 'splat.ply'
            if not result.exists():
                raise Exception(f'File {result} mancante')
            return result

        except Exception as e:
            raise GSplatterError(f'Exporting fallito: {e}')