from flask import Flask, render_template, request

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import PyPDF2

app = Flask(__name__)

# -------------------------------------------------
# QUESTION ENGINE (EXPANDED – MORE Q&A)
# -------------------------------------------------
def get_questions_by_skills(skills, level):
    data = {

        "python": {
            "easy": [
                {"q": "What is Python?", "a": "Python is a high-level interpreted programming language."},
                {"q": "Is Python compiled or interpreted?", "a": "Python is interpreted."},
                {"q": "What are Python keywords?", "a": "Reserved words with special meaning."},
                {"q": "What is PEP 8?", "a": "Python style guide."}
            ],
            "medium": [
                {"q": "Difference between list and tuple?", "a": "Lists are mutable, tuples are immutable."},
                {"q": "What is list comprehension?", "a": "Compact syntax for creating lists."},
                {"q": "What is a dictionary?", "a": "Key-value data structure."},
                {"q": "What are *args and **kwargs?", "a": "Used to pass variable arguments."}
            ],
            "hard": [
                {"q": "Explain decorators.", "a": "Decorators modify function behavior."},
                {"q": "What is GIL?", "a": "Global Interpreter Lock controls threads."},
                {"q": "Deep copy vs shallow copy?", "a": "Deep copies objects, shallow copies references."},
                {"q": "Explain generators.", "a": "Functions that yield values using yield keyword."}
            ]
        },

        "dbms": {
            "easy": [
                {"q": "What is DBMS?", "a": "Software to manage databases."},
                {"q": "What is a database?", "a": "Organized collection of data."},
                {"q": "What is a table?", "a": "Data stored in rows and columns."},
                {"q": "What is SQL?", "a": "Structured Query Language."}
            ],
            "medium": [
                {"q": "What is normalization?", "a": "Reduces data redundancy."},
                {"q": "Primary key?", "a": "Unique identifier for records."},
                {"q": "Foreign key?", "a": "Links two tables."},
                {"q": "What is a join?", "a": "Combines rows from tables."}
            ],
            "hard": [
                {"q": "Explain ACID properties.", "a": "Atomicity, Consistency, Isolation, Durability."},
                {"q": "What is indexing?", "a": "Improves query performance."},
                {"q": "What is deadlock in DBMS?", "a": "Transactions wait indefinitely."},
                {"q": "Explain isolation levels.", "a": "Controls data visibility in transactions."}
            ]
        },

        "os": {
            "easy": [
                {"q": "What is an Operating System?", "a": "Manages hardware and software."},
                {"q": "Functions of OS?", "a": "Process, memory, file management."},
                {"q": "Types of OS?", "a": "Batch, Time-sharing, Real-time."}
            ],
            "medium": [
                {"q": "Process vs Thread?", "a": "Threads share memory."},
                {"q": "What is scheduling?", "a": "CPU time allocation."},
                {"q": "What is context switching?", "a": "Switching CPU between processes."}
            ],
            "hard": [
                {"q": "Explain deadlock.", "a": "Processes wait indefinitely."},
                {"q": "Deadlock conditions?", "a": "Mutual exclusion, hold & wait, no preemption, circular wait."},
                {"q": "What is paging?", "a": "Memory management technique."}
            ]
        },

        "cn": {
            "easy": [
                {"q": "What is a computer network?", "a": "Connects devices."},
                {"q": "Types of networks?", "a": "LAN, WAN, MAN."},
                {"q": "What is IP?", "a": "Internet Protocol."}
            ],
            "medium": [
                {"q": "What is TCP?", "a": "Reliable protocol."},
                {"q": "TCP vs UDP?", "a": "TCP reliable, UDP faster."},
                {"q": "What is DNS?", "a": "Resolves domain names."}
            ],
            "hard": [
                {"q": "Explain OSI model.", "a": "7-layer network model."},
                {"q": "What is congestion control?", "a": "Manages traffic."},
                {"q": "What is subnetting?", "a": "Divides networks."}
            ]
        }
    }

    grouped_questions = {}
    for skill in skills:
        questions = data.get(skill, {}).get(level, [])
        if questions:
            grouped_questions[skill.upper()] = questions

    return grouped_questions


# -------------------------------------------------
# JD NLP
# -------------------------------------------------
def extract_jd_skills(text):
    if not text:
        return []

    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    filtered = [w for w in tokens if w.isalpha() and w not in stop_words]

    mapping = {
        "python": ["python"],
        "dbms": ["sql", "database"],
        "os": ["operating", "system"],
        "cn": ["network", "tcp"]
    }

    skills = set()
    for skill, words in mapping.items():
        for w in filtered:
            if w in words:
                skills.add(skill)

    return list(skills)


# -------------------------------------------------
# RESUME PARSING
# -------------------------------------------------
def extract_resume_text(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()


def extract_resume_skills(text):
    skills = []
    if "python" in text: skills.append("python")
    if "sql" in text: skills.append("dbms")
    if "network" in text: skills.append("cn")
    if "operating system" in text: skills.append("os")
    return skills


# -------------------------------------------------
# MAIN ROUTE
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    grouped_questions = {}
    level = None

    if request.method == "POST":
        mode = request.form.get("mode")
        level = request.form.get("level")

        if mode == "skill":
            skills = request.form.getlist("skills")
            grouped_questions = get_questions_by_skills(skills, level)

        elif mode == "jd":
            jd_text = request.form.get("jd_input")
            skills = extract_jd_skills(jd_text)
            grouped_questions = get_questions_by_skills(skills, level)

        elif mode == "resume":
            resume_file = request.files.get("resume_file")
            if resume_file:
                text = extract_resume_text(resume_file)
                skills = extract_resume_skills(text)
                grouped_questions = get_questions_by_skills(skills, level)

    return render_template(
        "index.html",
        grouped_questions=grouped_questions,
        level=level
    )


if __name__ == "__main__":
    app.run(debug=True)
