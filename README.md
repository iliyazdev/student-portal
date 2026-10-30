# 🎓 Student Portal

<p align="center">
  <strong>A modern academic management platform with ML-powered student performance prediction.</strong>
</p>

<p align="center">
  <a href="https://iliyaz.me"><img src="https://img.shields.io/badge/Portfolio-iliyaz.me-6366f1?style=for-the-badge&logo=safari&logoColor=white" alt="Portfolio" /></a>
  <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-2.1+-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://xgboost.readthedocs.io/"><img src="https://img.shields.io/badge/XGBoost-93.4%25%20Accuracy-FF6600?style=for-the-badge&logo=xgboost&logoColor=white" alt="XGBoost" /></a>
  <a href="https://www.mysql.com/"><img src="https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-00758F?style=for-the-badge&logo=mysql&logoColor=white" alt="Database" /></a>
</p>

<p align="center">
  <img src="assets/hero_3d_banner.png" alt="Student Portal 3D Experience" width="820" />
</p>

---

## 💡 Why I Built This

During college, our everyday academic activities were scattered across paper notebooks, random WhatsApp groups, and physical bulletin boards. 

* **Attendance took too long:** Teachers spent 15 minutes of every 50-minute class calling roll numbers out of paper registers.
* **Study materials were easily lost:** Lecture slides and notes were shared through group chats and buried under messages.
* **Academic help arrived too late:** Semester marks were only calculated at the very end of term. If a student was falling behind, neither teachers nor parents knew until exam results were published—when it was already too late to catch up.

I built **Student Portal** to solve all three problems in one place. It gives students, faculty, and administrators a single, easy-to-use web app for attendance, study materials, assignments, and grades—and includes an **XGBoost machine learning model** that flags academic risk early in the semester so faculty can step in and help.

---

## 🚀 Key Features

### 🎓 For Students
* **Live Attendance Tracker:** Check real-time attendance percentage anytime and see exactly where you stand against the mandatory 75% cutoff.
* **Course Study Materials:** Download lecture slides, PDFs, and notes uploaded by professors 24/7.
* **Assignments & Deadlines:** See upcoming tasks, project requirements, and submission dates in one spot.
* **Exam Results:** Instant access to internal marks and semester scorecards.
* **Direct Messaging:** Send private questions to professors without needing informal social apps.

### 👩‍🏫 For Faculty
* **Fast Roster Attendance:** Entire class attendance in under 45 seconds—all students default to *Present*, teachers just tap absentees and hit save.
* **Upload Study Materials:** Share notes, syllabus sheets, and PDFs with all enrolled students instantly.
* **Assignment Management:** Post assignments with descriptions, deadlines, and requirements.
* **Marks & Feedback:** Enter internal exam marks and leave individual student feedback.
* **ML Risk Evaluation:** Run the predictive engine to identify students who may need academic guidance early.

### 👨‍💼 For Administrators
* **Manage Teachers & Students:** Create accounts, assign teaching subjects, and manage departmental student rosters.
* **Campus Announcements:** Post official notices and exam dates to the portal dashboard.
* **System Overview:** View department-wide marks submission status and system records.

---

## 🤖 How the Machine Learning Prediction Works

Instead of waiting for semester finals to see who is struggling, the portal uses machine learning to assess academic risk while there is still time to help.

```
  Student Attendance %  ──┐
                          ├──►  [ Feature Preprocessing ]  ──►  [ XGBoost Model ]  ──►  🟢 Good  (On Track)
  Internal Test Scores  ──┘                                                             🟡 Fair  (Needs Review)
                                                                                        🔴 Poor  (At Risk - Early Help)
```

* **Algorithm:** **XGBoost Classifier** (Gradient Boosted Decision Trees), benchmarked against Gaussian Naive Bayes.
* **Model Accuracy:** **93.4%** on academic trajectory test data.
* **Why it matters:** It shifts academic support from reactive (failing at finals) to proactive (early faculty mentorship weeks before exams).

---

## 📥 Project Documents & Downloads

All official project documentation and presentation assets are included directly in this repository:

| Document | Format | Description | Link |
|:---|:---:|:---|:---:|
| **Project Report** | 📄 PDF | Full 72-page official project report covering System Architecture, Data Flow Diagrams (DFD), UML Design, Test Cases, and ML Results. | [Download PDF](./Documents/Student%20Portal.pdf) |
| **Presentation Deck** | 📊 PPTX | Official 31-slide defense and viva slide deck. | [Download PPTX](./Documents/student%20Portal.pptx) |
| **Database Schema** | 🗄️ SQL | Complete SQL schema definitions for all 9 relational tables. | [View Schema](./Documents/database.txt) |

---

## 🛠️ Tech Stack

| Layer | Tools & Libraries |
|:---|:---|
| **Backend** | Python 3, Django 2.1+ |
| **Machine Learning** | XGBoost, Scikit-learn, Pandas, NumPy |
| **Database** | MySQL / SQLite3 |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Version Control** | Git, GitHub |

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/iliyazdev/student-portal.git
cd student-portal
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database setup & start server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

### 5. Default Credentials
* **Admin Portal:** `admin` / `admin`
* **Faculty & Student:** Provisioned through Admin Dashboard or direct registration.

---

## 📁 Repository Structure

```text
student-portal/
├── manage.py                     # Django management script
├── requirements.txt              # Python package requirements
├── run.bat                       # 1-click Windows start script
├── db.sqlite3                    # Local development database
├── assets/                       # Screenshots and visual banners
├── Documents/
│   ├── Student Portal.pdf        # Full project documentation report
│   ├── student Portal.pptx       # Presentation slide deck
│   └── database.txt              # SQL schema definition
├── model/
│   ├── dataset.csv               # Student academic training dataset
│   └── data.npy                  # Preprocessed feature matrix
├── Student/                      # Django project configuration (settings, URLs)
└── StudentApp/                   # Core portal app (views, models, templates, static)
```

---

## 👨‍💻 Author

**Shaik Iliyaz**  
UI/UX Designer & Full-Stack Developer  
* 🌐 Portfolio: **[iliyaz.me](https://iliyaz.me)**  
* 🐙 GitHub: **[@iliyazdev](https://github.com/iliyazdev)**  

---

<p align="center">
  <sub>Built with ❤️ by Shaik Iliyaz • <a href="https://iliyaz.me">iliyaz.me</a></sub>
</p>
