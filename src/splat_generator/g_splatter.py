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
        max_workers: int | None = None,
        max_iterations: int | None = None,
        downsample: int | None = None
    ):
        self.log_name = 'G SPLATTER'
        self.mode = mode
        self.output = output
        self.undistorted = undistorted
        self.transforms = transforms
        self.trained = trained
        self.splat = splat
        self.max_workers = max_workers
        self.max_iterations = max_iterations
        self.downsample = downsample


    def start(self) -> None:
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
            colmap_path = (input / 'colmap' / 'sparse' / '0').resolve()
            images_path = (input / 'images').resolve()
            output_path = output.resolve()
            
            command = [
                'ns-process-data', 'images',
                '--data', str(images_path),
                '--output-dir', str(output_path),
                '--skip-colmap', '--skip-image-processing',
                '--colmap-model-path', str(colmap_path),
                '--colmap-cmd', 'true'
            ]
            run_command(command)

            result = output / 'transforms.json'
            if not result.exists():
                raise Exception('File transforms.json non trovato')
            return result
        
        except Exception as e:
            raise GSplatterError(f'Importazione fallita: {e}')

    def _training(self, input_images: Path, input_transforms: Path, output: Path) -> Path:
        try:
            abs_input_images = input_images.resolve()
            abs_input_transforms = input_transforms.resolve()
            abs_output = output.resolve()

            target_images = abs_input_images / 'images'
            symlink_path = abs_input_transforms / 'images'

            if symlink_path.is_symlink():
                symlink_path.unlink()
            elif symlink_path.is_dir():
                shutil.rmtree(symlink_path)
            elif symlink_path.exists():
                symlink_path.unlink()

            symlink_path.symlink_to(target_images)

            command = [
                'ns-train', 'splatfacto',
                '--data', str(abs_input_transforms),
                '--output-dir', str(abs_output),
                '--viewer.quit-on-train-completion', 'True',
                '--vis', 'tensorboard',
            ]

            if self.max_workers:
                command += ['--pipeline.datamanager.max-thread-workers', str(self.max_workers)]
            if self.max_iterations:
                command += ['--max-num-iterations', str(self.max_iterations)]
            if self.downsample:
                command += ['--pipeline.datamanager.camera-res-scale-factor', str(1 / self.downsample)]

            command += [
                'nerfstudio-data',
                '--orientation-method', 'pca',
                '--center-method', 'focus',
            ]
                
            run_command(command)

            target = (abs_output / abs_input_transforms.name / 'splatfacto')
            if not target.exists():
                raise Exception(f'Cartella {target} mancante')
            result = max([d for d in target.iterdir() if d.is_dir()], key=lambda p: p.stat().st_mtime)
            return result

        except Exception as e:
            raise GSplatterError(f"Training fallito: {e}")

    def _exporting(self, input: Path, output: Path) -> Path:
        try:
            abs_input = (input / 'config.yml').resolve()
            abs_output = output.resolve()

            command = [
                'ns-export', 'gaussian-splat', 
                '--load-config', str(abs_input),
                '--output-dir', str(abs_output)
            ]
            run_command(command)

            result = output / 'splat.ply'
            if not result.exists():
                raise Exception(f'File {result} mancante')
            return result

        except Exception as e:
            raise GSplatterError(f'Esportazione fallita: {e}')