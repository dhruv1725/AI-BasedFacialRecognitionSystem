import os
import sys
from datetime import date, datetime

import cv2
import numpy as np


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# IMPORTS
# ============================================================

from app.database.db import get_connection
from app.recognition.face.embedding import FaceEmbedding


# ============================================================
# SETTINGS
# ============================================================

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "faces"
)

CAMERA_INDEX = 0

THRESHOLD = 0.50
MIN_MATCH_MARGIN = 0.04


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):

    try:

        a = np.asarray(a, dtype=np.float32)
        b = np.asarray(b, dtype=np.float32)

        if a.shape != b.shape:
            return -1.0

        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)

        if a_norm == 0 or b_norm == 0:
            return -1.0

        return float(
            np.dot(a, b) /
            (a_norm * b_norm)
        )

    except Exception:

        return -1.0


# ============================================================
# LOAD REGISTERED FACES
# ============================================================

def load_registered_faces():

    registered = {}

    if not os.path.exists(DATASET_PATH):
        return registered

    for folder_name in os.listdir(DATASET_PATH):

        folder_path = os.path.join(
            DATASET_PATH,
            folder_name
        )

        if not os.path.isdir(folder_path):
            continue

        if "_" not in folder_name:
            continue

        student_id, student_name = (
            folder_name.split("_", 1)
        )

        embeddings = []

        for file_name in os.listdir(folder_path):

            if not file_name.endswith(".npy"):
                continue

            file_path = os.path.join(
                folder_path,
                file_name
            )

            try:

                embedding = np.load(
                    file_path
                ).astype(np.float32)

                if embedding.ndim != 1:
                    continue

                if not np.all(
                    np.isfinite(embedding)
                ):
                    continue

                embeddings.append(embedding)

            except Exception as e:

                print(
                    f"Could not load {file_path}: {e}"
                )

        if embeddings:

            registered[student_id] = {
                "name": student_name,
                "embeddings": embeddings
            }

    return registered


# ============================================================
# FIND BEST MATCH
# ============================================================

def find_best_match(
    face_embedding,
    registered_faces
):

    results = []

    for student_id, data in registered_faces.items():

        scores = []

        for stored_embedding in data["embeddings"]:

            score = cosine_similarity(
                face_embedding,
                stored_embedding
            )

            if score >= -1:
                scores.append(score)

        if not scores:
            continue

        scores.sort(reverse=True)

        top_scores = scores[:3]

        best_score = top_scores[0]

        average_top = (
            sum(top_scores) /
            len(top_scores)
        )

        final_score = (
            best_score * 0.70
            +
            average_top * 0.30
        )

        results.append({
            "student_id": student_id,
            "name": data["name"],
            "score": final_score
        })

    if not results:
        return None

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = results[0]

    if len(results) > 1:

        second = results[1]

        margin = (
            best["score"] -
            second["score"]
        )

        if (
            best["score"] < THRESHOLD
            or margin < MIN_MATCH_MARGIN
        ):
            return None

    else:

        if best["score"] < THRESHOLD:
            return None

    return best


# ============================================================
# ATTENDANCE START DATE
# ============================================================

def get_attendance_start_date():

    connection = get_connection()

    if connection is None:
        return date.today()

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT attendance_start_date
            FROM attendance_settings
            WHERE id = 1;
        """)

        row = cursor.fetchone()

        if row and row[0]:
            return row[0]

        return date.today()

    except Exception:

        return date.today()

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# ACTIVE SESSION
# ============================================================

def get_active_session():

    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM attendance_sessions
            WHERE session_date = CURRENT_DATE
              AND status = 'Active'
            ORDER BY id DESC
            LIMIT 1;
        """)

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# MARK ATTENDANCE
# ============================================================

def mark_attendance(student_id):

    today = date.today()

    start_date = get_attendance_start_date()

    if today < start_date:

        return "Attendance period has not started"

    if get_active_session() is None:

        return "Session not active"

    connection = get_connection()

    if connection is None:
        return "Database error"

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM students
            WHERE student_id = %s;
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:
            return "Student not found"

        cursor.execute("""
            SELECT id
            FROM attendance
            WHERE student_id = %s
              AND attendance_date = %s;
        """, (
            student_id,
            today
        ))

        if cursor.fetchone():

            return "Already marked"

        now = datetime.now()

        cursor.execute("""
            INSERT INTO attendance (
                student_id,
                attendance_date,
                attendance_time,
                status
            )
            VALUES (%s, %s, %s, 'Present');
        """, (
            student_id,
            today,
            now.time()
        ))

        connection.commit()

        return "Attendance marked"

    except Exception as e:

        connection.rollback()

        print("Attendance error:")
        print(e)

        return "Database error"

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# RECOGNITION
# ============================================================

def recognize_faces():

    print("RECOGNIZE.PY STARTED")

    if get_active_session() is None:

        print(
            "Attendance session is not active."
        )

        return

    registered_faces = load_registered_faces()

    if not registered_faces:

        print(
            "No registered face embeddings found."
        )

        return

    total_samples = sum(
        len(data["embeddings"])
        for data in registered_faces.values()
    )

    print(
        f"Loaded {total_samples} registered face samples."
    )

    model = FaceEmbedding()

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "Error: Could not open camera."
        )

        return

    print("Recognition started.")
    print("Press Q to quit.")

    marked_this_session = set()

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "Could not read camera frame."
            )

            break

        faces = model.get_faces(frame)

        if len(faces) == 1:

            face = faces[0]

            embedding = face.embedding

            match = find_best_match(
                embedding,
                registered_faces
            )

            x1, y1, x2, y2 = map(
                int,
                face.bbox
            )

            if match:

                student_id = match["student_id"]
                name = match["name"]
                score = match["score"]

                if student_id not in marked_this_session:

                    status = mark_attendance(
                        student_id
                    )

                    if status == "Attendance marked":

                        marked_this_session.add(
                            student_id
                        )

                else:

                    status = "Already marked"

                label = (
                    f"{name} | "
                    f"{score:.2f} | "
                    f"{status}"
                )

            else:

                label = "Unknown"

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

        elif len(faces) > 1:

            cv2.putText(
                frame,
                "Only one face allowed",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "No face detected",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        cv2.imshow(
            "AI Facial Recognition Attendance",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    recognize_faces()