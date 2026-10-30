from django.urls import path
from . import views

urlpatterns = [
    # ROOT URL
    path("", views.index, name="home"),
    path("index/", views.index, name="index"),

    # Admin URLs
    path("admin-login/", views.AdminLogin, name="AdminLogin"),
    path("admin-login-action/", views.AdminLoginAction, name="AdminLoginAction"),
    
    # Faculty URLs
    path("add-faculty/", views.AddFaculty, name="AddFaculty"),
    path("add-faculty-action/", views.AddFacultyAction, name="AddFacultyAction"),
    path("faculty-login/", views.FacultyLogin, name="FacultyLogin"),
    path("faculty-login-action/", views.FacultyLoginAction, name="FacultyLoginAction"),
    path("view-faculty/", views.ViewFaculty, name="ViewFaculty"),
    path("choose-faculty/", views.ChooseFaculty, name="ChooseFaculty"),
    path("faculty-suggestion/", views.FacultySuggestion, name="FacultySuggestion"),
    path("auto-faculty-selection/", views.AutoFacultySelection, name="AutoFacultySelection"),

    # Student URLs
    path("add-student/", views.AddStudent, name="AddStudent"),
    path("add-student-action/", views.AddStudentAction, name="AddStudentAction"),
    path("student-login/", views.StudentLogin, name="StudentLogin"),
    path("student-login-action/", views.StudentLoginAction, name="StudentLoginAction"),
    path("view-student/", views.ViewStudent, name="ViewStudent"),
    path("student-screen/", views.StudentScreen, name="StudentScreen"),

    # Academics & Performance URLs
    path("school-performance/", views.SchoolPerformance, name="SchoolPerformance"),
    path("add-attendance/", views.AddAttendance, name="AddAttendance"),
    path("add-attendance-action/", views.AddAttendanceAction, name="AddAttendanceAction"),
    path("add-marks/", views.AddMarks, name="AddMarks"),
    path("add-marks-action/", views.AddMarksAction, name="AddMarksAction"),
    path("view-marks/", views.ViewMarks, name="ViewMarks"),
    path("view-marks-action/", views.ViewMarksAction, name="ViewMarksAction"),
    path("view-progress-report/", views.ViewProgressReport, name="ViewProgressReport"),
    path("view-progress-report-action/", views.ViewProgressReportAction, name="ViewProgressReportAction"),

    # Materials & Assignments URLs
    path("create-assignments/", views.CreateAssignments, name="CreateAssignments"),
    path("create-assignments-action/", views.CreateAssignmentsAction, name="CreateAssignmentsAction"),
    path("upload-material/", views.UploadMaterial, name="UploadMaterial"),
    path("upload-material-action/", views.UploadMaterialAction, name="UploadMaterialAction"),
    path("download-materials/", views.DownloadMaterials, name="DownloadMaterials"),
    path("download-material-action/", views.DownloadMaterialAction, name="DownloadMaterialAction"),
    path("view-assignments/", views.ViewAssignments, name="ViewAssignments"),

    # Messaging & Feedback URLs
    path("student-messaging/", views.StudentMessaging, name="StudentMessaging"),
    path("student-messaging-action/", views.StudentMessagingAction, name="StudentMessagingAction"),
    path("messaging/", views.Messaging, name="Messaging"),
    path("messaging-action/", views.MessagingAction, name="MessagingAction"),
    path("view-messages/", views.ViewMessages, name="ViewMessages"),
    path("view-student-messages/", views.ViewStudentMessages, name="ViewStudentMessages"),
    path("feedback/", views.Feedback, name="Feedback"),
    path("feedback-action/", views.FeedbackAction, name="FeedbackAction"),

    # Session Management
    path("logout/", views.Logout, name="Logout"),
]