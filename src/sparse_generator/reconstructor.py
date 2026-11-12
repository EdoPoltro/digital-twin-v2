from src.common.exceptions import ReconstructorError
from hloc import reconstruction, triangulation
from src.common.utils import *
import numpy as np
import pycolmap

class Reconstructor(Logger):
    def __init__(
        self,
        mode: str,
        output: bool,
        matches: Path,
        features: Path,
        sparse: Path,
        frames_camera_uno: Path,
        frames_camera_due: Path | None = None,
        rig_offset: tuple[float, float, float] | None = None
    ):
        self.log_name = 'RECONSTRUCTOR'
        self.mode = mode
        self.output = output
        self.frames_camera_uno = frames_camera_uno
        self.frames_camera_due = frames_camera_due
        self.sparse = sparse
        self.matches = matches
        self.features = features
        self.rig_offset = rig_offset

        self.features_file = self.features / 'features.h5'
        self.matches_file = self.matches / 'matches.h5'
        self.pairs_file = self.matches / 'pairs.txt'
        self.sparse_file = self.sparse / 'sparse.ply'
        self.database = self.sparse / 'database.db'
        self.model_out = self.sparse / 'models' / '0'

        if self.mode == 'stereo' and not self.frames_camera_due:
            raise ReconstructorError("Percorso camera due mancante")

    def start(self):
        self.log('Inizio ricostruzione')
                    
        if self.mode == 'stereo':
            self._stereo()
        elif self.mode == 'mono':
            self._mono()

        self.log("Ricostruzione completata")

    def _stereo(self):

        # fase 1, controllo input
        file_detection(self.features_file, ReconstructorError)
        file_detection(self.matches_file, ReconstructorError)
        file_detection(self.pairs_file, ReconstructorError)

        # fase 2, pulizia output
        folder_cleaning(self.sparse, ReconstructorError)

        # fase 3, recostruction
        first_points, first_alignements, final_points, final_alignements = self._reconstruction_stereo(self.frames_camera_uno.parent)
        if self.output:
            self.log(f'prima ricostruzione punti trovati: {first_points}')
            self.log(f'prima ricostruzione immagini allineate: {first_alignements}')
            self.log(f'seconda ricostruzione punti trovati: {final_points}')
            self.log(f'seconda ricostruzione immagini allineate: {final_alignements}')
                    
        # fase 4, struttura output (models/0)
        arrange_model(self.model_out, self.sparse, ReconstructorError)

    def _mono(self):

        # fase 1, controllo input
        file_detection(self.features_file, ReconstructorError)
        file_detection(self.matches_file, ReconstructorError)
        file_detection(self.pairs_file, ReconstructorError)

        # fase 2, pulizia output
        folder_cleaning(self.sparse, ReconstructorError)

        # fase 3 recostruction
        points, alignements = self._reconstruction_mono(self.frames_camera_uno)
        if self.output:
            self.log(f'Punti trovati: {points}')
            self.log(f'Immagini allineate: {alignements}')

        # fase 4, struttura output (models/0)
        arrange_model(self.model_out, self.sparse, ReconstructorError)

    def _rig_config(self) -> pycolmap.RigConfig:
        camera_due = pycolmap.RigConfigCamera(image_prefix=f'{self.frames_camera_due.name}/')

        if self.rig_offset is not None:
            cam_from_rig = pycolmap.Rigid3d()                                   
            cam_from_rig.translation = -np.array(self.rig_offset, dtype=float)  
            camera_due.cam_from_rig = cam_from_rig

        return pycolmap.RigConfig(cameras=[
            pycolmap.RigConfigCamera(ref_sensor=True, image_prefix=f'{self.frames_camera_uno.name}/'), 
            camera_due,
        ])

    def _database_config(self, frames: Path, camera_mode) -> None:
        reconstruction.create_empty_db(self.database)
        reconstruction.import_images(
            frames, self.database, camera_mode, None, dict(camera_model='OPENCV')
        )
        image_ids = reconstruction.get_image_ids(self.database)
        with pycolmap.Database.open(self.database) as db:
            triangulation.import_features(image_ids, db, self.features_file)
            triangulation.import_matches(
                image_ids, db, self.pairs_file, self.matches_file, None, False
            )
        triangulation.estimation_and_geometric_verification(
            self.database, self.pairs_file, False
        )

    def _reconstruction_stereo(self, frames: Path) -> tuple[int, int, int, int]:
        try:
            self._database_config(frames, pycolmap.CameraMode.PER_FOLDER)

            first_points = 0
            first_alignements = 0
            options = None

            if self.rig_offset is None:
                first_model = reconstruction.run_reconstruction(self.sparse, self.database, frames)
                if first_model is None:
                    raise Exception('Nessun modello generato dal primo passaggio di ricostruzione')
                first_points = first_model.num_points3D()
                first_alignements = first_model.num_reg_images()

                shutil.rmtree(self.sparse / 'models', ignore_errors=True)
                with pycolmap.Database.open(self.database) as db:
                    pycolmap.apply_rig_config([self._rig_config()], db, first_model)
            else:

                with pycolmap.Database.open(self.database) as db:
                    pycolmap.apply_rig_config([self._rig_config()], db)
                options = {'ba_refine_sensor_from_rig': False}

            final_model = reconstruction.run_reconstruction(self.sparse, self.database, frames, False, options)
            if final_model is None:
                raise Exception('Nessun modello generato dal passaggio finale di ricostruzione')

            self._save_model(final_model)

            return first_points, first_alignements, final_model.num_points3D(), final_model.num_reg_images()

        except Exception as e:
            raise ReconstructorError(f'Errore nella ricostruzione del modello: {e}')

    def _reconstruction_mono(self, frames: Path, options = None) -> tuple[int, int]:
        try:
            model = reconstruction.main(
                sfm_dir=self.sparse,
                image_dir=frames,
                pairs=self.pairs_file,
                features=self.features_file,
                matches=self.matches_file,
                camera_mode=pycolmap.CameraMode.SINGLE,
                mapper_options=options,
                image_options=dict(camera_model='OPENCV')
            )

            self._save_model(model)

            return model.num_points3D(), model.num_reg_images()
        except Exception as e:
            raise ReconstructorError(f'Errore nella ricostruzione del modello: {e}')

    def _save_model(self, model) -> None:
        shutil.rmtree(self.sparse / 'models', ignore_errors=True)
        self.model_out.mkdir(parents=True, exist_ok=True)
        model.write(str(self.model_out))
        model.export_PLY(str(self.sparse_file))

    