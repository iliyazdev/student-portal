# 🎓 Student Portal — Academic Management & ML Performance Prediction Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-2.1.7-green.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-93.4%25%20Accuracy-orange.svg?logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML%20Pipeline-yellow.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%20%2F%20SQLite-4479A1.svg?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

> A centralized, role-based educational web ecosystem powered by **Django** and **Machine Learning (XGBoost & Gaussian Naive Bayes)** to automate institutional administration, streamline faculty-student communication, and accurately predict student academic trajectories for timely mentorship interventions.

---

## 📌 Table of Contents
- [Executive Overview](#-executive-overview)
- [The Problem vs The Solution](#-the-problem-vs-the-solution)
- [Key Features & Role Modules](#-key-features--role-modules)
  - [👑 Administrator Module](#-administrator-module)
  - [👨‍🏫 Faculty Module](#-faculty-module)
  - [🎓 Student Module](#-student-module)
- [🤖 Machine Learning Engine](#-machine-learning-engine)
- [🗄️ Database Architecture](#️-database-architecture)
- [📂 Project Directory Structure](#-project-directory-structure)
- [⚡ Quick Start & Installation](#-quick-start--installation)
- [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
- [🚀 Future Scope](#-future-scope)
- [👨‍💻 Author & Acknowledgments](#-author--acknowledgments)

---

## 📖 Executive Overview

Traditional collegiate environments often face communication fragmentation, slow manual attendance bookkeeping, and a critical absence of early academic warnings. 

The **Student Portal** bridges this gap by unifying **Students**, **Faculty**, and **Administrators** onto a high-performance web platform. In addition to digitizing daily academic workflows (attendance, study materials, assignments, marks, and feedback), it features a built-in **Predictive Machine Learning Pipeline** that evaluates historical attendance and examination trends to classify student performance as **Good**, **Fair**, or **Poor** with **93.4% accuracy** (using XGBoost).

---

## ⚖️ The Problem vs The Solution

| Challenge in Existing Systems | How Student Portal Solves It |
| :--- | :--- |
| **Manual Data Management:** Paper registers and disparate spreadsheets cause administrative delays and lost records. | **Unified Relational Cloud Database:** Real-time synchronized storage for marks, attendance, and credentials. |
| **No Early Warning System:** Marks are recorded only after exams; struggling students are caught too late. | **Proactive ML Prediction:** Predicts student trajectory weeks before semester finals to enable mentorship. |
| **Communication Gaps:** Students and teachers rely on informal or disconnected messaging channels. | **Built-in 2-Way Messaging:** Direct faculty-student communication with verified institutional audit trails. |
| **Scattered Study Materials:** Physical handouts and buried links hinder remote student study habits. | **Digital Course Repository:** 24/7 cloud repository for lecture slides, notes, syllabi, and assignment briefs. |

---

## ✨ Key Features & Role Modules

### 👑 Administrator Module
* **Faculty Provisioning:** Add, verify, edit, and deactivate faculty credentials and assigned teaching subjects.
* **Student Enrollment:** Manage student rosters by academic year, course stream, and roll number.
* **Institutional Governance:** Overview of departmental marks submission, system usage metrics, and audit logs.
* **Global Broadcasts:** Dispatch institution-wide academic announcements and schedule notices.

### 👨‍🏫 Faculty Module
* **Attendance Ledger:** Daily class attendance entry with instant automated percentage rollups.
* **Study Material Management:** Upload lecture notes, PDF guides, presentations, and reference documentation.
* **Assignment Engine:** Create assignments with submission guidelines, deadlines, and task criteria.
* **Marks & Grading Desk:** Submit internal examination marks, practical scores, and qualitative student feedback.
* **ML Student Performance Prediction:** Run automated ML model to predict whether a student's trajectory is `Good`, `Fair`, or `Poor` based on historical features.
* **Direct Messaging:** Respond to student inquiries and send direct parent/student updates.

### 🎓 Student Module
* **Academic Dashboard:** Clean at-a-glance overview of attendance health, registered subjects, and alerts.
* **Attendance Cutoff Tracker:** Real-time visibility into attendance percentage against mandatory 75% university thresholds.
* **Course Repository:** Download lecture notes and study guides uploaded by assigned professors.
* **Assignment Submission:** View active course assignments, task descriptions, and submission deadlines.
* **Semester Results:** Searchable examination scorecards with historical GPA progression.
* **Faculty Feedback:** Rate course instruction and submit confidential academic feedback.

---

## 🤖 Machine Learning Engine

The core predictive component trains on curated academic performance metrics (attendance rate, internal examination scores, prior performance indicators, and submission consistency) to classify students into actionable categories:

```
┌─────────────────────────────────┐
│ Student Academic History Data   │
│ (Attendance, Internal Marks)   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Feature Preprocessing Pipeline  │
│ (Min-Max Scaling, LabelEncoder) │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Machine Learning Classifiers    │
│ • XGBoost Classifier (93.4%)    │
│ • Gaussian Naive Bayes          │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Prediction Output Classification│
│ 🟢 Good  |  🟡 Fair  |  🔴 Poor │
└─────────────────────────────────┘
```

### Comparative Model Evaluation
* **XGBoost Classifier:** Achieved **93.4% accuracy**, delivering high precision in identifying students at academic risk.
* **Gaussian Naive Bayes:** Serves as a lightweight baseline probabilistic benchmark.

---

## 🗄️ Database Architecture

The system utilizes a structured relational database (MySQL / SQLite3). Primary schemas include:

* `faculty`: `(faculty_name, gender, contact_no, email, qualification, experience, teaching_subjects, username, password)`
* `student`: `(student_name, gender, contact_no, email, course, course_year, username, password)`
* `student_attendance`: `(student_name, faculty_name, attended_date)`
* `uploadmaterial`: `(faculty_name, material_name, description, filename, upload_date)`
* `marks`: `(student_name, faculty_name, course_name, course_year, subject_name, subject_marks, feedback, upload_date)`
* `assignments`: `(faculty_name, course_name, subject_name, course_year, assignment_task, description, assignment_date)`
* `messages`: `(sender_name, receiver_name, subject, message, message_date)`
* `feedback`: `(student_name, faculty_name, feedback, ratings, feedback_date)`
* `choosefaculty`: `(faculty_name, student_name, class_name)`

---

## 📂 Project Directory Structure

```text
Student Portal/
├── manage.py                     # Django management script
├── run.bat                       # 1-Click Windows execution script
├── requirements.txt              # Production Python package manifest
├── db.sqlite3                    # Local application database
├── README.md                     # Comprehensive project documentation
├── Documents/
│   ├── Student Portal.pdf        # Complete academic project report
│   ├── student Portal.pptx       # Slide deck presentation
│   ├── database.txt              # SQL schema definition file
│   └── requirements.txt          # Module requirement references
├── model/
│   ├── dataset.csv               # Student academic training dataset
│   └── data.npy                  # Preprocessed serialized matrix
├── Student/                      # Core Django Configuration
│   ├── settings.py               # Django application settings
│   ├── urls.py                   # Master routing configuration
│   ├── wsgi.py                   # WSGI web server interface
│   └── __init__.py
└── StudentApp/                   # Academic Portal Application
    ├── admin.py                  # Django administrative hooks
    ├── apps.py                   # App configuration
    ├── models.py                 # ORM models definition
    ├── views.py                  # Controllers, ML Pipeline & DB logic
    ├── urls.py                   # Application route bindings
    ├── static/                   # Static assets (CSS, JS, Images, Documents)
    │   ├── images/               # Portal graphics & icons
    │   └── files/                # Uploaded study materials & syllabus PDFs
    └── templates/                # HTML5 / Bootstrap Views
        ├── index.html            # Main landing & authentication screen
        ├── AdminScreen.html      # Administrator management console
        ├── FacultyScreen.html    # Faculty portal dashboard
        ├── StudentScreen.html    # Student interactive dashboard
        ├── AddAttendance.html    # Faculty attendance roster
        ├── AddMarks.html         # Grade recording screen
        ├── ViewProgress.html     # ML prediction analytics view
        ├── CreateAssignment.html # Assignment builder
        ├── UploadMaterial.html   # Study material uploader
        └── Messaging.html        # Two-way communication console
```

---

## ⚡ Quick Start & Installation

### Prerequisites
* **Python 3.8 to 3.12** installed on your system.
* **Git** installed on your system.
* (Optional) **MySQL Server** installed (e.g. via XAMPP or native service). The system includes support for local SQLite3 or MySQL.

### Step 1: Clone the Repository
```bash
git clone https://github.com/iliyazdev/student-portal.git
cd student-portal
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
If using MySQL, create the database:
```sql
CREATE DATABASE portal_db;
```
*(Verify your connection parameters in `StudentApp/views.py` or `Student/settings.py`)*

### Step 5: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Start the Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser to access the portal.

---

## 🧪 Testing & Quality Assurance

Comprehensive verification strategies applied across the portal modules:
* **Unit Testing:** Individual verification of database connection helpers and ML feature encoders.
* **Functional & Role Testing:** Verified access separation across Admin, Faculty, and Student roles.
* **Black-Box Testing:** Validation of form inputs, duplicate record handling, and file upload size caps.
* **ML Inference Validation:** Stress-tested edge cases on missing attendance data to confirm graceful fallbacks.

---

## 🚀 Future Scope

* **Biometric & RFID Sync:** Automated integration with classroom hardware for touchless attendance.
* **Deep Learning Integration:** Continuous recurrent neural networks (LSTM) to track semester-by-semester student trajectories.
* **Mobile App Extension:** Dedicated cross-platform Flutter/React Native application for mobile push notifications.
* **Plagiarism Scanner:** Automatic inspection of submitted student assignment files.

---

## 👨‍💻 Author & Acknowledgments

* **Shaik Iliyaz** — *Lead UI/UX Designer & Full-Stack Developer*
  * GitHub: [@iliyazdev](https://github.com/iliyazdev)
  * Portfolio: [Iliyaz Portfolio](https://github.com/iliyazdev)

Developed as a comprehensive academic project for higher-education institutions, demonstrating modern human-centered educational software engineering.

