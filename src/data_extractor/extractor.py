from src.common.exceptions import ExtractorError
from src.common.utils import *
import shutil
from typing import Literal, TypedDict
import os
import cv2
import numpy as np

class FramesData(TypedDict):
    id: int
    frames: list[np.ndarray]
    gray: np.ndarray
    blur: float
    flow: float | None
    keypoints: np.ndarray | None

class Extractor(Logger):

    def __init__(
        self,
        mode: Literal['stereo', 'mono'],
        margin: int,
        output: bool,
        flow_filter: int,
        blur_filter: int,
        force_flash_detection: bool,
        max_frame_gap: int,
        raw_camera_uno: Path,
        frames_camera_uno: Path,
        offset_camera_uno: int | None = None,
        raw_camera_due: Path | None = None,
        frames_camera_due: Path | None = None,
        offset_camera_due: int | None = None,
        analysis_scale: float = 0.5,
    ):
        self.mode = mode
        self.margin = margin
        self.output = output
        self.flow_filter = flow_filter
        self.blur_filter = blur_filter
        self.force_flash_detection = force_flash_detection
        self.max_frame_gap = max_frame_gap
        self.raw_camera_uno = raw_camera_uno
        self.raw_camera_due = raw_camera_due
        self.frames_camera_uno = frames_camera_uno
        self.frames_camera_due = frames_camera_due
        self.offset_camera_uno = offset_camera_uno
        self.offset_camera_due = offset_camera_due
        self.analysis_scale = analysis_scale
        self.corner_distance = max(1, round(30 * analysis_scale))

        self.log_name = 'D EXTRACTOR'

        if self.mode == 'stereo':
            if not self.raw_camera_due or not self.frames_camera_due:
                raise ExtractorError("In modalita' stereo devi fornire i percorsi anche per la seconda camera")

    def start(self):
        self.log('Inizio estrazione')

        if self.mode == 'stereo':
            self._stereo()
        elif self.mode == 'mono':
            self._mono()

        self.log("Estrazione conclusa")

    def _stereo(self):

        # fase 1, controllo dati e pulizia
        self.raw_camera_uno_video = self._get_video(self.raw_camera_uno)
        self.raw_camera_due_video = self._get_video(self.raw_camera_due)
        folder_cleaning(self.frames_camera_uno, ExtractorError)
        folder_cleaning(self.frames_camera_due, ExtractorError)
        if self.output:
            self.log(f"Video camera uno: {self.raw_camera_uno_video}")
            self.log(f"Video camera due: {self.raw_camera_due_video}")

        # fase 2, flash detection
        if self.offset_camera_uno is None:
            self.offset_camera_uno = self._flash_detection(self.raw_camera_uno_video)
        if self.offset_camera_due is None:
            self.offset_camera_due = self._flash_detection(self.raw_camera_due_video)
        if self.output:
            self.log(f"Offset camera uno: {self.offset_camera_uno}")
            self.log(f"Offset camera due: {self.offset_camera_due}")

        # fase 3, inizializzo e applico l'offset
        self.capture_camera_uno = cv2.VideoCapture(self.raw_camera_uno_video)
        self.capture_camera_due = cv2.VideoCapture(self.raw_camera_due_video)

        if not self.capture_camera_uno.isOpened() or not self.capture_camera_due.isOpened():
            raise ExtractorError("Impossibile aprire uno o etrambi i video con cv2")

        self.capture_camera_uno.set(cv2.CAP_PROP_POS_FRAMES, self.offset_camera_uno)
        self.capture_camera_due.set(cv2.CAP_PROP_POS_FRAMES, self.offset_camera_due)

        # fase 4, analisi del video
        capture_analysis = cv2.VideoCapture(self.raw_camera_uno_video)

        if not capture_analysis.isOpened():
            raise ExtractorError("Impossibile aprire il video per l'analisi")

        capture_analysis.set(cv2.CAP_PROP_POS_FRAMES, self.offset_camera_uno)
        if self.output:
            self.log('Inizio analisi')

        tot_frame, min_flow, max_flow, mean_flow, self.flow_threshold, min_blur, max_blur, mean_blur, self.blur_threshold = self._analyze_video(capture_analysis)
        capture_analysis.release()

        if self.output:
            self.log(f"Frame analizzati: {tot_frame}")
            self.log(f"Range flow: {min_flow:.1f}px - {max_flow:.1f}px - {mean_flow:.1f}px - {self.flow_threshold:.1f}px")
            self.log(f"Range blur: {min_blur:.1f} - {max_blur:.1f} - {mean_blur:.1f} - {self.blur_threshold:.1f}")

        # fase 5, estrazione e salvataggio frame
        counter, avg_gap, max_gap = self._extraction([self.capture_camera_uno, self.capture_camera_due])
        if self.output:
            self.log(f"Frames:    {counter}") 
            self.log(f"Gap medio: {avg_gap:.1f}")
            self.log(f"Gap max:   {max_gap}")

        # fase 6, release
        self.capture_camera_uno.release()
        self.capture_camera_due.release()

    def _mono(self):
                
        # fase 1, controllo dati e pulizia
        self.raw_camera_uno_video = self._get_video(self.raw_camera_uno)
        folder_cleaning(self.frames_camera_uno, ExtractorError)
        if self.output:
            self.log(f"Video trovato: {self.raw_camera_uno_video}")

        # fase 2, flash detection forzata
        if self.force_flash_detection:
            if self.offset_camera_uno is None:
                self.offset_camera_uno = self._flash_detection(self.raw_camera_uno_video)   
            if self.output:
                self.log(f"Offset impostato: {self.offset_camera_uno}")

        # fase 2, inizializzo e applico l'offset
        self.capture_camera_uno = cv2.VideoCapture(self.raw_camera_uno_video)

        if not self.capture_camera_uno.isOpened():
            raise ExtractorError("Impossibile aprire il video con cv2")

        if self.offset_camera_uno:
            self.capture_camera_uno.set(cv2.CAP_PROP_POS_FRAMES, self.offset_camera_uno)

        # fase 3, analisi del video
        capture_analysis = cv2.VideoCapture(self.raw_camera_uno_video)

        if not capture_analysis.isOpened():
            raise ExtractorError("Impossibile aprire il video per l'analisi")

        if self.offset_camera_uno:
            capture_analysis.set(cv2.CAP_PROP_POS_FRAMES, self.offset_camera_uno)
        if self.output:
            self.log('Inizio analisi')

        tot_frame, min_flow, max_flow, mean_flow, self.flow_threshold, min_blur, max_blur, mean_blur, self.blur_threshold = self._analyze_video(capture_analysis)
        capture_analysis.release()

        if self.output:
            self.log(f"Frames analizzati: {tot_frame}")
            self.log(f"Range flow: {min_flow:.1f}px - {max_flow:.1f}px - {mean_flow:.1f}px - {self.flow_threshold:.1f}px")
            self.log(f"Range blur: {min_blur:.1f} - {max_blur:.1f} - {mean_blur:.1f} - {self.blur_threshold:.1f}")

        # fase 4, estrazione e salvataggio frame
        counter, avg_gap, max_gap = self._extraction([self.capture_camera_uno])
        if self.output:
            self.log(f"Frames:    {counter}") 
            self.log(f"Gap medio: {avg_gap:.1f}")
            self.log(f"Gap max:   {max_gap}")

        # fase 5, release
        self.capture_camera_uno.release()

    def _get_video(self, folder: Path) -> Path:
        extensions = ('.mp4', '.avi', '.mov', '.mkv')

        num = data_detection(folder, ExtractorError)

        if num > 1:
            raise ExtractorError(f"La cartella contiene piu' di un video: {folder}")
        
        content: list[str] = [f for f in os.listdir(folder) if not f.startswith('.')]
        target = folder / content[0]

        if not os.path.isfile(target):
            raise ExtractorError(f"La cartella non contiene video: {folder}")

        if not content[0].lower().endswith(extensions):
            raise ExtractorError(f"Il video non e' di un formato supportato: {target}")
        
        return target

    def _flash_detection(self, video: str, max_variation=30) -> int:
        capture = cv2.VideoCapture(video)
        tot_frame = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        max_frame = int(tot_frame * 0.40)

        frame_found = None
        old_brightness = None

        for i in range(max_frame):
            ret_frame, frame = capture.read()

            if not ret_frame:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.percentile(gray, 95)

            if old_brightness is not None:
                variation = brightness - old_brightness
                if variation > 0 and variation > max_variation:
                    frame_found = i
                    break

            old_brightness = brightness

        capture.release()

        if frame_found is None:
            raise ExtractorError('Flash detection fallita')

        result = frame_found + self.margin

        if result > tot_frame:
            raise ExtractorError("Il frame trovato e' troppo vicino alla fine del video")

        return result

    def _analyze_video(self, video: cv2.VideoCapture):
        tot_frame = 0
        last_gray = None
        last_keypoints = None

        blur_values = []
        flow_values = []

        while True:
            ret, frame = video.read()

            if not ret:
                break

            tot_frame += 1
            if self.output:
                if tot_frame % 50 == 0 and getattr(self, 'output', True):
                    self.log(f"Frames esaminati: {tot_frame}")

            gray = self._to_gray(frame)
            
            if last_gray is None:
                last_gray = gray.copy()
                last_keypoints = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=self.corner_distance)
                continue

            blur = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_values.append(blur)

            if last_keypoints is not None and len(last_keypoints) > 0:
                new_keypoints, status, _ = cv2.calcOpticalFlowPyrLK(last_gray, gray, last_keypoints, None)

                good_new = new_keypoints[status == 1]
                good_old = last_keypoints[status == 1]

                if len(good_new) > 10:
                    distances = np.linalg.norm(good_new - good_old, axis=1)
                    avg_movement = np.mean(distances)
                    flow_values.append(avg_movement)

            last_gray = gray.copy()
            last_keypoints = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=self.corner_distance)

        if last_gray is None:
            raise ExtractorError("L'analisi e' fallita, si e' verificato un problema con il video")

        min_blur = min(blur_values)
        max_blur = max(blur_values)
        mean_blur = sum(blur_values) / len(blur_values)

        min_flow = min(flow_values) if flow_values else 0
        max_flow = max(flow_values) if flow_values else 0
        mean_flow = sum(flow_values) / len(flow_values) if flow_values else 0

        blur_threshold = np.percentile(blur_values, self.blur_filter)
        flow_threshold = np.percentile(flow_values, self.flow_filter)     

        return tot_frame, min_flow, max_flow, mean_flow, flow_threshold, min_blur, max_blur, mean_blur, blur_threshold

    def _extraction(self, captures: list) -> tuple[int, float, int]:

        current_frames: FramesData | None = None
        last_saved_frames: FramesData | None = None
        best_frames: FramesData | None = None
        prev_best_frames: FramesData | None = None
        saved_frames_counter: int = 0

        saved_ids: list[int] = []

        while True: 
            frames = []
            rets = []
            for cap in captures:
                ret, frame = cap.read()
                rets.append(ret)
                frames.append(frame)

            if not all(rets):
                break

            gray = self._to_gray(frames[0])
            current_frames = {
                'id': 1 if current_frames is None else current_frames['id'] + 1,
                'frames': frames,
                'gray': gray,
                'blur': float(cv2.Laplacian(gray, cv2.CV_64F).var()),
                'flow': None,
                'keypoints': None
            }

            if last_saved_frames is None:
                last_saved_frames = self._save_frames(current_frames, saved_frames_counter + 1, 'Primo salvataggio')
                saved_ids.append(last_saved_frames['id'])
                saved_frames_counter += 1
                continue

            prev_best_frames = best_frames
            if best_frames is None or current_frames['blur'] > best_frames['blur']:
                best_frames = current_frames

            if current_frames['id'] - last_saved_frames['id'] >= self.max_frame_gap:
                last_saved_frames = self._save_frames(best_frames, saved_frames_counter + 1, f'Gap massimo ({self.max_frame_gap})')
                saved_ids.append(last_saved_frames['id'])
                saved_frames_counter += 1
                best_frames = None
                continue

            if current_frames['blur'] < self.blur_threshold:
                continue

            if last_saved_frames['keypoints'] is not None and len(last_saved_frames['keypoints']) > 0:
                new_keypoints, status, _= cv2.calcOpticalFlowPyrLK(last_saved_frames['gray'], current_frames['gray'], last_saved_frames['keypoints'], None)

                good_new = new_keypoints[status == 1]
                good_old = last_saved_frames['keypoints'][status == 1]

                if len(good_new) > 10:
                    current_frames['flow'] = float(np.mean(np.linalg.norm(good_new - good_old, axis=1)))

            if current_frames['flow'] is None:
                chosen = prev_best_frames if prev_best_frames is not None else current_frames
                last_saved_frames = self._save_frames(chosen, saved_frames_counter + 1, 'Tracciamento perso')
                saved_ids.append(last_saved_frames['id'])
                saved_frames_counter += 1
                best_frames = current_frames if chosen is not current_frames else None

            elif current_frames['flow'] >= self.flow_threshold:
                last_saved_frames = self._save_frames(current_frames, saved_frames_counter + 1, 'Movimento')
                saved_ids.append(last_saved_frames['id'])
                saved_frames_counter += 1
                best_frames = None

        if last_saved_frames is None:
            raise ExtractorError("L'estrazione e' fallita, si e' verificato un problema con uno dei due video")

        if saved_frames_counter <= 10:
            raise ExtractorError("Sono stati estratti meno di 10 frame")

        gaps = [b - a for a, b in zip(saved_ids, saved_ids[1:])]
        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)

        return saved_frames_counter, avg_gap, max_gap

    def _save_frames(self, frames: FramesData, number: int, reason: str) -> FramesData:
        self._save_frame(self.frames_camera_uno, frames['frames'][0], number)
        if len(frames['frames']) > 1:
            self._save_frame(self.frames_camera_due, frames['frames'][1], number)

        frames['keypoints'] = cv2.goodFeaturesToTrack(frames['gray'], maxCorners=200, qualityLevel=0.01, minDistance=self.corner_distance)

        if self.output:
            flow = f" - Flow: {frames['flow']:.1f}px" if frames['flow'] is not None else ''
            self.log(f"Frame {number:03d} (video {frames['id']}) - {reason}{flow} - Blur: {frames['blur']:.1f}")
        return frames

    def _save_frame(self, folder: Path, frame: np.ndarray, index: int):
        target = f'frame_{index:04d}.png'
        target_path = folder / target
        cv2.imwrite(target_path, frame)

    def _to_gray(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.analysis_scale != 1.0:
            gray = cv2.resize(gray, None, fx=self.analysis_scale, fy=self.analysis_scale, interpolation=cv2.INTER_AREA)

        return gray
