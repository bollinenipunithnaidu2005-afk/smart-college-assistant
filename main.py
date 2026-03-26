from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll TEXT UNIQUE,
        dept TEXT,
        section TEXT,
        subjects INTEGER,
        marks TEXT,
        cgpa REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            try:
                name = request.form.get("name", "").strip()
                roll = request.form.get("roll", "").strip()
                dept = request.form.get("dept", "").strip()
                section = request.form.get("section", "").strip()
                marks_input = request.form.get("marks", "").strip()

                # Validate empty
                if not name or not roll or not marks_input:
                    return "❌ Fill all fields"

                # Convert marks
                marks = []
                for m in marks_input.split(","):
                    m = m.strip()
                    if not m.isdigit():
                        return "❌ Use format like 80,90,70"
                    m = int(m)

                    if m < 0 or m > 100:
                        return "❌ Marks must be 0–100"

                    marks.append(m)

                subjects = len(marks)

                # CGPA
                cgpa = round(sum(marks) / len(marks), 2)

                # Save
                conn = sqlite3.connect("students.db")
                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO students (name, roll, dept, section, subjects, marks, cgpa)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, roll, dept, section, subjects, marks_input, cgpa))

                conn.commit()
                conn.close()

            except sqlite3.IntegrityError:
                return "❌ Roll number already exists!"
            except Exception as e:
                return f"ERROR: {e}"

        return redirect("/")

    # GET
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("index.html", students=students or [])


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", students=students or [])


if __name__ == "__main__":
    app.run(debug=True)
