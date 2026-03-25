from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# 🔥 INIT DB
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

# 🔍 PERFORMANCE
def analyze(avg):
    if avg >= 90:
        return "🌟 Excellent"
    elif avg >= 75:
        return "👍 Good"
    elif avg >= 50:
        return "⚠️ Average"
    else:
        return "❌ Improve"

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        action = request.form.get("action")

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        # ➕ ADD STUDENT
        if action == "add":
            name = request.form.get("name")
            roll = request.form.get("roll")
            dept = request.form.get("dept")
            section = request.form.get("section")
            subjects = int(request.form.get("subjects"))
            marks_input = request.form.get("marks")

            try:
                marks_list = list(map(int, marks_input.split(",")))

                if len(marks_list) != subjects:
                    message = "❌ Subjects & marks count mismatch"
                elif any(m < 0 or m > 100 for m in marks_list):
                    message = "❌ Marks must be 0-100"
                else:
                    avg = sum(marks_list) / subjects
                    cgpa = round(avg / 10, 2)

                    try:
                        cursor.execute("""
                        INSERT INTO students (name, roll, dept, section, subjects, marks, cgpa)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (name, roll, dept, section, subjects, marks_input, cgpa))

                        conn.commit()
                        message = "✅ Added successfully!"
                    except:
                        message = "❌ Roll already exists"

            except:
                message = "❌ Invalid marks format"

        # 🔍 SEARCH
        elif action == "search":
            roll = request.form.get("search_roll")
            cursor.execute("SELECT * FROM students WHERE roll=?", (roll,))
            data = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM students")
            data = cursor.fetchall()

        # 🗑️ DELETE
        if action == "delete":
            roll = request.form.get("delete_roll")
            cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
            conn.commit()
            message = "🗑️ Deleted"

        # ✏️ EDIT
        if action == "edit":
            roll = request.form.get("edit_roll")
            marks_input = request.form.get("new_marks")

            try:
                marks_list = list(map(int, marks_input.split(",")))
                avg = sum(marks_list) / len(marks_list)
                cgpa = round(avg / 10, 2)

                cursor.execute("""
                UPDATE students SET marks=?, cgpa=?
                WHERE roll=?
                """, (marks_input, cgpa, roll))

                conn.commit()
                message = "✏️ Updated"
            except:
                message = "❌ Error updating"

        conn.close()

    else:
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        data = cursor.fetchall()
        conn.close()

    # 📊 PROCESS DATA
    students = []
    section_count = {}

    for row in data:
        avg = sum(map(int, row[6].split(","))) / row[5]

        key = f"{row[3]}-{row[4]}"
        section_count[key] = section_count.get(key, 0) + 1

        students.append({
            "name": row[1],
            "roll": row[2],
            "dept": row[3],
            "section": row[4],
            "subjects": row[5],
            "marks": row[6],
            "cgpa": row[7],
            "report": analyze(avg)
        })

    return render_template("index.html",
                           students=students,
                           message=message,
                           section_count=section_count)

if __name__ == "__main__":
    app.run(debug=True)
