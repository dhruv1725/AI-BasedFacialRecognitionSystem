# FaceAttend AI — AI-Based Facial Recognition Attendance System

FaceAttend AI is an AI-powered facial recognition attendance system built with Python, Flask, InsightFace, OpenCV, and PostgreSQL.

The system allows students to register their faces, recognize registered students through a camera, automatically mark attendance, and view attendance analytics through a web interface.

---

## 🚀 Features

### 🤖 AI Facial Recognition

* Uses InsightFace for face detection and recognition.
* Generates facial embeddings for registered students.
* Uses cosine similarity to compare faces.
* Supports multiple face samples for better recognition.

### 🛡️ Liveness Detection

* Helps distinguish a live person from a static image.
* Adds an additional security layer to the attendance process.

### 📸 Face Registration

* Register students using a webcam.
* Captures multiple face samples.
* Generates and stores face embeddings.
* Supports different face angles and samples.

### ✅ Automated Attendance

* Automatically marks recognized students as Present.
* Prevents duplicate attendance for the same student on the same day.
* Stores attendance date and time in PostgreSQL.

### 📊 Attendance Analytics

* Attendance percentage calculation.
* Attendance history.
* Attendance statistics from a configurable attendance start date.
* Student-specific attendance information.

### 👨‍🎓 Student Management

* View registered students.
* View individual student details.
* View student attendance records.

### 🗄️ PostgreSQL Database

Stores:

* Student information
* Attendance records
* Attendance settings

### 🌐 Web Interface

Built using:

* Flask
* HTML
* CSS
* JavaScript

---

## 🛠️ Technology Stack

| Technology   | Purpose                        |
| ------------ | ------------------------------ |
| Python       | Backend development            |
| Flask        | Web application                |
| InsightFace  | Face recognition               |
| ONNX Runtime | AI model execution             |
| OpenCV       | Camera and image processing    |
| NumPy        | Numerical operations           |
| PostgreSQL   | Database                       |
| psycopg2     | PostgreSQL connection          |
| HTML5        | Web pages                      |
| CSS3         | User interface                 |
| JavaScript   | Browser camera and interaction |
| Gunicorn     | Production server              |

---

## 📁 Project Structure

```text
AI-BasedFacialRecognitionSystem/
│
├── app/
│   ├── analytics/
│   ├── camera/
│   ├── database/
│   ├── liveness/
│   ├── recognition/
│   │   ├── face/
│   │   │   ├── embedding.py
│   │   │   └── register.py
│   │   └── recognize.py
│   ├── training/
│   │   └── train.py
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

## 🔄 How the System Works

```text
Student Registration
        ↓
Capture Face Samples
        ↓
Generate Face Embeddings
        ↓
Store Student + Embeddings
        ↓
Open Recognition Page
        ↓
Detect Face
        ↓
Generate Current Face Embedding
        ↓
Compare With Registered Embeddings
        ↓
Recognize Student
        ↓
Check Attendance
        ↓
Mark Present
        ↓
Store Attendance in PostgreSQL
        ↓
Display Analytics
```

---

## 🧠 Face Recognition Process

FaceAttend AI uses InsightFace to generate numerical representations called **face embeddings**.

During registration:

```text
Camera
   ↓
Face Detection
   ↓
Face Embedding
   ↓
Save Embedding
```

During recognition:

```text
Camera
   ↓
Face Detection
   ↓
Generate Embedding
   ↓
Compare With Registered Embeddings
   ↓
Calculate Similarity
   ↓
Recognized / Unknown
```

Cosine similarity is used to compare the current face embedding with registered face embeddings.

---

## 🗄️ Database

The application uses PostgreSQL.

### Students Table

Stores registered student information.

```text
students
├── id
├── student_id
├── name
└── created_at
```

### Attendance Table

Stores daily attendance.

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

Stores the attendance calculation start date.

```text
attendance_settings
├── id
└── attendance_start_date
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/dhruv1725/AI-BasedFacialRecognitionSystem.git
cd AI-BasedFacialRecognitionSystem
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```powershell
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄️ PostgreSQL Configuration

The application uses environment variables for database credentials.

Set:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Example for PowerShell:

```powershel
```
