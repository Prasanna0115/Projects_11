from flask import Flask, render_template_string, request
import pdfplumber
from docx import Document
import os
import uuid
from werkzeug.utils import secure_filename
app = Flask(__name__)
def read_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text
def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text
def analyse_resume(text, role):
    skills = [
        "python",
        "flask",
        "sql",
        "database",
        "api",
        "backend",
        "openai",
        "tidb"
    ]
    found_skills = []
    text = text.lower()
    for skill in skills:
        if skill in text:
            found_skills.append(skill)
    score = int((len(found_skills) / len(skills)) * 100)
    return {
        "role": role,
        "skills": found_skills,
        "score": score
    }
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Resume Analyser</title>
</head>
<body>
    <h1>AI Resume Analyser</h1>
    <form method="POST" enctype="multipart/form-data">
        <label>Upload Resume (PDF/DOCX):</label><br><br>
        <input type="file" name="resume" required><br><br>
        <label>Role:</label><br><br>
        <input type="text" name="role" placeholder="Backend Engineer" required><br><br>
        <button type="submit">Analyse Resume</button>
    </form>
    {% if result %}
        <h2>Analysis Result</h2>
        <p><b>Role:</b> {{ result.role }}</p>
        <p><b>Matched Skills:</b> {{ result.skills }}</p>
        <p><b>Resume Score:</b> {{ result.score }}%</p>
    {% endif %}
</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        file = request.files.get("resume")
        role = request.form.get("role", "")
        if file and file.filename:
            filename = secure_filename(file.filename)
            filename = str(uuid.uuid4()) + "_" + filename
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", filename)
            file.save(file_path)
            if filename.endswith(".pdf"):
                text = read_pdf(file_path)
            elif filename.endswith(".docx"):
                text = read_docx(file_path)
            else:
                text = ""
            result = analyse_resume(text, role)
    return render_template_string(HTML, result=result)
if __name__ == "__main__":
    app.run(debug=True)

    # http://127.0.0.1:5000