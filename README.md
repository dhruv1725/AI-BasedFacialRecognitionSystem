# FaceAttend AI — AI-Based Facial Recognition Attendance System

FaceAttend AI is an AI-powered facial recognition attendance system designed to automate student attendance using **face recognition, liveness detection, PostgreSQL, and a web-based dashboard**.

The system captures and registers student faces, generates facial embeddings using InsightFace, recognizes registered students through a camera, and automatically records attendance in a PostgreSQL database.

---

## 🚀 Features

### 🤖 AI Face Recognition

* Uses **InsightFace** for face detection and facial embeddings.
* Compares live face embeddings with registered face embeddings.
* Uses cosine similarity to determine identity.
* Configurable recognition threshold.
* Displays recognized student information in real time.

### 🛡️ Liveness Detection

* Includes a liveness-detection module to help distinguish a real person from a static image.
* Helps improve the reliability of automated attendance.

### 📸 Face Registration

* Register students using a browser camera.
* Captures multiple face samples.
* Generates and stores facial embeddings.
* Supports different face angles and expressions to improve recognition.

### 📝 Automated Attendance

* Automatically marks a recognized student as **Present**.
* Prevents duplicate attendance for the same student on the same day.
* Records:

  * Student ID
  * Attendance date
  * Attendance time
  * Attendance status

### 📊 Attendance Analytics

* Dashboard with attendance statistics.
* Attendance percentage calculation.
* Attendance period can be configured using a start date.
* Student-specific attendance information.
* Daily and historical attendance views.

### 👨‍🎓 Student Management

* View all registered students.
* View individual student details.
* View student-specific attendance history.

### 🗄️ PostgreSQL Database

The system uses PostgreSQL for storing:

* Student information
* Attendance records
* Attendance configuration

### 🌐 Web Interface

Built with Flask and HTML/CSS.

Main pages include:

* Dashboard
* Register Student
* Face Recognition
* Students
* Today's Attendance
* All Attendance
* Student Details

---

## 🏗️ Technology Stack

| Technology   | Purpose                            |
| ------------ | ---------------------------------- |
| Python       | Core programming language          |
| Flask        | Web application framework          |
| InsightFace  | Face recognition and embeddings    |
| ONNX Runtime | AI model inference                 |
| OpenCV       | Image and camera processing        |
| NumPy        | Numerical and embedding operations |
| PostgreSQL   | Database                           |
| psycopg2     | PostgreSQL connection              |
| HTML5        | Web interface                      |
| CSS3         | UI styling                         |
| JavaScript   | Browser camera and frontend logic  |
| Gunicorn     | Production WSGI server             |

---

## 📂 Project Structure

```text
AI-BasedFacialRecognitionSystem/
│
├── app/
│   ├── analytics/
│   │   └── analytics.py
│   │
│   ├── camera/
│   │   └── camera.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   └── schema.py
│   │
│   ├── liveness/
│   │   └── liveness.py
│   │
│   ├── recognition/
│   │   ├── face/
│   │   │   ├── embedding.py
│   │   │   └── register.py
│   │   └── recognize.py
│   │
│   ├── training/
│   │   └── train.py
│   │
│   └── main.py
│
├── attendance/
│   └── view_attendance.py
│
├── dataset/
│   └── faces/
│
├── test/
│   └── test_liveness.py
│
├── web/
│   ├── app.py
│   │
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   │
│   └── templates/
│       ├── all_attendance.html
│       ├── dashboard.html
│       ├── recognition.html
│       ├── register.html
│       ├── student_detail.html
│       ├── students.html
│       └── today_attendance.html
│
├── check_attendance.py
├── check_db.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ How It Works

```text
                 ┌─────────────────────┐
                 │     Student         │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Browser Camera      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Face Detection      │
                 │   InsightFace       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Liveness Detection  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Face Embedding      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Compare Embeddings  │
                 │ Cosine Similarity   │
                 └──────────┬──────────┘
                            │
                     Match Found?
                       /        \
                     Yes         No
                      │           │
                      ▼           ▼
              ┌────────────┐   Unknown
              │ Attendance │
              │   Present  │
              └─────┬──────┘
                    │
                    ▼
              ┌────────────┐
              │ PostgreSQL │
              └────────────┘
```

---

## 🧠 Face Recognition Process

During student registration:

```text
Student
   ↓
Camera
   ↓
Face Detection
   ↓
Multiple Face Samples
   ↓
Face Embeddings
   ↓
Stored Embeddings
```

During attendance:

```text
Live Camera
     ↓
Face Detection
     ↓
Face Embedding
     ↓
Compare with Registered Embeddings
     ↓
Similarity Score
     ↓
Recognized Student
     ↓
Attendance Database
```

---

## 🗄️ Database

The application uses PostgreSQL.

### Students

Stores registered student information.

```text
students
├── id
├── student_id
├── name
└── created_at
```

### Attendance

Stores attendance records.

```text
attendance
├── id
├── student_id
├── attendance_date
├── attendance_time
└── status
```

The database prevents duplicate attendance for the same student on the same date.

### Attendance Settings

Stores the configured attendance start date.

```text
attendance_settings
├── id
└── attendance_start_date
```

---

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/dhruv1725/AI-BasedFacialRecognitionSystem.git
```

```bash
cd AI-BasedFacialRecognitionSystem
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🐘 PostgreSQL Setup

Install PostgreSQL and create a database:

```text
facial-attendance
```

The application uses environment variables for database configuration.

### Local environment variables

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=facial-attendance
DB_USER=postgres
DB_PASSWORD=your_password
```

For production environments, the application can use:

```text
DATABASE_URL
```

Do **not** commit database passwords or other secrets to GitHub.

---

## ▶️ Running the Application

From the project root:

```powershell
python web\app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 📸 Register a Student

1. Open the web application.
2. Go to **Register Student**.
3. Enter:

   * Student ID
   * Student Name
4. Allow camera access.
5. The system captures multiple face samples.
6. Face embeddings are generated.
7. The student becomes available for recognition.

---

## 👤 Mark Attendance

1. Open **Recognition**.
2. Allow camera access.
3. Look toward the camera.
4. The system detects the face.
5. InsightFace generates the live embedding.
6. The embedding is compared with registered embeddings.
7. If a valid match is found, attendance is recorded.
8. Duplicate attendance for the same day is prevented.

---

## 📊 Attendance Analytics

The dashboard provides information such as:

* Total students
* Present students
* Attendance percentage
* Attendance period
* Student attendance history
* Daily attendance records

The attendance calculation uses the configured attendance start date.

---

## 🔐 Security Notes

This project processes biometric information, so deployment should be handled carefully.

Do not commit:

```text
.env
database passwords
face images
facial embeddings
private credentials
```

Use environment variables for sensitive configuration.

---

## 🚀 Deployment

The application can be deployed using a Python-compatible hosting platform.

Production server:

```bash
gunicorn web.app:app
```

Build command:

```bash
pip install -r requirements.txt
```

For production deployment, database credentials should be supplied through environment variables.

Face embeddings stored on a server filesystem also require persistent storage if registrations need to survive server restarts or redeployments.

---

## 🧪 Testing

The project includes testing code for liveness detection.

Run:

```powershell
python test\test_liveness.py
```

Database information can be checked using:

```powershell
python check_db.py
```

Attendance records can be inspected using:

```powershell
python check_attendance.py
```

---

## 🔮 Future Improvements

Possible future improvements include:

* Cloud/object storage for face embeddings
* Improved anti-spoofing
* Multi-camera support
* Role-based authentication
* Admin panel
* Email attendance reports
* CSV/PDF attendance export
* Advanced attendance analytics
* Notification system
* Mobile-friendly interface
* Recognition performance optimization
* Docker deployment
* Cloud-based AI inference

---

## 👨‍💻 Author

**Dhruv Kumar**

GitHub:
https://github.com/dhruv1725

---

## 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.
