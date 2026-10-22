from src.data_extractor.extractor import Extractor
from src.sparse_generator.f_extractor import FExtractor
from src.sparse_generator.f_matcher import FMatcher
from src.sparse_generator.reconstructor import Reconstructor
from src.sparse_generator.undistorter import Undistorter
from src.common.exceptions import *
from config.common.config import *
from config.data_extractor.config import *
from config.sparse_generator.config import *
from config.splat_generator.config import *
from src.common.utils import ask_to_continue

def main():
    try:
        # extractor = Extractor(
        #     mode=MODE,
        #     margin=MARGIN_OFFSET,
        #     offset_camera_uno=OFFSET_CAMERA_UNO,
        #     offset_camera_due=OFFSET_CAMERA_DUE,
        #     output=OUTPUT,
        #     raw_camera_uno=RAW_CAMERA_UNO,
        #     raw_camera_due=RAW_CAMERA_DUE,
        #     frames_camera_uno=FRAMES_CAMERA_UNO,
        #     frames_camera_due=FRAMES_CAMERA_DUE
        # )
        # extractor.start()

        # if ASK_TO_CONTINUE:
        #     if not ask_to_continue():
        #         return

        # f_extractor = FExtractor(
        #     mode=MODE,
        #     output=OUTPUT,
        #     features=FEATURES,
        #     frames_camera_uno=FRAMES_CAMERA_UNO,
        #     frames_camera_due=FRAMES_CAMERA_DUE,
        #     max_keypoints=MAX_KEYPOINTS,
        #     keypoints_threshold=KEYPOINTS_THRESHOLD
        # )

        # f_extractor.start()

        # f_matcher = FMatcher(
        #     mode=MODE,
        #     output=OUTPUT,
        #     features=FEATURES,
        #     frames_camera_uno=FRAMES_CAMERA_UNO,
        #     frames_camera_due=FRAMES_CAMERA_DUE,
        #     matches=MATCHES,
        #     overlap=OVERLAP
        # )

        # f_matcher.start()

        reconstructor = Reconstructor(
            mode=MODE,
            output=OUTPUT,
            sparse=SPARSE,
            frames_camera_uno=FRAMES_CAMERA_UNO,
            features=FEATURES,
            frames_camera_due=FRAMES_CAMERA_DUE,
            matches=MATCHES
        )

        reconstructor.start()

        undistorter = Undistorter(
            mode=MODE,
            output=OUTPUT,
            sparse=SPARSE,
            undistorted=UNDISTORTED,
            frames_camera_uno=FRAMES_CAMERA_UNO,
            frames_camera_due=FRAMES_CAMERA_DUE
        )

        undistorter.start()

        if ASK_TO_CONTINUE:
            if not ask_to_continue():
                return

    except ExtractorError as e:
        print(f'[D EXTRACTOR] {e}')
    except FExtractorError as e:
        print(f'[F EXTRACTOR] {e}')
    except FMatcherError as e:
        print(f'[F MATCHER] {e}')
    except ReconstructorError as e:
        print(f'[RECONSTRUCTOR] {e}')
    except Exception as e:
        print(f'Errore imprevisto: {e}')

if __name__ == "__main__":
    main()