from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
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

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        action = request.form.get("action")

        # ================= ADD STUDENT =================
        if action == "add":

            name = request.form.get("name")
            roll = request.form.get("roll")  # keep string
            dept = request.form.get("dept")
            section = request.form.get("section")

            try:
                subjects = int(request.form.get("subjects"))
                marks_input = request.form.get("marks")

                # Convert "80,90,70" → [80,90,70]
                marks = [int(x.strip()) for x in marks_input.split(",")]

                # Validation
                if len(marks) != subjects:
                    return "❌ Subjects count & marks mismatch!"

                if any(m < 0 or m > 100 for m in marks):
                    return "❌ Marks must be between 0–100"

                cgpa = round(sum(marks) / len(marks), 2)

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

            except:
                return "❌ Invalid input format!"

        # ================= DELETE =================
        elif action == "delete":
            roll = request.form.get("roll")

            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
            conn.commit()
            conn.close()

        # ================= SEARCH =================
        elif action == "search":
            search_roll = request.form.get("search_roll")

            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE roll=?", (search_roll,))
            result = cursor.fetchall()
            conn.close()

            return render_template("index.html", students=result)

        # ================= UPDATE =================
        elif action == "update":
            roll = request.form.get("roll")
            new_marks_input = request.form.get("marks")

            try:
                marks = [int(x.strip()) for x in new_marks_input.split(",")]

                if any(m < 0 or m > 100 for m in marks):
                    return "❌ Invalid marks!"

                cgpa = round(sum(marks) / len(marks), 2)

                conn = sqlite3.connect("students.db")
                cursor = conn.cursor()

                cursor.execute("""
                UPDATE students SET marks=?, cgpa=? WHERE roll=?
                """, (new_marks_input, cgpa, roll))

                conn.commit()
                conn.close()

            except:
                return "❌ Update failed!"

        return redirect("/")

    # GET REQUEST
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("index.html", students=students)


if __name__ == "__main__":
    app.run(debug=True)
