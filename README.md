# AI Resume Screening & Job Recommendation System

A beginner-friendly Flask minor project that analyzes a student's PDF resume and recommends suitable job roles using NLP, TF-IDF and Cosine Similarity.

## Features

- Student registration and login
- PDF resume upload
- Resume text extraction
- Basic skill extraction
- TF-IDF based resume/job representation
- Cosine Similarity matching
- Top job recommendations
- Matching percentage
- Skill-gap analysis
- SQLite database
- Bootstrap-based interface

## Technology Stack

- Frontend: HTML, CSS, Bootstrap
- Backend: Python, Flask
- Database: SQLite
- AI/NLP: Scikit-learn, TF-IDF, Cosine Similarity
- PDF processing: PyPDF2

## Project Structure

ai_resume_job_recommendation/
├── app.py
├── requirements.txt
├── README.md
├── database.db          (created automatically)
├── uploads/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── results.html

## How to Run on Windows

1. Extract the ZIP file.
2. Open the extracted folder in VS Code.
3. Open Terminal in VS Code.
4. Create a virtual environment:

   python -m venv venv

5. Activate it:

   .\venv\Scripts\activate

6. Install dependencies:

   pip install -r requirements.txt

7. Run:

   python app.py

8. Open the browser at:

   http://127.0.0.1:5000

## Important

The initial version supports text-based PDF resumes. Scanned/image-only PDFs may not produce usable text unless OCR is added.

The matching percentage is a similarity score produced by the model; it is not a hiring probability or guarantee.

## Suggested Future Enhancements

- DOCX resume support
- OCR for scanned resumes
- spaCy/NER-based skill extraction
- BERT/transformer embeddings
- Admin panel for adding jobs
- Resume improvement suggestions
- Course recommendations for missing skills
- More detailed resume parsing
