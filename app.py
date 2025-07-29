from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret-key"

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS absences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                date TEXT,
                reason TEXT,
                added_by TEXT
            )
        ''')

        conn.execute("INSERT OR IGNORE INTO teachers (username, password) VALUES (?, ?)", ("teacher", "12345"))
    print("Database initialized.")

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect("database.db") as conn:
            result = conn.execute("SELECT * FROM teachers WHERE username=? AND password=?", (username, password)).fetchone()
            if result:
                session["teacher"] = username
                return redirect("/dashboard")
            else:
                return "معلومات الدخول خاطئة"
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "teacher" not in session:
        return redirect("/")
    if request.method == "POST":
        student = request.form["student"]
        date = request.form["date"]
        reason = request.form["reason"]
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO absences (student_name, date, reason, added_by) VALUES (?, ?, ?, ?)",
                         (student, date, reason, session["teacher"]))
    with sqlite3.connect("database.db") as conn:
        absences = conn.execute("SELECT * FROM absences WHERE added_by=?", (session["teacher"],)).fetchall()
    return render_template("dashboard.html", absences=absences)


@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
