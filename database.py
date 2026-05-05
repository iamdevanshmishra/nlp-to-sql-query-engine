import sqlite3
import random
from datetime import datetime, timedelta
import os

# ------------------ DATABASE PATH ------------------
DB_NAME = os.path.join(os.path.dirname(__file__), "student.db")

# ------------------ CREATE CONNECTION ------------------
connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

# ------------------ DROP TABLE (optional clean run) ------------------
cursor.execute("DROP TABLE IF EXISTS STUDENT")

# ------------------ CREATE TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS STUDENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    course TEXT NOT NULL,
    section TEXT NOT NULL,
    marks INTEGER NOT NULL CHECK(marks BETWEEN 0 AND 100),
    exam_date DATE NOT NULL
);
""")

# ------------------ SAMPLE DATA CONFIG ------------------
COURSES = [
    "Data Science",
    "DevOps",
    "Web Development",
    "Cyber Security",
    "AI/ML"
]

SECTIONS = ["A", "B", "C", "D"]

FIRST_NAMES = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Aditi","Bharat",
    "Krishna","Ishaan","Shaurya","Atharv","Kabir","Rudra","Aryan","Aniket",
    "Ananya","Diya","Ira","Myra","Aadhya","Sara","Navya","Aadeesh",
    "Meera","Riya","Kavya","Siya","Anika","Devansh","Anirudha"
]

LAST_NAMES = [
    "Sharma","Verma","Gupta","Singh","Khare",
    "Kumar","Patel","Yadav","Shah","Joshi","Mehta",
    "Agarwal","Chauhan","Pandey","Mishra","Tiwari",
    "Reddy","Nair","Iyer","Das","Ghosh","Khatwani",
    "Banerjee","Mukherjee","Chatterjee","Kulkarni","Deshmukh","Borkar","Singhai","Jain"
]

# ------------------ RANDOM DATE GENERATOR ------------------
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

# ------------------ GENERATE LARGE DATASET ------------------
def generate_students(n=5000):
    data = []

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    for _ in range(n):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        course = random.choice(COURSES)
        section = random.choice(SECTIONS)

        # realistic marks distribution
        base = random.gauss(70, 15)
        marks = max(0, min(100, int(base)))

        exam_date = random_date(start_date, end_date)

        data.append((first_name, last_name, course, section, marks, exam_date))

    return data

# ------------------ INSERT DATA ------------------
print("Generating large dataset...")
student_data = generate_students(5000)

cursor.executemany("""
INSERT INTO STUDENT (first_name, last_name, course, section, marks, exam_date)
VALUES (?, ?, ?, ?, ?, ?)
""", student_data)

connection.commit()

# ------------------ VERIFY COUNT ------------------
count = cursor.execute("SELECT COUNT(*) FROM STUDENT").fetchone()[0]
print(f"✅ Total rows inserted: {count}")

# ------------------ CLOSE ------------------
connection.close()
print("✅ Database ready for QuerySense!")