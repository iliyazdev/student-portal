from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os
import io
import base64
import smtplib
import pymysql
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Prevents Matplotlib GUI errors on headless servers
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
from contextlib import contextmanager

# ==========================================
# DATABASE CONNECTION & HELPER
# ==========================================

def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='portal_db',
        charset='utf8'
    )

@contextmanager
def get_db_cursor():
    """Context manager to guarantee DB connections are always closed and freed."""
    con = get_db_connection()
    try:
        with con.cursor() as cur:
            yield cur, con
    finally:
        con.close()


# ==========================================
# MACHINE LEARNING PIPELINE
# ==========================================

dataset_path = os.path.join(settings.BASE_DIR, "model", "dataset.csv")
dataset = pd.read_csv(dataset_path)

le = LabelEncoder()
dataset['FinalResult'] = le.fit_transform(dataset['FinalResult'].astype(str))
labels = le.classes_

Y = dataset['FinalResult'].to_numpy()
X = dataset.drop(columns=['FinalResult']).to_numpy()

sc = MinMaxScaler()
X = sc.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

data_npy_path = os.path.join(settings.BASE_DIR, "model", "data.npy")
if os.path.exists(data_npy_path):
    data = np.load(data_npy_path, allow_pickle=True)
    if len(data) == 4:
        X_train, X_test, y_train, y_test = data

# Train Naive Bayes
nb_cls = GaussianNB()
nb_cls.fit(X_train, y_train)
predict_nb = nb_cls.predict(X_test)

# Train XGBoost safely without deprecated arguments
xg_cls = XGBClassifier(eval_metric='mlogloss')
xg_cls.fit(X_train, y_train)
predict_xg = xg_cls.predict(X_test)

# Cache structured metrics (idempotent, thread-safe)
ml_metrics = [
    {
        'name': 'Naive Bayes',
        'accuracy': round(accuracy_score(y_test, predict_nb) * 100, 2),
        'precision': round(precision_score(y_test, predict_nb, average='macro', zero_division=0) * 100, 2),
        'recall': round(recall_score(y_test, predict_nb, average='macro', zero_division=0) * 100, 2),
        'fscore': round(f1_score(y_test, predict_nb, average='macro', zero_division=0) * 100, 2),
    },
    {
        'name': 'XGBoost',
        'accuracy': round(accuracy_score(y_test, predict_xg) * 100, 2),
        'precision': round(precision_score(y_test, predict_xg, average='macro', zero_division=0) * 100, 2),
        'recall': round(recall_score(y_test, predict_xg, average='macro', zero_division=0) * 100, 2),
        'fscore': round(f1_score(y_test, predict_xg, average='macro', zero_division=0) * 100, 2),
    }
]

print("ML Training completed successfully")


def runML(marks):
    """Predict performance category based on marks using trained XGBoost."""
    global xg_cls, sc, labels
    try:
        feature_count = sc.n_features_in_
        data_row = [marks] + [0.0] * (feature_count - 1)
        data_arr = np.array([data_row])
        data_arr = sc.transform(data_arr)
        predict = xg_cls.predict(data_arr)[0]
        return labels[predict]
    except Exception as e:
        print(f"ML Prediction Error: {e}")
        return "Prediction Error"


def getClassMembers(faculty, subject):
    count = 0
    with get_db_cursor() as (cur, con):
        cur.execute("SELECT count(faculty_name) FROM choosefaculty WHERE faculty_name=%s AND class_name=%s", (faculty, subject))
        row = cur.fetchone()
        if row:
            count = row[0]
    return count


def getSubject(faculty):
    subject = ""
    with get_db_cursor() as (cur, con):
        cur.execute("SELECT teaching_subjects FROM faculty WHERE username=%s", (faculty,))
        row = cur.fetchone()
        if row and row[0]:
            subject = row[0]
    return subject


def getEmail(sname):
    email = ""
    with get_db_cursor() as (cur, con):
        cur.execute("SELECT email FROM student WHERE username=%s", (sname,))
        row = cur.fetchone()
        if row and row[0]:
            email = row[0]
    return email


def sendMail(subject, msg, email):
    """Safely send email with timeout to prevent blocking worker threads."""
    if not email:
        return False
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=5) as connection:
            email_address = os.environ.get('PORTAL_EMAIL', 'kaleem202120@gmail.com')
            email_password = os.environ.get('PORTAL_EMAIL_PWD', 'xyljzncebdxcubjq')
            connection.login(email_address, email_password)
            connection.sendmail(from_addr=email_address, to_addrs=[email], msg=f"Subject: {subject}\n\n{msg}")
        return True
    except Exception as e:
        print("Mail Send Exception (suppressed):", e)
        return False


# ==========================================
# PUBLIC & HOME VIEWS
# ==========================================

def index(request):
    """Home view featuring hero carousel."""
    return render(request, 'index.html', {})


def Logout(request):
    """Flushes session and securely logs out user."""
    request.session.flush()
    return redirect('index')


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

def AdminLogin(request):
    return render(request, 'AdminLogin.html', {})


def FacultyLogin(request):
    return render(request, 'FacultyLogin.html', {})


def StudentLogin(request):
    return render(request, 'StudentLogin.html', {})


def AdminLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()
        if username == 'admin' and password == 'admin':
            request.session['uname'] = username
            request.session['role'] = 'admin'
            context = {'data': f'Welcome Administrator, {username}!'}
            return render(request, 'AdminScreen.html', context)
        else:
            return render(request, 'AdminLogin.html', {'data': 'Invalid Admin username or password.'})
    return redirect('AdminLogin')


def FacultyLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()

        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, faculty_name FROM faculty WHERE username=%s AND password=%s", (username, password))
            row = cur.fetchone()

            if row:
                request.session['uname'] = username
                request.session['role'] = 'faculty'
                context = {'data': f'Welcome Teacher, {row[1]}!'}
                return render(request, 'FacultyScreen.html', context)
            else:
                return render(request, 'FacultyLogin.html', {'data': 'Invalid username or password.'})
    return redirect('FacultyLogin')


def StudentLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()

        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, student_name FROM student WHERE username=%s AND password=%s", (username, password))
            row = cur.fetchone()

            if row:
                request.session['uname'] = username
                request.session['role'] = 'student'
                context = {'data': f'Welcome Student, {row[1]}!'}
                return render(request, 'StudentScreen.html', context)
            else:
                return render(request, 'StudentLogin.html', {'data': 'Invalid username or password.'})
    return redirect('StudentLogin')


# ==========================================
# ADMIN VIEWS
# ==========================================

def AddFaculty(request):
    return render(request, 'AddFaculty.html', {})


def AddStudent(request):
    return render(request, 'AddStudent.html', {})


def AddFacultyAction(request):
    if request.method == 'POST':
        faculty = request.POST.get('t1', '').strip()
        gender = request.POST.get('t2', '').strip()
        contact = request.POST.get('t3', '').strip()
        email = request.POST.get('t4', '').strip()
        qualification = request.POST.get('t5', '').strip()
        experience = request.POST.get('t6', '').strip()
        teaching = request.POST.get('t7', '').strip()
        username = request.POST.get('t8', '').strip()
        password = request.POST.get('t9', '').strip()

        try:
            with get_db_cursor() as (cur, con):
                cur.execute("SELECT username FROM faculty WHERE username=%s", (username,))
                if cur.fetchone():
                    status = "Username already exists. Please choose another username."
                else:
                    query = """
                        INSERT INTO faculty (faculty_name, gender, contact_no, email, qualification, experience, teaching_subjects, username, password) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(query, (faculty, gender, contact, email, qualification, experience, teaching, username, password))
                    con.commit()
                    status = "Faculty details added successfully!"
        except Exception as e:
            status = f"Database Error: {str(e)}"

        return render(request, 'AddFaculty.html', {'data': status})
    return redirect('AddFaculty')


def AddStudentAction(request):
    if request.method == 'POST':
        student = request.POST.get('t1', '').strip()
        gender = request.POST.get('t2', '').strip()
        contact = request.POST.get('t3', '').strip()
        email = request.POST.get('t4', '').strip()
        course = request.POST.get('t5', '').strip()
        year = request.POST.get('t6', '').strip()
        username = request.POST.get('t7', '').strip()
        password = request.POST.get('t8', '').strip()

        try:
            with get_db_cursor() as (cur, con):
                cur.execute("SELECT username FROM student WHERE username = %s", (username,))
                if cur.fetchone():
                    status = "Username already exists. Please choose another username."
                else:
                    query = """
                        INSERT INTO student (student_name, gender, contact_no, email, course, course_year, username, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(query, (student, gender, contact, email, course, year, username, password))
                    con.commit()
                    status = "Student details added successfully!"
        except Exception as e:
            status = f"Database Error: {str(e)}"

        return render(request, 'AddStudent.html', {'data': status})
    return redirect('AddStudent')


def ViewFaculty(request):
    if request.method == 'GET':
        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Faculty Name</th>
                    <th>Gender</th>
                    <th>Contact No</th>
                    <th>Email ID</th>
                    <th>Qualification</th>
                    <th>Experience</th>
                    <th>Teaching Subject</th>
                    <th>Username</th>
                    <th>Password</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT * FROM faculty")
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='9' style='text-align:center;padding:20px;'>No faculty members registered yet.</td></tr>"
            for row in rows:
                output += f"""
                    <tr>
                        <td><strong>{row[0]}</strong></td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                        <td>{row[3]}</td>
                        <td>{row[4]}</td>
                        <td>{row[5]}</td>
                        <td><span class="badge badge-info">{row[6]}</span></td>
                        <td><code>{row[7]}</code></td>
                        <td><code>{row[8]}</code></td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'AdminScreen.html', {'data': output})


def ViewStudent(request):
    if request.method == 'GET':
        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Student Name</th>
                    <th>Gender</th>
                    <th>Contact No</th>
                    <th>Email ID</th>
                    <th>Course</th>
                    <th>Year</th>
                    <th>Username</th>
                    <th>Password</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT * FROM student")
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='8' style='text-align:center;padding:20px;'>No students registered yet.</td></tr>"
            for row in rows:
                output += f"""
                    <tr>
                        <td><strong>{row[0]}</strong></td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                        <td>{row[3]}</td>
                        <td><span class="badge badge-info">{row[4]}</span></td>
                        <td><span class="badge badge-primary">{row[5]}</span></td>
                        <td><code>{row[6]}</code></td>
                        <td><code>{row[7]}</code></td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'AdminScreen.html', {'data': output})


def SchoolPerformance(request):
    if request.method == 'GET':
        scores = []
        labels = []

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Teacher Name</th>
                    <th>Average Students Performance Grade</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT faculty_name, avg(subject_marks) FROM marks GROUP BY faculty_name")
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='2' style='text-align:center;padding:20px;'>No marks records found yet to compute performance.</td></tr>"
            for row in rows:
                scores.append(float(row[1]))
                labels.append(row[0])
                output += f'<tr><td><strong>{row[0]}</strong></td><td><strong>{float(row[1]):.2f}%</strong></td></tr>'
        output += "</tbody></table></div>"

        scores = np.asarray(scores)
        labels = np.asarray(labels)

        plt.figure(figsize=(6, 6))
        if len(scores) > 0 and np.sum(scores) > 0:
            colors = sns.color_palette('pastel')[0:len(scores)]
            plt.pie(scores, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
            plt.title("Teacher's Effectiveness Based on Student Performance Grades", fontsize=12, pad=15)
        else:
            plt.title("No Performance Data Available Yet", fontsize=12)
            plt.text(0.5, 0.5, "No marks data recorded yet", horizontalalignment='center', verticalalignment='center')
            plt.axis('off')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()

        img_b64 = base64.b64encode(buf.getvalue()).decode()
        return render(request, 'AdminScreen.html', {'data': output, 'img': img_b64})


# ==========================================
# STUDENT VIEWS
# ==========================================

def StudentScreen(request):
    uname = request.session.get('uname')
    if not uname:
        return redirect('StudentLogin')
    return render(request, 'StudentScreen.html', {})


def ChooseFaculty(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Faculty Name</th>
                    <th>Teaching Subject</th>
                    <th>Average Rating</th>
                    <th>Latest Feedback</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("""
                SELECT f.username, f.faculty_name, f.teaching_subjects,
                       COALESCE(AVG(CAST(fb.ratings AS DECIMAL(4,2))), 0) as avg_rating,
                       (SELECT feedback FROM feedback WHERE faculty_name = f.username ORDER BY feedback_date DESC LIMIT 1) as latest_fb
                FROM faculty f
                LEFT JOIN feedback fb ON f.username = fb.faculty_name
                GROUP BY f.username, f.faculty_name, f.teaching_subjects
            """)
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='5' style='text-align:center;padding:20px;'>No faculty registered in the system.</td></tr>"
            for row in rows:
                avg_rate = f"⭐ {float(row[3]):.1f} / 5" if row[3] > 0 else "<span style='color:var(--text-muted);'>No ratings yet</span>"
                fb_text = row[4] if row[4] else "<span style='color:var(--text-muted);'>No feedback yet</span>"
                output += f"""
                    <tr>
                        <td><strong>{row[1]}</strong> ({row[0]})</td>
                        <td><span class="badge badge-info">{row[2]}</span></td>
                        <td>{avg_rate}</td>
                        <td>{fb_text}</td>
                        <td>
                            <a href="/auto-faculty-selection/?name={row[0]}&subject={row[2]}" class="btn-choose">
                                <i class="fas fa-check"></i> Choose Faculty
                            </a>
                        </td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'FacultySuggestion.html', {'data': output})


def FacultySuggestion(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Faculty Name</th>
                    <th>Teaching Subject</th>
                    <th>Student Performance Average</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("""
                SELECT f.username, f.faculty_name, f.teaching_subjects,
                       COALESCE(AVG(m.subject_marks), 0) as avg_marks
                FROM faculty f
                LEFT JOIN marks m ON f.username = m.faculty_name
                GROUP BY f.username, f.faculty_name, f.teaching_subjects
            """)
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='4' style='text-align:center;padding:20px;'>No faculty available yet.</td></tr>"
            for row in rows:
                perf = f"{float(row[3]):.1f}%" if row[3] > 0 else "<span style='color:var(--text-muted);'>No marks data yet</span>"
                output += f"""
                    <tr>
                        <td><strong>{row[1]}</strong> ({row[0]})</td>
                        <td><span class="badge badge-info">{row[2]}</span></td>
                        <td><strong>{perf}</strong></td>
                        <td>
                            <a href="/auto-faculty-selection/?name={row[0]}&subject={row[2]}" class="btn-choose">
                                <i class="fas fa-user-plus"></i> Select Faculty
                            </a>
                        </td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'FacultySuggestion.html', {'data': output})


def AutoFacultySelection(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        faculty = request.GET.get('name', '').strip()
        subject = request.GET.get('subject', '').strip()

        status = "Error processing request."
        try:
            with get_db_cursor() as (cur, con):
                cur.execute("SELECT faculty_name FROM choosefaculty WHERE student_name=%s AND class_name=%s", (uname, subject))
                existing = cur.fetchone()
                if existing:
                    status = f"You have already selected faculty '{existing[0]}' for subject '{subject}'."
                else:
                    members_count = getClassMembers(faculty, subject)
                    if members_count >= 60:
                        status = "Slot limit reached for this faculty (60 members). Please try another teacher."
                    else:
                        cur.execute("INSERT INTO choosefaculty (faculty_name, student_name, class_name) VALUES(%s, %s, %s)", (faculty, uname, subject))
                        con.commit()
                        status = f"You have been successfully assigned to faculty '{faculty}' for '{subject}'!"
        except Exception as e:
            status = f"Database Error: {str(e)}"

        return render(request, 'StudentScreen.html', {'data': status})


def Feedback(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = '<tr><td><font size="3" color="black"><b>Choose Faculty</b></td>'
        output += '<td><select name="t1">'
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, faculty_name FROM faculty")
            rows = cur.fetchall()
            for row in rows:
                output += f'<option value="{row[0]}">{row[1]} ({row[0]})</option>'
        output += "</select></td></tr>"
        return render(request, 'Feedback.html', {'data1': output})


def FeedbackAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        faculty = request.POST.get('t1', '').strip()
        feedback = request.POST.get('t2', '').strip()
        rating = request.POST.get('t3', '').strip()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with get_db_cursor() as (cur, con):
                cur.execute("INSERT INTO feedback VALUES(%s, %s, %s, %s, %s)", (uname, faculty, feedback, rating, current_datetime))
                con.commit()
                status = "Your feedback has been successfully submitted!"
        except Exception as e:
            status = f"Error submitting feedback: {str(e)}"

        return render(request, 'StudentScreen.html', {'data': status})
    return redirect('Feedback')


def ViewMarks(request):
    uname = request.session.get('uname')
    if not uname:
        return redirect('StudentLogin')
    return render(request, 'ViewMarks.html', {})


def ViewMarksAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        course = request.POST.get('t1', '').strip()
        year = request.POST.get('t2', '').strip()
        total = 0
        count = 0

        with get_db_cursor() as (cur, con):
            cur.execute("SELECT subject_name, subject_marks FROM marks WHERE student_name=%s AND course_year=%s AND course_name=%s", (uname, year, course))
            rows = cur.fetchall()

            if not rows:
                output = f"<div class='alert-message error'><i class='fas fa-info-circle'></i> No marks records found for Course: <b>{course}</b>, Year: <b>{year}</b>.</div>"
            else:
                output = """
                <div class="table-container">
                <table class="styled-table">
                    <thead>
                        <tr>
                            <th>Subject Name</th>
                            <th>Obtained Marks</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for row in rows:
                    output += f'<tr><td><strong>{row[0]}</strong></td><td>{row[1]}</td></tr>'
                    total += float(row[1])
                    count += 1

                avg_gpa = total / count if count > 0 else 0
                feedback_ml = runML(avg_gpa)
                badge_class = "badge-success" if feedback_ml == "Good" else ("badge-warning" if feedback_ml == "Fair" else "badge-danger")

                output += f"""
                    </tbody>
                    <tfoot>
                        <tr class="summary-row"><td><strong>Total Marks</strong></td><td><strong>{total:.1f}</strong></td></tr>
                        <tr class="summary-row"><td><strong>Average Percentage / GPA</strong></td><td><strong>{avg_gpa:.2f}%</strong></td></tr>
                        <tr class="summary-row highlight">
                            <td><strong>Machine Learning Performance Prediction</strong></td>
                            <td><span class="badge {badge_class}">{feedback_ml}</span></td>
                        </tr>
                    </tfoot>
                </table>
                </div>
                """

        return render(request, 'StudentScreen.html', {'data': output})
    return redirect('ViewMarks')


def ViewMessages(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Teacher Name</th>
                    <th>Subject</th>
                    <th>Message</th>
                    <th>Date Received</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT * FROM messages WHERE receiver_name=%s ORDER BY message_date DESC", (uname,))
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='4' style='text-align:center;padding:25px;'>No messages in your inbox.</td></tr>"
            for row in rows:
                output += f"""
                    <tr>
                        <td><strong>{row[0]}</strong></td>
                        <td><strong>{row[2]}</strong></td>
                        <td>{row[3]}</td>
                        <td><small>{row[4]}</small></td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'StudentScreen.html', {'data': output})


def DownloadMaterials(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Faculty Name</th>
                    <th>Material Name</th>
                    <th>Description</th>
                    <th>Filename</th>
                    <th>Upload Date</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT * FROM uploadmaterial ORDER BY upload_date DESC")
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='6' style='text-align:center;padding:25px;'>No study materials uploaded yet.</td></tr>"
            for row in rows:
                output += f"""
                    <tr>
                        <td><strong>{row[0]}</strong></td>
                        <td><strong>{row[1]}</strong></td>
                        <td>{row[2]}</td>
                        <td><code>{row[3]}</code></td>
                        <td><small>{row[4]}</small></td>
                        <td>
                            <a href="/download-material-action/?name={row[3]}" class="btn-download">
                                <i class="fas fa-download"></i> Download
                            </a>
                        </td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'StudentScreen.html', {'data': output})


def DownloadMaterialAction(request):
    if request.method == 'GET':
        filename = request.GET.get('name', '')
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        file_path = os.path.join(settings.BASE_DIR, "StudentApp", "static", "files", filename)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                content = file.read()
            response = HttpResponse(content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse("Requested file not found on the server.", status=404)


def StudentMessaging(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = '<tr><td><font size="3" color="black"><b>Choose Teacher Name</b></td>'
        output += '<td><select name="sname">'
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, faculty_name FROM faculty")
            rows = cur.fetchall()
            for row in rows:
                output += f'<option value="{row[0]}">{row[1]} ({row[0]})</option>'
        output += "</select></td></tr>"
        return render(request, 'StudentMessaging.html', {'data1': output})


def StudentMessagingAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        fname = request.POST.get('sname', '').strip()
        subject = request.POST.get('t1', '').strip()
        message = request.POST.get('t2', '').strip()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with get_db_cursor() as (cur, con):
                cur.execute("INSERT INTO messages VALUES(%s, %s, %s, %s, %s)", (uname, fname, subject, message, current_datetime))
                con.commit()
                status = f"Message successfully sent to teacher '{fname}'!"
        except Exception as e:
            status = f"Error sending message: {str(e)}"

        return render(request, 'StudentScreen.html', {'data': status})
    return redirect('StudentMessaging')


def ViewAssignments(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('StudentLogin')

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Faculty Name</th>
                    <th>Course</th>
                    <th>Subject</th>
                    <th>Year</th>
                    <th>Assignment Task</th>
                    <th>Description</th>
                    <th>Due Date</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT * FROM assignments ORDER BY assignment_date DESC")
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='7' style='text-align:center;padding:25px;'>No assignments posted yet.</td></tr>"
            for row in rows:
                output += f"""
                    <tr>
                        <td><strong>{row[0]}</strong></td>
                        <td><span class="badge badge-info">{row[1]}</span></td>
                        <td>{row[2]}</td>
                        <td><span class="badge badge-primary">{row[3]}</span></td>
                        <td><strong>{row[4]}</strong></td>
                        <td>{row[5]}</td>
                        <td><span class="badge badge-warning">{row[6]}</span></td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'StudentScreen.html', {'data': output})


# ==========================================
# FACULTY VIEWS
# ==========================================

def FacultyScreen(request):
    uname = request.session.get('uname')
    if not uname:
        return redirect('FacultyLogin')
    return render(request, 'FacultyScreen.html', {})


def ViewStudentMessages(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        output = """
        <div class="table-container">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Student Name</th>
                    <th>Subject</th>
                    <th>Message</th>
                    <th>Date Received</th>
                </tr>
            </thead>
            <tbody>
        """
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT * FROM messages WHERE receiver_name=%s ORDER BY message_date DESC", (uname,))
            rows = cur.fetchall()
            if not rows:
                output += "<tr><td colspan='4' style='text-align:center;padding:25px;'>No student messages in your inbox.</td></tr>"
            for row in rows:
                output += f"""
                    <tr>
                        <td><strong>{row[0]}</strong></td>
                        <td><strong>{row[2]}</strong></td>
                        <td>{row[3]}</td>
                        <td><small>{row[4]}</small></td>
                    </tr>
                """
        output += "</tbody></table></div>"
        return render(request, 'FacultyScreen.html', {'data': output})


def ViewProgressReport(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        output = '<tr><td><font size="3" color="black"><b>Choose Student Name</b></td>'
        output += '<td><select name="sname">'
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, student_name FROM student")
            rows = cur.fetchall()
            for row in rows:
                output += f'<option value="{row[0]}">{row[1]} ({row[0]})</option>'
        output += "</select></td></tr>"
        return render(request, 'ViewProgressReport.html', {'data1': output})


def ViewProgressReportAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        sname = request.POST.get('sname', '').strip()
        course = request.POST.get('t1', '').strip()
        year = request.POST.get('t2', '').strip()
        total = 0
        count = 0

        with get_db_cursor() as (cur, con):
            cur.execute("SELECT subject_name, subject_marks FROM marks WHERE student_name=%s AND course_year=%s AND course_name=%s", (sname, year, course))
            rows = cur.fetchall()

            if not rows:
                output = f"<div class='alert-message error'><i class='fas fa-info-circle'></i> No marks records found for Student: <b>{sname}</b> (Course: <b>{course}</b>, Year: <b>{year}</b>).</div>"
            else:
                output = """
                <div class="table-container">
                <table class="styled-table">
                    <thead>
                        <tr>
                            <th>Subject Name</th>
                            <th>Obtained Marks</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for row in rows:
                    output += f'<tr><td><strong>{row[0]}</strong></td><td>{row[1]}</td></tr>'
                    total += float(row[1])
                    count += 1

                avg_gpa = total / count if count > 0 else 0
                feedback_ml = runML(avg_gpa)
                badge_class = "badge-success" if feedback_ml == "Good" else ("badge-warning" if feedback_ml == "Fair" else "badge-danger")

                output += f"""
                    </tbody>
                    <tfoot>
                        <tr class="summary-row"><td><strong>Total Marks</strong></td><td><strong>{total:.1f}</strong></td></tr>
                        <tr class="summary-row"><td><strong>Average Percentage / GPA</strong></td><td><strong>{avg_gpa:.2f}%</strong></td></tr>
                        <tr class="summary-row highlight">
                            <td><strong>Machine Learning Performance Prediction</strong></td>
                            <td><span class="badge {badge_class}">{feedback_ml}</span></td>
                        </tr>
                    </tfoot>
                </table>
                </div>
                """

        return render(request, 'FacultyScreen.html', {'data': output})
    return redirect('ViewProgressReport')


def Messaging(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        output = '<tr><td><font size="3" color="black"><b>Choose Student Name</b></td>'
        output += '<td><select name="sname">'
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, student_name FROM student")
            rows = cur.fetchall()
            for row in rows:
                output += f'<option value="{row[0]}">{row[1]} ({row[0]})</option>'
        output += "</select></td></tr>"
        return render(request, 'Messaging.html', {'data1': output})


def MessagingAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        sname = request.POST.get('sname', '').strip()
        subject = request.POST.get('t1', '').strip()
        message = request.POST.get('t2', '').strip()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with get_db_cursor() as (cur, con):
                cur.execute("INSERT INTO messages VALUES(%s, %s, %s, %s, %s)", (uname, sname, subject, message, current_datetime))
                con.commit()

            email = getEmail(sname)
            email_sent = False
            if email:
                email_sent = sendMail(subject, message, email)

            if email_sent:
                status = f"Message successfully stored and email notification sent to {email}!"
            else:
                status = f"Message successfully stored in database for student '{sname}'!"
        except Exception as e:
            status = f"Error sending message: {str(e)}"

        return render(request, 'FacultyScreen.html', {'data': status})
    return redirect('Messaging')


def AddMarks(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        output = '<tr><td><font size="3" color="black"><b>Choose Student Name</b></td>'
        output += '<td><select name="sname">'
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, student_name FROM student")
            rows = cur.fetchall()
            for row in rows:
                output += f'<option value="{row[0]}">{row[1]} ({row[0]})</option>'
        output += "</select></td></tr>"
        return render(request, 'AddMarks.html', {'data1': output})


def AddMarksAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        sname = request.POST.get('sname', '').strip()
        course = request.POST.get('t1', '').strip()
        subject = request.POST.get('t2', '').strip()
        year = request.POST.get('t3', '').strip()
        marks = request.POST.get('t4', '').strip()
        feedback = request.POST.get('t5', '').strip()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with get_db_cursor() as (cur, con):
                query = "INSERT INTO marks VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(query, (sname, uname, course, year, subject, marks, feedback, current_datetime))
                con.commit()
                status = "Marks details successfully submitted!"
        except Exception as e:
            status = f"Error submitting marks: {str(e)}"

        return render(request, 'FacultyScreen.html', {'data': status})
    return redirect('AddMarks')


def UploadMaterial(request):
    uname = request.session.get('uname')
    if not uname:
        return redirect('FacultyLogin')
    return render(request, 'UploadMaterial.html', {})


def UploadMaterialAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        material = request.POST.get('t1', '').strip()
        desc = request.POST.get('t2', '').strip()

        if 't3' in request.FILES:
            upload_file = request.FILES['t3']
            filename = os.path.basename(upload_file.name)
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                with get_db_cursor() as (cur, con):
                    query = "INSERT INTO uploadmaterial VALUES(%s, %s, %s, %s, %s)"
                    cur.execute(query, (uname, material, desc, filename, current_datetime))
                    con.commit()

                save_dir = os.path.join(settings.BASE_DIR, "StudentApp", "static", "files")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, filename)

                with open(save_path, "wb") as f:
                    for chunk in upload_file.chunks():
                        f.write(chunk)

                status = f"Study material '{material}' successfully uploaded!"
            except Exception as e:
                status = f"Error uploading material: {str(e)}"
        else:
            status = "No file selected. Please choose a file to upload."

        return render(request, 'UploadMaterial.html', {'data': status})
    return redirect('UploadMaterial')


def CreateAssignments(request):
    uname = request.session.get('uname')
    if not uname:
        return redirect('FacultyLogin')
    return render(request, 'CreateAssignments.html', {})


def CreateAssignmentsAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        course = request.POST.get('t1', '').strip()
        subject = request.POST.get('t2', '').strip()
        year = request.POST.get('t3', '').strip()
        assignment = request.POST.get('t4', '').strip()
        desc = request.POST.get('t5', '').strip()
        dd = request.POST.get('t6', '').strip()

        try:
            with get_db_cursor() as (cur, con):
                query = "INSERT INTO assignments VALUES(%s, %s, %s, %s, %s, %s, %s)"
                cur.execute(query, (uname, course, subject, year, assignment, desc, dd))
                con.commit()
                status = "Assignment task successfully created!"
        except Exception as e:
            status = f"Error submitting assignment: {str(e)}"

        return render(request, 'CreateAssignments.html', {'data': status})
    return redirect('CreateAssignments')


def AddAttendance(request):
    if request.method == 'GET':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        output = '<tr><td><font size="3" color="black"><b>Select Students (Multi-Select)</b></td>'
        output += '<td><select name="t1" multiple size="8">'
        with get_db_cursor() as (cur, con):
            cur.execute("SELECT username, student_name, course, course_year FROM student")
            rows = cur.fetchall()
            for row in rows:
                output += f'<option value="{row[0]}">{row[1]} ({row[0]} - {row[2]} {row[3]})</option>'
        output += "</select></td></tr>"
        return render(request, 'AddAttendance.html', {'data1': output})


def AddAttendanceAction(request):
    if request.method == 'POST':
        uname = request.session.get('uname')
        if not uname:
            return redirect('FacultyLogin')

        students = request.POST.getlist('t1')
        if not students:
            return render(request, 'FacultyScreen.html', {'data': 'Error: No students selected. Please select at least one student.'})

        current_datetime = datetime.now().strftime("%Y-%m-%d")
        try:
            with get_db_cursor() as (cur, con):
                insert_query = "INSERT INTO student_attendance VALUES (%s, %s, %s)"
                for student in students:
                    cur.execute(insert_query, (student, uname, current_datetime))
                con.commit()
                status = f"Attendance successfully marked for {len(students)} student(s)!"
        except Exception as e:
            status = f"Database Error: {str(e)}"

        return render(request, 'FacultyScreen.html', {'data': status})
    return redirect('AddAttendance')