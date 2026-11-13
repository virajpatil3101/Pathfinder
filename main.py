
from pathlib import Path
import json, sqlite3, re, os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent.parent
DB = Path(os.environ.get("PATHFINDER_DB_PATH", str(BASE / "pathfinder.sqlite3")))
DB.parent.mkdir(parents=True, exist_ok=True)
CAREERS = json.loads((BASE / "data" / "careers.json").read_text(encoding="utf-8"))
FAQS = json.loads((BASE / "data" / "faqs.json").read_text(encoding="utf-8"))

app = FastAPI(title="PathFinder - Student Career Guidance", version="1.0")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

@app.on_event("startup")
def startup():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS assessments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            education TEXT NOT NULL,
            report_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"status":"ok","message":"PathFinder backend is running"}

@app.get("/api/careers")
def get_careers():
    return {"careers": CAREERS}

class Assessment(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int | None = Field(default=None, ge=13, le=60)
    education: str = Field(min_length=2, max_length=100)
    interests: list[str] = Field(min_length=1, max_length=20)
    quiz_answers: dict[str, int]
    skill_ratings: dict[str, int] = {}

@app.post("/api/assessment")
def assessment(data: Assessment):
    ids = {c["id"] for c in CAREERS}
    counts = {}
    other = []
    for raw in data.interests:
        value = raw.strip()
        key = value.lower()
        if key in ids:
            counts[key] = counts.get(key, 0) + 1
        elif value:
            other.append(value)

    # Quiz is intentionally small and transparent; frontend sends question ID and selected option.
    questions = {
      "q1": {"correct":1, "domain":"technology"},
      "q2": {"correct":1, "domain":"technology"},
      "q3": {"correct":2, "domain":"business"},
      "q4": {"correct":0, "domain":"engineering"},
      "q5": {"correct":1, "domain":"public_service"},
      "q6": {"correct":2, "domain":"healthcare"},
      "q7": {"correct":0, "domain":"technology"},
      "q8": {"correct":1, "domain":"agriculture"}
    }
    valid = {k:v for k,v in data.quiz_answers.items() if k in questions}
    correct = sum(1 for k,v in valid.items() if v == questions[k]["correct"])
    knowledge = round(100 * correct / len(questions)) if len(valid) == len(questions) else round(100 * correct / max(1,len(valid)))
    ranked = sorted(CAREERS, key=lambda c: counts.get(c["id"],0), reverse=True)
    ranked = [c for c in ranked if counts.get(c["id"],0) > 0][:3]
    if not ranked:
        ranked = [CAREERS[0]]
    ratings = {k:max(0,min(4,int(v))) for k,v in data.skill_ratings.items()}
    skill_pct = round(sum(ratings.values())/(4*len(ratings))*100) if ratings else None
    interest_pct = round(max(counts.values(), default=0)/max(1,len(data.interests))*100)
    overall_parts = [knowledge*.4, interest_pct*.3]
    total_weight = .7
    if skill_pct is not None:
        overall_parts.append(skill_pct*.3)
        total_weight = 1.0
    overall = round(sum(overall_parts)/total_weight)
    confidence = "Limited"
    if len(valid) == 8 and len(data.interests) >= 5 and skill_pct is not None:
        confidence = "Moderate"
    report = {
      "student_name": data.name, "education": data.education,
      "scores":{"knowledge":knowledge,"interest_alignment":interest_pct,
                "skill_self_rating":skill_pct,"overall_indicator":overall},
      "confidence":confidence,
      "career_matches":[
        {"id":c["id"],"name":c["name"],"icon":c["icon"],
         "reason":f"You selected this area {counts.get(c['id'],0)} time(s).",
         "courses":c["courses"],"jobs":c["jobs"],"skills":c["skills"],"roadmap":c["roadmap"]}
        for c in ranked
      ],
      "skill_ratings":ratings,
      "other_interests":other,
      "important_note":"Exploratory guidance only. This is not a validated aptitude test and does not guarantee admission, a job or salary. Verify course eligibility and professional requirements from official sources."
    }
    with connect() as con:
        cur = con.execute("INSERT INTO assessments(student_name,education,report_json) VALUES(?,?,?)",
                          (data.name,data.education,json.dumps(report,ensure_ascii=False)))
        report["assessment_id"] = cur.lastrowid
    return report

@app.get("/api/assessment/{assessment_id}")
def get_assessment(assessment_id: int):
    with connect() as con:
        row = con.execute("SELECT report_json FROM assessments WHERE id=?",(assessment_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Assessment not found")
    result = json.loads(row["report_json"])
    result["assessment_id"] = assessment_id
    return result

def tokens(s):
    return set(re.findall(r"[a-z0-9+#]+", s.lower()))

@app.post("/api/chat")
def chat(payload: dict):
    question = str(payload.get("question","")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please type a question.")
    qtokens = tokens(question)
    ranked = []
    for item in FAQS:
        searchable = item["q"] + " " + " ".join(item["keywords"]) + " " + item["a"]
        overlap = len(qtokens & tokens(searchable)) / max(1,len(qtokens))
        ranked.append((overlap,item))
    ranked.sort(key=lambda x:x[0], reverse=True)
    score,item = ranked[0]
    if score < 0.18:
        return {"answer":"I don't have a verified answer for that question yet. Please rephrase it or check with a qualified counsellor / the relevant official institution.",
                "confidence":"Low","source":None,"abstained":True}
    return {"answer":item["a"],"confidence":"Moderate" if score >= .35 else "Limited",
            "source":item["source"],"abstained":False}

@app.get("/api/history")
def history():
    with connect() as con:
        rows = con.execute("SELECT id,student_name,education,created_at FROM assessments ORDER BY id DESC LIMIT 20").fetchall()
    return {"assessments":[dict(r) for r in rows]}
