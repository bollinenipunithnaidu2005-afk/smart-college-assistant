from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# 🔥 CREATE DATABASE
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
        marks INTEGER,
        cgpa REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# 🔍 PERFORMANCE ANALYSIS
def analyze_performance(marks):
    if marks >= 90:
        return "🌟 Excellent!"
    elif marks >= 75:
        return "👍 Good"
    elif marks >= 50:
        return "⚠️ Average"
    else:
        return "❌ Needs Improvement"

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        action = request.form.get("action")

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        # ➕ ADD
        if action == "add":
            name = request.form.get("name")
            roll = request.form.get("roll")
            dept = request.form.get("dept")
            section = request.form.get("section")

            try:
                marks = int(request.form.get("marks"))

                if marks < 0 or marks > 100:
                    message = "❌ Marks must be 0-100"
                else:
                    cgpa = round(marks / 10, 2)

                    try:
                        cursor.execute("""
                        INSERT INTO students (name, roll, dept, section, marks, cgpa)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (name, roll, dept, section, marks, cgpa))

                        conn.commit()
                        message = "✅ Student added!"
                    except:
                        message = "❌ Roll already exists!"

            except:
                message = "❌ Invalid input!"

        # 🔍 SEARCH
        elif action == "search":
            search_roll = request.form.get("search_roll")
            cursor.execute("SELECT * FROM students WHERE roll=?", (search_roll,))
            data = cursor.fetchall()

            students = []
            for row in data:
                students.append({
                    "name": row[1],
                    "roll": row[2],
                    "dept": row[3],
                    "section": row[4],
                    "marks": row[5],
                    "cgpa": row[6],
                    "report": analyze_performance(row[5])
                })

            conn.close()
            return render_template("index.html", students=students, message="🔍 Search result")

        # 🗑️ DELETE
        elif action == "delete":
            delete_roll = request.form.get("delete_roll")
            cursor.execute("DELETE FROM students WHERE roll=?", (delete_roll,))
            conn.commit()
            message = "🗑️ Student deleted!"

        # ✏️ EDIT
        elif action == "edit":
            edit_roll = request.form.get("edit_roll")

            try:
                new_marks = int(request.form.get("new_marks"))

                if new_marks < 0 or new_marks > 100:
                    message = "❌ Marks must be 0-100"
                else:
                    cgpa = round(new_marks / 10, 2)

                    cursor.execute("""
                    UPDATE students
                    SET marks=?, cgpa=?
                    WHERE roll=?
                    """, (new_marks, cgpa, edit_roll))

                    conn.commit()
                    message = "✏️ Updated!"

            except:
                message = "❌ Invalid marks!"

        conn.close()

    # 📥 FETCH ALL DATA
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    students = []
    for row in data:
        students.append({
            "name": row[1],
            "roll": row[2],
            "dept": row[3],
            "section": row[4],
            "marks": row[5],
            "cgpa": row[6],
            "report": analyze_performance(row[5])
        })

    conn.close()

    return render_template("index.html", students=students, message=message)


if __name__ == "__main__":
    app.run(debug=True)
