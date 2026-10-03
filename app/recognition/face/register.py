import os
import cv2
import time
import numpy as np

from app.recognition.face.embedding import FaceEmbedding


# ============================================================
# SETTINGS
# ============================================================

TOTAL_SAMPLES = 30
CAPTURE_DELAY = 0.5
CAMERA_INDEX = 0


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "faces"
)

os.makedirs(DATASET_PATH, exist_ok=True)


# ============================================================
# REGISTER FACE
# ============================================================

def register_face():

    print()
    print("=" * 50)
    print("FACE REGISTRATION")
    print("=" * 50)

    student_id = input("Enter Student ID: ").strip()
    name = input("Enter Student Name: ").strip()

    if not student_id:
        print("Student ID cannot be empty.")
        return

    if not name:
        print("Student name cannot be empty.")
        return

    # --------------------------------------------------------
    # Create student folder
    # --------------------------------------------------------

    folder_name = f"{student_id}_{name}"

    student_folder = os.path.join(
        DATASET_PATH,
        folder_name
    )

    os.makedirs(student_folder, exist_ok=True)

    # --------------------------------------------------------
    # Find existing samples
    # --------------------------------------------------------

    existing_files = [
        file_name
        for file_name in os.listdir(student_folder)
        if file_name.lower().endswith(".npy")
    ]

    sample_count = len(existing_files)

    if sample_count >= TOTAL_SAMPLES:
        print()
        print(f"Student already has {sample_count} samples.")
        print(f"Maximum required samples: {TOTAL_SAMPLES}")
        print()
        return

    print()
    print(f"Existing samples: {sample_count}")
    print(f"Samples required: {TOTAL_SAMPLES}")
    print()
    print("Instructions:")
    print("1. Look directly at the camera.")
    print("2. Slowly move your face left and right.")
    print("3. Slightly move up and down.")
    print("4. Keep only one face in front of the camera.")
    print("5. Press Q to stop registration.")
    print()

    # --------------------------------------------------------
    # Load face recognition model
    # --------------------------------------------------------

    try:
        face_model = FaceEmbedding()
    except Exception as e:
        print("Could not load face recognition model.")
        print(e)
        return

    # --------------------------------------------------------
    # Open camera
    # --------------------------------------------------------

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("Error: Could not open camera.")
        return

    last_capture_time = 0

    try:

        while sample_count < TOTAL_SAMPLES:

            success, frame = camera.read()

            if not success:
                print("Error: Could not read frame from camera.")
                break

            # ------------------------------------------------
            # Detect faces
            # ------------------------------------------------

            faces = face_model.get_faces(frame)

            current_time = time.time()

            # ------------------------------------------------
            # Draw detected faces
            # ------------------------------------------------

            if faces:

                for face in faces:

                    box = face.bbox.astype(int)

                    x1, y1, x2, y2 = box

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                # ------------------------------------------------
                # Only capture one face
                # ------------------------------------------------

                if len(faces) == 1:

                    face = faces[0]

                    embedding = getattr(
                        face,
                        "embedding",
                        None
                    )

                    if embedding is not None:

                        if (
                            current_time - last_capture_time
                            >= CAPTURE_DELAY
                        ):

                            sample_count += 1

                            file_name = (
                                f"sample_{sample_count:03d}.npy"
                            )

                            file_path = os.path.join(
                                student_folder,
                                file_name
                            )

                            np.save(
                                file_path,
                                embedding
                            )

                            last_capture_time = current_time

                            print(
                                f"Saved sample "
                                f"{sample_count}/{TOTAL_SAMPLES}"
                            )

                else:

                    cv2.putText(
                        frame,
                        "Only one face allowed",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

            else:

                cv2.putText(
                    frame,
                    "No face detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            # ------------------------------------------------
            # Progress text
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"Samples: {sample_count}/{TOTAL_SAMPLES}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Move face slowly | Press Q to quit",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            # ------------------------------------------------
            # Display camera
            # ------------------------------------------------

            cv2.imshow(
                "Face Registration",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print()
                print("Registration stopped by user.")
                break

    finally:

        camera.release()
        cv2.destroyAllWindows()

    # ========================================================
    # RESULT
    # ========================================================

    print()
    print("=" * 50)
    print("REGISTRATION FINISHED")
    print("=" * 50)

    print(f"Student ID : {student_id}")
    print(f"Name       : {name}")
    print(f"Samples    : {sample_count}/{TOTAL_SAMPLES}")
    print(f"Folder     : {student_folder}")

    if sample_count >= TOTAL_SAMPLES:
        print("Status     : SUCCESS")
    else:
        print("Status     : INCOMPLETE")

    print("=" * 50)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    register_face()