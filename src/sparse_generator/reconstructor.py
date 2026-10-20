from src.common.exceptions import FMatcherError
from src.common.utils import *
import json
import pycolmap
from hloc import reconstruction

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
    ):
        self.log_name = 'RECONSTRUCTOR'
        self.mode = mode
        self.output = output
        self.frames_camera_uno = frames_camera_uno
        self.frames_camera_due = frames_camera_due
        self.sparse = sparse
        self.matches = matches
        self.features = features

        self.rig_config = sparse / 'rig_config.json'
        self.features_file = self.features / 'features.h5'
        self.matches_file = self.matches / 'matches.h5'
        self.pairs_file = self.matches / 'pairs.txt'
        self.sparse_file = self.sparse / 'sparse.ply'

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

        # fase 3, configurazione rig
        self._rig_config()
        if self.output:
            self.log(f'Configurazione rig completata: {self.rig_config}')

        mapper_options = pycolmap.IncrementalMapperOptions()
        mapper_options.rig_config_path = str(self.rig_config)

        # fase 4 recostruction
        self._reconstruction(self.frames_camera_uno.parent, mapper_options)

        # fase 4, struttura output (models/0)
        arrange_model(self.model_out, self.sparse, ReconstructorError)

    def _mono(self):

        # fase 1, controllo input
        file_detection(self.features_file, ReconstructorError)
        file_detection(self.matches_file, ReconstructorError)
        file_detection(self.pairs_file, ReconstructorError)

        # fase 2, pulizia output
        folder_cleaning(self.sparse, ReconstructorError)

        # fase 4 recostruction
        self._reconstruction(self.frames_camera_uno)

    def _rig_config(self) -> None:
        rig_config = [
            {
                "ref_camera_id": 1,
                "cameras": [
                    {
                        "camera_id": 1,
                        "image_prefix": f"{self.frames_camera_uno.name}/"
                    },
                    {
                        "camera_id": 2,
                        "image_prefix": f"{self.frames_camera_due.name}/"
                    }
                ]
            }
        ]
        
        try:
            with open(self.rig_config, 'w') as f:
                json.dump(rig_config, f, indent=4)
        except Exception as e:
            raise ReconstructorError("Impossibile salvare il file rig_config.json") from e

    def _reconstruction(self, frames: Path, options = None):
        try:
            if self.mode == 'mono':
                camera_mode = pycolmap.CameraMode.SINGLE
            elif self.mode =='stereo':
                camera_mode = pycolmap.CameraMode.PER_FOLDER

            model = reconstruction.main(
                sfm_dir=self.sparse,
                image_dir=frames,
                pairs=self.pairs_file,
                features=self.features_file,
                matches=self.matches_file,
                camera_mode=camera_mode,
                mapper_options=options
            )

            model.export_PLY(str(self.sparse_file))

            if self.output:
                self.log(f'Modello salvato: {self.sparse_file}')
                self.log(f'Punti trovati: {model.num_points3D()}')
                self.log(f'Immagini allineate: {model.num_reg_images()}')
        except Exception as e:
            raise ReconstructorError(f'Errore nella ricostruzione del modello: {e}') from e