from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import re
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SKILLS = [
    "python", "java", "c", "c++", "javascript", "html", "css", "bootstrap",
    "react", "node.js", "flask", "django", "sql", "mysql", "sqlite",
    "mongodb", "dbms", "machine learning", "deep learning", "nlp",
    "tensorflow", "pandas", "numpy", "scikit-learn", "git", "github",
    "rest api", "aws", "docker", "linux", "data analysis", "excel",
    "power bi", "tableau", "communication", "problem solving"
]

JOB_DATA = [
    ("Python Developer", "Python Flask Django SQL Git REST API problem solving"),
    ("Web Developer", "HTML CSS JavaScript Bootstrap React Python SQL Git"),
    ("Data Analyst", "Python SQL Pandas NumPy Excel Power BI Tableau Data Analysis"),
    ("Java Developer", "Java SQL DBMS Spring Git REST API problem solving"),
    ("Machine Learning Engineer", "Python Machine Learning Pandas NumPy Scikit-learn TensorFlow SQL"),
    ("Frontend Developer", "HTML CSS JavaScript Bootstrap React Git"),
    ("Backend Developer", "Python Java Flask Django SQL REST API Git Docker"),
    ("Database Developer", "SQL MySQL SQLite DBMS Python Git"),
]

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    if conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO jobs (title, description) VALUES (?, ?)",
            JOB_DATA
        )
    conn.commit()
    conn.close()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_text(path):
    text = []
    reader = PdfReader(path)
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)

def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))

def calculate_matches(resume_text):
    conn = get_db()
    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()

    documents = [resume_text] + [job["description"] for job in jobs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    results = []
    resume_skills = set(extract_skills(resume_text))

    for job, score in zip(jobs, scores):
        required = set(extract_skills(job["description"]))
        missing = sorted(required - resume_skills)
        results.append({
            "id": job["id"],
            "title": job["title"],
            "score": round(float(score) * 100, 2),
            "missing": missing,
            "required": sorted(required)
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results, sorted(resume_skills)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            flash("Please fill all fields.")
            return redirect(url_for("register"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.")
            return redirect(url_for("register"))
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session.get("name"))

@app.route("/analyze", methods=["POST"])
def analyze():
    if "user_id" not in session:
        return redirect(url_for("login"))

    file = request.files.get("resume")
    if not file or file.filename == "":
        flash("Please select a PDF resume.")
        return redirect(url_for("dashboard"))

    if not allowed_file(file.filename):
        flash("Only PDF resumes are supported.")
        return redirect(url_for("dashboard"))

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        resume_text = extract_pdf_text(path)
        if not resume_text.strip():
            flash("Could not extract text from the PDF. Please upload a text-based PDF.")
            return redirect(url_for("dashboard"))

        matches, skills = calculate_matches(resume_text)
        top_matches = matches[:5]
        return render_template(
            "results.html",
            matches=top_matches,
            skills=skills,
            resume_text=resume_text[:3000]
        )
    except Exception as exc:
        flash(f"Error analyzing resume: {exc}")
        return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
