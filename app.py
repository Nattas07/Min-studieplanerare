from flask import Flask, render_template, request, redirect
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data.json"
EVENT_FILE = "event.json"

# ---------- Hjälpfunktioner ----------

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def load_event():
    if not os.path.exists(EVENT_FILE):
        return {}
    with open(EVENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_event(event):
    with open(EVENT_FILE, "w", encoding="utf-8") as f:
        json.dump(event, f, indent=4, ensure_ascii=False)

# ---------- Startsida ----------

@app.route("/")
def index():
    tasks = load_tasks()
    event = load_event()

    # Beräkna dagar kvar för event
    days_left = None
    if event.get("date"):
        try:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            days_left = (event_date - datetime.now()).days
        except:
            days_left = None

    # Beräkna dagar kvar för varje uppgift
    for task in tasks:
        try:
            deadline_date = datetime.strptime(task["deadline"], "%Y-%m-%d")
            task["days_left"] = (deadline_date - datetime.now()).days
        except:
            task["days_left"] = "N/A"

    # Sortera uppgifter efter närmaste deadline först
    tasks.sort(key=lambda x: x.get("deadline", "9999-12-31"))

    return render_template("index.html", tasks=tasks, event=event, days_left=days_left)

# ---------- Lägg till uppgift ----------

@app.route("/add", methods=["POST"])
def add():
    tasks = load_tasks()

    links_raw = request.form.get("links", "")
    links = [l.strip() for l in links_raw.split(",") if l.strip()]  

    new_task = {
        "id": str(uuid.uuid4()),
        "title": request.form["title"],
        "deadline": request.form["deadline"],
        "status": "Ej påbörjad",
        "task_type": request.form.get("task_type", ""),
        "links": links  # ← sparar listan med länkar
    }

    tasks.append(new_task)
    save_tasks(tasks)
    return redirect("/")

# ---------- Uppdatera status eller ta bort uppgift ----------

@app.route("/update_status", methods=["POST"])
def update_status():
    task_id = request.form.get("task_id")
    tasks = load_tasks()

    if "status" in request.form:
        new_status = request.form["status"]
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = new_status
                break
    elif "delete" in request.form:
        tasks = [task for task in tasks if task["id"] != task_id]

    save_tasks(tasks)
    return redirect("/")

# ---------- Lägg till händelse ----------

@app.route("/add_event", methods=["POST"])
def add_event():
    event = {
        "name": request.form["name"],
        "date": request.form["date"]
    }
    save_event(event)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)