from src.common.exceptions import FMatcherError
from src.common.utils import *
from hloc import match_features
from pathlib import Path

# capire se lapproccio migliore per la funzione di matching e fare una altra funzione 
# volendo posso rendere globale il minimo di frame trovati per lanciare exception
# rendere univoci i nomi dei file e non hardcoded

class FMatcher(Logger):
    def __init__(
        self,
        mode: str,
        output: bool,
        features: Path,
        matches: Path,
        frames_camera_uno: Path,
        overlap: int,
        frames_camera_due: Path | None = None,
    ):
        self.log_name = 'F MATCHER'
        self.mode = mode
        self.output = output
        self.features = features
        self.matches = matches
        self.overlap = overlap
        self.frames_camera_uno = frames_camera_uno
        self.frames_camera_due = frames_camera_due

        self.features_file = self.features / 'features.h5'
        self.pairs_file = self.matches / 'pairs.txt'
        self.matches_file = self.matches / 'matches.h5'

        self.conf = match_features.confs['superpoint+lightglue'].copy()

        if self.mode == 'stereo' and not self.frames_camera_due:
            raise FMatcherError("Percorso camera due mancante")

    def start(self):
        self.log('Inizio matching')
            
        if self.mode == 'stereo':
            self._stereo()
        elif self.mode == 'mono':
            self._mono()

        self.log("Matching completato")

    def _stereo(self):
        # fase 1, controllo input
        file_detection(self.features_file, FMatcherError)
        
        # fase 2, pulizia output
        folder_cleaning(self.matches, FMatcherError)

        # fase 3, pairs
        pairing_result = self._stereo_pairing(self.pairs_file)
        if self.output:
            self.log(f'Pairing completato, coppie trovare: {pairing_result}')

        # fase 4, matching
        self._matching(self.features_file, self.pairs_file, self.matches_file)

    def _mono(self):
        # fase 1, controllo input
        file_detection(self.features_file, FMatcherError)

        # fase 2, pulizia output
        folder_cleaning(self.matches, FMatcherError)

        # fase 3, pairs
        pairing_result = self._mono_pairing(self.pairs_file)
        if self.output:
            self.log(f'Pairing completato, coppie trovare: {pairing_result}')

        # fase 4, matching
        self._matching(self.features_file, self.pairs_file, self.matches_file)
            
    def _stereo_pairing(self, target) -> int:
        frames_camera_uno = sorted([frame.name for frame in self.frames_camera_uno.iterdir() if frame.is_file()])
        frames_camera_due = sorted([frame.name for frame in  self.frames_camera_due.iterdir() if frame.is_file()])

        if not frames_camera_uno or not frames_camera_due:
            raise FMatcherError('Impossibile ottenere i frame')

        pairs = []

        for i in range(len(frames_camera_uno)):
            current_frame_uno = f'{self.frames_camera_uno.name}/{frames_camera_uno[i]}'
            current_frame_due = f'{self.frames_camera_due.name}/{frames_camera_due[i]}'

            pairs.append(f'{current_frame_uno} {current_frame_due}')
            if self.output:
                self.log(f'Coppia creata {current_frame_uno} - {current_frame_due}')

            for j in range(1, self.overlap + 1):
                next_index = i + j
                
                if next_index < len(frames_camera_uno):
                    next_frame_uno = f"{self.frames_camera_uno.name}/{frames_camera_uno[next_index]}"
                    next_frame_due = f"{self.frames_camera_due.name}/{frames_camera_due[next_index]}"
                    
                    pairs.append(f"{current_frame_uno} {next_frame_uno}")
                    pairs.append(f"{current_frame_due} {next_frame_due}")
                    pairs.append(f"{current_frame_uno} {next_frame_due}")
                    if self.output:
                        self.log(f'Coppia creata {current_frame_uno} - {next_frame_uno}')
                        self.log(f'Coppia creata {current_frame_due} - {next_frame_due}')
                        self.log(f'Coppia creata {current_frame_uno} - {next_frame_due}')

        try:
            with open(target, 'w') as file:
                file.write('\n'.join(pairs))
        except Exception as e:
            raise FMatcherError('Errore nel salvataggio del file pairs.txt') from e

        return len(pairs)

    def _mono_pairing(self, target) -> int:
        frames = sorted([frame.name for frame in self.frames_camera_uno.iterdir() if frame.is_file()])

        if not frames:
            raise FMatcherError('Impossibile ottenere i frame')

        pairs = []

        for i in range(len(frames)):
            current_frame = frames[i]

            for j in range(1, self.overlap + 1):
                next_index = i + j

                if next_index < len(frames):
                    next_frame = frames[next_index]

                    pairs.append(f"{current_frame} {next_frame}") 

                    if self.output:
                        self.log(f'Coppia creata {current_frame} - {next_frame}')

        try:
            with open(target, 'w') as file:
                file.write('\n'.join(pairs))
        except Exception as e:
            raise FMatcherError('Errore nel salvataggio del file pairs.txt')from e

        return len(pairs)

    def _matching(self, features, pairs, target) -> None:
        try:
            match_features.main(
                conf=self.conf,
                pairs=pairs,
                features=features,
                matches=target
            )        
        except Exception as e:
            raise FMatcherError("Matching fallito") from e
