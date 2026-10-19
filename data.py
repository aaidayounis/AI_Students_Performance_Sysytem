"""Results of the analysis that was already done in project.ipynb.

The CSV itself is not needed to run the website - every number below comes
from the notebook's outputs (describe(), isnull(), the charts and the heatmap).
Bar heights that were only shown as pictures in the notebook were measured
from the chart images, so they are accurate to roughly +/- 0.1 points
(+/- 2 students for the grade counts).
"""

N_STUDENTS = 4000
N_COLUMNS = 15
DUPLICATES = 0

# Missing values found in the notebook (df.isnull().sum()) - filled with median / mode
MISSING = [
    ("Previous_GPA", 107, "median"),
    ("Sleep_Hours_Per_Day", 115, "median"),
    ("Midterm_Score", 81, "median"),
    ("Study_Hours_Per_Day", 57, "median"),
    ("Quiz_Average", 56, "median"),
    ("Attendance_Percent", 42, "median"),
    ("Extracurricular_Activities", 40, "mode"),
    ("Final_Exam_Score", 38, "median"),
    ("Gender", 32, "mode"),
    ("Assignments_Completed", 30, "median"),
    ("Final_Grade", 22, "mode"),
    ("Internet_Access", 19, "mode"),
    ("Age", 17, "median"),
]

# df.describe() (before cleaning) - mean / std
STATS = {
    "quiz": {"mean": 59.38, "std": 15.93},
    "midterm": {"mean": 59.35, "std": 17.83},
    "final": {"mean": 59.50, "std": 18.93},
    "gpa": {"mean": 2.99, "std": 0.50},
    "study": {"mean": 3.55, "std": 1.75},
    "attendance": {"mean": 76.79, "std": 14.12},
    "sleep": {"mean": 6.83, "std": 1.21},
    "completion": {"mean": 83.5, "std": 15.0},  # mean completed / mean total
}

# Final grade distribution (cell 17) in natural grade order
GRADES = [("A+", 116), ("A", 303), ("B", 733), ("C", 1065), ("D", 976), ("F", 807)]

# Average Quiz / Midterm / Final (cell 20)
AVG_SCORES = [("Quiz", 59.36), ("Midterm", 59.33), ("Final Exam", 59.49)]

# Internet access vs final exam (cell 23)
INTERNET = [("No internet", 55.82), ("Internet", 59.98)]

# Final exam score by group (cells 30, 33, 36, 38)
SLEEP = [("Below 5 h", 57.46), ("5-7 h", 59.46), ("7-9 h", 59.63), ("Above 9 h", 62.42)]
STUDY = [("0-2 h", 53.42), ("2-4 h", 58.57), ("4-6 h", 63.15), ("Above 6 h", 67.96)]
ATTENDANCE = [("Below 50%", 52.96), ("50-70%", 56.35), ("70-85%", 59.75), ("85-100%", 62.45)]
# 0-25% bin was empty in the notebook (no student that low), so it is not shown
COMPLETION = [("26-50%", 51.98), ("51-75%", 56.92), ("76-100%", 60.63)]

# Correlation heatmap (cell 27)
CORR_LABELS = ["Study Hours", "Attendance", "Assignments", "Midterm", "Quiz Avg", "Prev. GPA", "Final Exam"]
CORR = [
    [1.00, 0.03, 0.13, 0.26, 0.27, -0.01, 0.24],
    [0.03, 1.00, 0.22, 0.19, 0.19, -0.01, 0.15],
    [0.13, 0.22, 1.00, 0.07, 0.09, -0.02, 0.05],
    [0.26, 0.19, 0.07, 1.00, 0.61, 0.36, 0.52],
    [0.27, 0.19, 0.09, 0.61, 1.00, 0.41, 0.56],
    [-0.01, -0.01, -0.02, 0.36, 0.41, 1.00, 0.35],
    [0.24, 0.15, 0.05, 0.52, 0.56, 0.35, 1.00],
]
R_QUIZ_FINAL = 0.56
