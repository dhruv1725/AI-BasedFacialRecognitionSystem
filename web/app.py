import os
import sys
import base64
import shutil
from datetime import datetime, date, timedelta

import cv2
import numpy as np

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# IMPORTS
# ============================================================

from app.database.db import get_connection
from app.recognition.face.embedding import FaceEmbedding
from app.liveness.liveness import LivenessDetector


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ============================================================
# PATHS / SETTINGS
# ============================================================

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "faces"
)

os.makedirs(DATASET_PATH, exist_ok=True)


# ============================================================
# FACE RECOGNITION SETTINGS
# ============================================================

THRESHOLD = 0.50
MIN_MATCH_MARGIN = 0.04
MAX_REGISTERED_SAMPLES = 30


face_model = None


# ============================================================
# LIVENESS
# ============================================================

try:

    liveness_detector = LivenessDetector()

except Exception as e:

    print("Liveness detector initialization failed:")
    print(e)

    liveness_detector = None


# ============================================================
# FACE MODEL
# ============================================================

def get_face_model():

    global face_model

    if face_model is None:

        print("Loading InsightFace model...")

        face_model = FaceEmbedding()

        print("InsightFace model ready.")

    return face_model


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        # Students
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Attendance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                attendance_date DATE NOT NULL,
                attendance_time TIME NOT NULL,
                status VARCHAR(20) DEFAULT 'Present',
                UNIQUE(student_id, attendance_date)
            );
        """)

        # Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                id SERIAL PRIMARY KEY,
                session_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME,
                status VARCHAR(20) DEFAULT 'Active',
                CHECK (status IN ('Active', 'Completed'))
            );
        """)

        # Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_settings (
                id INTEGER PRIMARY KEY,
                attendance_start_date DATE NOT NULL
            );
        """)

        cursor.execute("""
            INSERT INTO attendance_settings
                (id, attendance_start_date)
            VALUES
                (1, CURRENT_DATE)
            ON CONFLICT (id) DO NOTHING;
        """)

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print("Database initialization error:")
        print(e)

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()


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

        # Safety fallback
        return date.today()

    except Exception as e:

        print("Could not get attendance start date:")
        print(e)

        return date.today()

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# SET ATTENDANCE START DATE
# ============================================================

def set_attendance_start_date(start_date):

    connection = get_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE attendance_settings
            SET attendance_start_date = %s
            WHERE id = 1;
        """, (start_date,))

        connection.commit()

        return True, "Attendance period updated successfully."

    except Exception as e:

        connection.rollback()

        print("Could not update attendance start date:")
        print(e)

        return False, "Could not update attendance period."

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# GET ACTIVE SESSION
# ============================================================

def get_active_session():

    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor()

        # IMPORTANT:
        # Only today's active session is valid.
        cursor.execute("""
            SELECT
                id,
                session_date,
                start_time,
                end_time,
                status
            FROM attendance_sessions
            WHERE session_date = CURRENT_DATE
              AND status = 'Active'
            ORDER BY id DESC
            LIMIT 1;
        """)

        return cursor.fetchone()

    except Exception as e:

        print("Could not get active session:")
        print(e)

        return None

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# GET LATEST SESSION
# ============================================================

def get_latest_session():

    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                session_date,
                start_time,
                end_time,
                status
            FROM attendance_sessions
            ORDER BY id DESC
            LIMIT 1;
        """)

        return cursor.fetchone()

    except Exception as e:

        print("Could not get latest session:")
        print(e)

        return None

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# GET ALL STUDENTS
# ============================================================

def get_all_students():

    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                student_id,
                name,
                created_at
            FROM students
            ORDER BY student_id;
        """)

        return cursor.fetchall()

    except Exception as e:

        print("Could not get students:")
        print(e)

        return []

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# COUNT WORKING DAYS
# ============================================================

def count_working_days(start_date, end_date):

    if start_date > end_date:
        return 0

    current = start_date
    count = 0

    while current <= end_date:

        if current.weekday() < 5:
            count += 1

        current += timedelta(days=1)

    return count


# ============================================================
# MARK ATTENDANCE
# ============================================================

def mark_attendance(student_id):

    today = date.today()

    start_date = get_attendance_start_date()

    if today < start_date:
        return {
            "success": False,
            "code": "PERIOD_NOT_STARTED",
            "message": "Attendance period has not started yet."
        }

    session = get_active_session()

    if session is None:
        return {
            "success": False,
            "code": "SESSION_NOT_ACTIVE",
            "message": "Attendance session is not active."
        }

    connection = get_connection()

    if connection is None:
        return {
            "success": False,
            "code": "DATABASE_ERROR",
            "message": "Database connection failed."
        }

    cursor = None

    try:

        cursor = connection.cursor()

        # Check student
        cursor.execute("""
            SELECT student_id, name
            FROM students
            WHERE student_id = %s;
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:

            return {
                "success": False,
                "code": "STUDENT_NOT_FOUND",
                "message": "Student is not registered."
            }

        # Check duplicate
        cursor.execute("""
            SELECT id
            FROM attendance
            WHERE student_id = %s
              AND attendance_date = %s;
        """, (student_id, today))

        existing = cursor.fetchone()

        if existing:

            return {
                "success": True,
                "code": "ALREADY_MARKED",
                "message": "Attendance already marked.",
                "student_id": student_id,
                "name": student[1]
            }

        # Insert attendance
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

        return {
            "success": True,
            "code": "MARKED",
            "message": "Attendance marked successfully.",
            "student_id": student_id,
            "name": student[1]
        }

    except Exception as e:

        connection.rollback()

        print("Attendance error:")
        print(e)

        return {
            "success": False,
            "code": "DATABASE_ERROR",
            "message": "Could not save attendance."
        }

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# IMAGE DECODER
# ============================================================

def decode_image(image_data):

    try:

        if not image_data:
            return None

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        return frame

    except Exception as e:

        print("Image decode error:")
        print(e)

        return None


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):

    try:

        a = np.asarray(a, dtype=np.float32)
        b = np.asarray(b, dtype=np.float32)

        if a.size == 0 or b.size == 0:
            return -1.0

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
# LOAD REGISTERED EMBEDDINGS
# ============================================================

def load_registered_embeddings():

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

        student_id, student_name = folder_name.split(
            "_",
            1
        )

        embeddings = []

        for file_name in os.listdir(folder_path):

            if not file_name.lower().endswith(".npy"):
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

                if embedding.size == 0:
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

def find_best_match(query_embedding):

    registered = load_registered_embeddings()

    if not registered:
        return None

    student_results = []

    for student_id, student_data in registered.items():

        scores = []

        for stored_embedding in student_data["embeddings"]:

            score = cosine_similarity(
                query_embedding,
                stored_embedding
            )

            if score >= -1:
                scores.append(score)

        if not scores:
            continue

        scores.sort(reverse=True)

        # Use the strongest few samples rather than
        # trusting one random sample.
        top_scores = scores[:3]

        best_score = top_scores[0]
        average_top_score = sum(top_scores) / len(top_scores)

        final_score = (
            (best_score * 0.70)
            +
            (average_top_score * 0.30)
        )

        student_results.append({
            "student_id": student_id,
            "name": student_data["name"],
            "score": final_score,
            "best_score": best_score
        })

    if not student_results:
        return None

    student_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = student_results[0]

    # Compare best and second-best students.
    if len(student_results) > 1:

        second = student_results[1]

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
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    start_date = get_attendance_start_date()

    return render_template(
        "dashboard.html",
        attendance_start_date=start_date
    )


# ============================================================
# STUDENTS
# ============================================================

@app.route("/students")
def students():

    return render_template(
        "students.html",
        students=get_all_students()
    )


# ============================================================
# REGISTER STUDENT
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    name = request.form.get(
        "name",
        ""
    ).strip()

    if not student_id or not name:

        return jsonify({
            "success": False,
            "message": "Student ID and name are required."
        }), 400

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM students
            WHERE student_id = %s;
        """, (student_id,))

        existing = cursor.fetchone()

        if existing:

            return jsonify({
                "success": False,
                "message": "Student ID already exists."
            }), 409

        cursor.execute("""
            INSERT INTO students (
                student_id,
                name
            )
            VALUES (%s, %s);
        """, (
            student_id,
            name
        ))

        connection.commit()

        safe_name = (
            name
            .replace("/", "_")
            .replace("\\", "_")
            .strip()
        )

        folder_name = f"{student_id}_{safe_name}"

        os.makedirs(
            os.path.join(
                DATASET_PATH,
                folder_name
            ),
            exist_ok=True
        )

        return jsonify({
            "success": True,
            "message": "Student registered successfully."
        })

    except Exception as e:

        connection.rollback()

        print("Registration error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not register student."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# REGISTER FACE SAMPLE
# ============================================================

@app.route("/api/register-face", methods=["POST"])
def register_face():

    data = request.get_json(silent=True) or {}

    student_id = str(
        data.get("student_id", "")
    ).strip()

    name = str(
        data.get("name", "")
    ).strip()

    image = data.get("image")

    if not student_id or not name or not image:

        return jsonify({
            "success": False,
            "message": "Student ID, name and image are required."
        }), 400

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

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

            return jsonify({
                "success": False,
                "message": "Student is not registered."
            }), 404

        actual_name = student[0]

        safe_name = (
            actual_name
            .replace("/", "_")
            .replace("\\", "_")
            .strip()
        )

        folder_name = (
            f"{student_id}_{safe_name}"
        )

        folder_path = os.path.join(
            DATASET_PATH,
            folder_name
        )

        os.makedirs(
            folder_path,
            exist_ok=True
        )

        existing_samples = [
            file
            for file in os.listdir(folder_path)
            if file.lower().endswith(".npy")
        ]

        if len(existing_samples) >= MAX_REGISTERED_SAMPLES:

            return jsonify({
                "success": False,
                "message": "Maximum 30 face samples already registered."
            }), 400

        frame = decode_image(image)

        if frame is None:

            return jsonify({
                "success": False,
                "message": "Invalid image."
            }), 400

        model = get_face_model()

        faces = model.get_faces(frame)

        if len(faces) != 1:

            return jsonify({
                "success": False,
                "message": "Exactly one face must be visible."
            }), 400

        embedding = faces[0].embedding

        if embedding is None:

            return jsonify({
                "success": False,
                "message": "Could not generate face embedding."
            }), 400

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        )

        if not np.all(np.isfinite(embedding)):

            return jsonify({
                "success": False,
                "message": "Invalid face embedding."
            }), 400

        sample_number = len(existing_samples) + 1

        while True:

            file_name = (
                f"sample_{sample_number:03d}.npy"
            )

            file_path = os.path.join(
                folder_path,
                file_name
            )

            if not os.path.exists(file_path):
                break

            sample_number += 1

        np.save(
            file_path,
            embedding
        )

        return jsonify({
            "success": True,
            "message": "Face sample saved.",
            "sample_number": sample_number,
            "total_samples": len(existing_samples) + 1
        })

    except Exception as e:

        print("Face registration error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not save face sample."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# DELETE STUDENT
# ============================================================

@app.route(
    "/students/delete/<student_id>",
    methods=["POST"]
)
def delete_student(student_id):

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM attendance
            WHERE student_id = %s;
        """, (student_id,))

        cursor.execute("""
            DELETE FROM students
            WHERE student_id = %s;
        """, (student_id,))

        deleted = cursor.rowcount

        connection.commit()

        if deleted == 0:

            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        # Delete every dataset folder belonging to this ID.
        if os.path.exists(DATASET_PATH):

            for folder_name in os.listdir(DATASET_PATH):

                if folder_name.startswith(
                    f"{student_id}_"
                ):

                    folder_path = os.path.join(
                        DATASET_PATH,
                        folder_name
                    )

                    if os.path.isdir(folder_path):

                        shutil.rmtree(
                            folder_path,
                            ignore_errors=True
                        )

        return jsonify({
            "success": True,
            "message": "Student deleted successfully."
        })

    except Exception as e:

        connection.rollback()

        print("Delete error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not delete student."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# STUDENT DETAIL
# ============================================================

@app.route(
    "/attendance/student/<student_id>"
)
def student_detail(student_id):

    connection = get_connection()

    if connection is None:

        return "Database connection failed.", 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                student_id,
                name,
                created_at
            FROM students
            WHERE student_id = %s;
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:

            return "Student not found.", 404

        cursor.execute("""
            SELECT
                attendance_date,
                attendance_time,
                status
            FROM attendance
            WHERE student_id = %s
            ORDER BY attendance_date DESC,
                     attendance_time DESC;
        """, (student_id,))

        attendance = cursor.fetchall()

        global_start = get_attendance_start_date()

        created_date = (
            student[3].date()
            if student[3]
            else global_start
        )

        effective_start = max(
            global_start,
            created_date
        )

        expected_days = count_working_days(
            effective_start,
            date.today()
        )

        present_days = sum(
            1
            for record in attendance
            if record[2] == "Present"
            and effective_start <= record[0] <= date.today()
        )

        absent_days = max(
            0,
            expected_days - present_days
        )

        if expected_days > 0:

            attendance_percentage = round(
                (
                    present_days /
                    expected_days
                ) * 100,
                2
            )

        else:

            attendance_percentage = 0

        analytics = {
            "expected_working_days": expected_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "attendance_percentage": attendance_percentage,
            "attendance_start_date": effective_start
        }

        return render_template(
            "student_detail.html",
            student=student,
            attendance=attendance,
            analytics=analytics
        )

    except Exception as e:

        print("Student detail error:")
        print(e)

        return "Could not load student.", 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# START ATTENDANCE PERIOD
# ============================================================

@app.route(
    "/attendance/start",
    methods=["POST"]
)
def attendance_start():

    start_date_value = request.form.get(
        "start_date",
        ""
    ).strip()

    if not start_date_value:

        return jsonify({
            "success": False,
            "message": "Start date is required."
        }), 400

    try:

        start_date = datetime.strptime(
            start_date_value,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Invalid date format."
        }), 400

    if start_date > date.today():

        return jsonify({
            "success": False,
            "message": "Future date is not allowed."
        }), 400

    success, message = set_attendance_start_date(
        start_date
    )

    if not success:

        return jsonify({
            "success": False,
            "message": message
        }), 500

    return jsonify({
        "success": True,
        "message": message,
        "attendance_start_date": start_date.isoformat()
    })


# ============================================================
# START RECOGNITION SESSION
# ============================================================

@app.route(
    "/api/attendance/session/start",
    methods=["POST"]
)
def start_attendance_session():

    start_date = get_attendance_start_date()

    if date.today() < start_date:

        return jsonify({
            "success": False,
            "message": "Attendance period has not started yet."
        }), 400

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        # Complete stale sessions from previous dates.
        cursor.execute("""
            UPDATE attendance_sessions
            SET status = 'Completed',
                end_time = COALESCE(end_time, CURRENT_TIME)
            WHERE status = 'Active'
              AND session_date < CURRENT_DATE;
        """)

        cursor.execute("""
            SELECT
                id,
                session_date,
                start_time,
                end_time,
                status
            FROM attendance_sessions
            WHERE session_date = CURRENT_DATE
              AND status = 'Active'
            ORDER BY id DESC
            LIMIT 1;
        """)

        existing = cursor.fetchone()

        if existing:

            connection.commit()

            return jsonify({
                "success": True,
                "message": "Attendance session is already active.",
                "session": {
                    "id": existing[0],
                    "session_date": str(existing[1]),
                    "start_time": str(existing[2]),
                    "end_time": (
                        str(existing[3])
                        if existing[3]
                        else None
                    ),
                    "status": existing[4]
                }
            })

        now = datetime.now()

        cursor.execute("""
            INSERT INTO attendance_sessions (
                session_date,
                start_time,
                status
            )
            VALUES (
                CURRENT_DATE,
                %s,
                'Active'
            )
            RETURNING
                id,
                session_date,
                start_time,
                end_time,
                status;
        """, (now.time(),))

        session = cursor.fetchone()

        connection.commit()

        if liveness_detector:
            liveness_detector.reset()

        return jsonify({
            "success": True,
            "message": "Attendance session started.",
            "session": {
                "id": session[0],
                "session_date": str(session[1]),
                "start_time": str(session[2]),
                "end_time": (
                    str(session[3])
                    if session[3]
                    else None
                ),
                "status": session[4]
            }
        })

    except Exception as e:

        connection.rollback()

        print("Session start error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not start attendance session."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# STOP RECOGNITION SESSION
# ============================================================

@app.route(
    "/api/attendance/session/stop",
    methods=["POST"]
)
def stop_attendance_session():

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE attendance_sessions
            SET
                end_time = CURRENT_TIME,
                status = 'Completed'
            WHERE id = (
                SELECT id
                FROM attendance_sessions
                WHERE session_date = CURRENT_DATE
                  AND status = 'Active'
                ORDER BY id DESC
                LIMIT 1
            )
            RETURNING
                id,
                session_date,
                start_time,
                end_time,
                status;
        """)

        session = cursor.fetchone()

        connection.commit()

        if session is None:

            return jsonify({
                "success": False,
                "message": "No active attendance session."
            }), 400

        if liveness_detector:
            liveness_detector.reset()

        return jsonify({
            "success": True,
            "message": "Attendance session stopped.",
            "session": {
                "id": session[0],
                "session_date": str(session[1]),
                "start_time": str(session[2]),
                "end_time": str(session[3]),
                "status": session[4]
            }
        })

    except Exception as e:

        connection.rollback()

        print("Session stop error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not stop attendance session."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# SESSION API
# ============================================================

@app.route("/api/attendance/session")
def attendance_session():

    session = get_active_session()

    if session:

        return jsonify({
            "active": True,
            "session": {
                "id": session[0],
                "session_date": str(session[1]),
                "start_time": str(session[2]),
                "end_time": (
                    str(session[3])
                    if session[3]
                    else None
                ),
                "status": session[4]
            }
        })

    latest = get_latest_session()

    if latest:

        return jsonify({
            "active": False,
            "session": {
                "id": latest[0],
                "session_date": str(latest[1]),
                "start_time": str(latest[2]),
                "end_time": (
                    str(latest[3])
                    if latest[3]
                    else None
                ),
                "status": latest[4]
            }
        })

    return jsonify({
        "active": False,
        "session": None
    })


# ============================================================
# DASHBOARD ANALYTICS
# ============================================================

@app.route("/api/analytics/dashboard")
def dashboard_analytics():

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        start_date = get_attendance_start_date()
        today = date.today()

        cursor.execute("""
            SELECT COUNT(*)
            FROM students;
        """)

        total_students = cursor.fetchone()[0]

        working_days = count_working_days(
            start_date,
            today
        )

        expected_attendance = (
            total_students *
            working_days
        )

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE attendance_date >= %s
              AND attendance_date <= %s
              AND status = 'Present';
        """, (
            start_date,
            today
        ))

        present_records = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE attendance_date = CURRENT_DATE
              AND status = 'Present';
        """)

        present_today = cursor.fetchone()[0]

        if expected_attendance > 0:

            attendance_percentage = round(
                (
                    present_records /
                    expected_attendance
                ) * 100,
                2
            )

        else:

            attendance_percentage = 0

        absent_records = max(
            0,
            expected_attendance -
            present_records
        )

        if attendance_percentage >= 85:
            status = "Healthy"
            insight = "Attendance is currently above 85%."
        elif attendance_percentage >= 75:
            status = "Moderate"
            insight = "Attendance is currently between 75% and 85%."
        else:
            status = "Needs Attention"
            insight = "Attendance is currently below 75%."

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance_sessions;
        """)

        total_sessions = cursor.fetchone()[0]

        return jsonify({
            "success": True,

            "total_students": total_students,

            "present": present_records,

            "present_today": present_today,

            "absent": absent_records,

            "percentage": attendance_percentage,

            "attendance_percentage": attendance_percentage,

            "attendance_start_date": start_date.isoformat(),

            "working_days": working_days,

            "expected_attendance": expected_attendance,

            "total_sessions": total_sessions,

            "status": status,

            "insight": insight
        })

    except Exception as e:

        print("Dashboard analytics error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not calculate analytics."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# STUDENT ANALYTICS API
# ============================================================

@app.route(
    "/api/analytics/student/<student_id>"
)
def student_analytics(student_id):

    connection = get_connection()

    if connection is None:

        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT created_at
            FROM students
            WHERE student_id = %s;
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:

            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        global_start = get_attendance_start_date()

        created_date = (
            student[0].date()
            if student[0]
            else global_start
        )

        effective_start = max(
            global_start,
            created_date
        )

        today = date.today()

        expected_days = count_working_days(
            effective_start,
            today
        )

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE student_id = %s
              AND attendance_date >= %s
              AND attendance_date <= %s
              AND status = 'Present';
        """, (
            student_id,
            effective_start,
            today
        ))

        present_days = cursor.fetchone()[0]

        absent_days = max(
            0,
            expected_days -
            present_days
        )

        if expected_days > 0:

            attendance_percentage = round(
                (
                    present_days /
                    expected_days
                ) * 100,
                2
            )

        else:

            attendance_percentage = 0

        return jsonify({
            "success": True,
            "expected_working_days": expected_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "attendance_percentage": attendance_percentage,
            "attendance_start_date": effective_start.isoformat()
        })

    except Exception as e:

        print("Student analytics error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Could not calculate student analytics."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# TODAY ATTENDANCE
# ============================================================

@app.route("/attendance/today")
def today_attendance():

    connection = get_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                s.student_id,
                s.name,
                a.attendance_date,
                a.attendance_time,
                a.status
            FROM attendance a
            JOIN students s
                ON s.student_id = a.student_id
            WHERE a.attendance_date = CURRENT_DATE
            ORDER BY a.attendance_time DESC;
        """)

        attendance = cursor.fetchall()

        students = get_all_students()

        return render_template(
            "today_attendance.html",
            students=students,
            attendance=attendance
        )

    except Exception as e:

        print("Today attendance error:")
        print(e)

        return "Could not load attendance.", 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# ALL ATTENDANCE
# ============================================================

@app.route("/attendance/all")
def all_attendance():

    connection = get_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                s.student_id,
                s.name,
                a.attendance_date,
                a.attendance_time,
                a.status
            FROM attendance a
            JOIN students s
                ON s.student_id = a.student_id
            ORDER BY
                a.attendance_date DESC,
                a.attendance_time DESC;
        """)

        attendance = cursor.fetchall()

        return render_template(
            "all_attendance.html",
            attendance=attendance
        )

    except Exception as e:

        print("All attendance error:")
        print(e)

        return "Could not load attendance.", 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# RECOGNITION PAGE
# ============================================================

@app.route("/recognition")
def recognition():

    return render_template(
        "recognition.html"
    )


# ============================================================
# RECOGNIZE FACE
# ============================================================

@app.route(
    "/api/recognize",
    methods=["POST"]
)
def recognize():

    # --------------------------------------------------------
    # SESSION CHECK
    # --------------------------------------------------------

    session = get_active_session()

    if session is None:

        return jsonify({
            "success": False,
            "recognized": False,
            "message": "Attendance session is not active."
        }), 400

    # --------------------------------------------------------
    # LIVENESS CHECK
    # --------------------------------------------------------

    if (
        liveness_detector is not None
        and not liveness_detector.is_live()
    ):

        return jsonify({
            "success": False,
            "recognized": False,
            "message": "Please blink once before recognition."
        }), 400

    data = request.get_json(silent=True) or {}

    image = data.get("image")

    frame = decode_image(image)

    if frame is None:

        return jsonify({
            "success": False,
            "recognized": False,
            "message": "Invalid camera image."
        }), 400

    model = get_face_model()

    faces = model.get_faces(frame)

    # --------------------------------------------------------
    # EXACTLY ONE FACE
    # --------------------------------------------------------

    if len(faces) == 0:

        return jsonify({
            "success": False,
            "recognized": False,
            "message": "No face detected."
        }), 200

    if len(faces) > 1:

        return jsonify({
            "success": False,
            "recognized": False,
            "message": "Only one face should be visible."
        }), 200

    face = faces[0]

    embedding = face.embedding

    if embedding is None:

        return jsonify({
            "success": False,
            "recognized": False,
            "message": "Could not generate face embedding."
        }), 200

    match = find_best_match(
        embedding
    )

    if match is None:

        return jsonify({
            "success": True,
            "recognized": False,
            "name": "Unknown",
            "message": "Face not recognized."
        })

    attendance_result = mark_attendance(
        match["student_id"]
    )

    # After successfully marking a new person,
    # require another blink for the next person.
    if (
        attendance_result["code"] == "MARKED"
        and liveness_detector is not None
    ):

        liveness_detector.reset()

    return jsonify({
        "success": True,
        "recognized": True,
        "student_id": match["student_id"],
        "name": match["name"],
        "confidence": round(
            match["score"] * 100,
            2
        ),
        "similarity": round(
            match["score"],
            4
        ),
        "attendance": attendance_result["message"],
        "attendance_code": attendance_result["code"]
    })


# ============================================================
# LIVENESS RESET
# ============================================================

@app.route(
    "/api/liveness/reset",
    methods=["POST"]
)
def reset_liveness():

    if liveness_detector is None:

        return jsonify({
            "success": False,
            "message": "Liveness detector unavailable."
        }), 500

    liveness_detector.reset()

    return jsonify({
        "success": True,
        "message": "Liveness reset."
    })


# ============================================================
# LIVENESS CHECK
# ============================================================

@app.route(
    "/api/liveness/check",
    methods=["POST"]
)
def check_liveness():

    if liveness_detector is None:

        return jsonify({
            "success": False,
            "live": False,
            "message": "Liveness detector unavailable."
        }), 500

    data = request.get_json(silent=True) or {}

    image = data.get("image")

    frame = decode_image(image)

    if frame is None:

        return jsonify({
            "success": False,
            "live": False,
            "message": "Invalid image."
        }), 400

    live = liveness_detector.check_liveness(
        frame
    )

    return jsonify({
        "success": True,
        "live": live,
        "message": (
            "Liveness detected."
            if live
            else "Please blink once."
        )
    })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    connection = get_connection()

    database_ok = connection is not None

    if connection:
        connection.close()

    return jsonify({
        "status": "ok",
        "database": database_ok,
        "face_model_loaded": face_model is not None,
        "liveness_available": liveness_detector is not None
    })


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("FACEATTEND AI")
    print("=" * 70)

    if initialize_database():

        print("Database initialized.")

    else:

        print("Database initialization failed.")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )