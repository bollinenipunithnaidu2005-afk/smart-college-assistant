from flask import Flask, render_template, request
import os

app = Flask(__name__)

FILE_NAME = "students.txt"


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    students = []
    topper = None
    average = None

    # ✅ Safe file reading
    try:
        with open(FILE_NAME, "r") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                parts = line.split(",")

                if len(parts) != 3:
                    continue

                name, roll, marks = parts

                try:
                    marks = int(marks)
                except:
                    continue

                students.append({
                    "name": name,
                    "roll": roll,
                    "marks": marks
                })
    except:
        pass

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            name = request.form.get("name")
            roll = request.form.get("roll")

            try:
                marks = int(request.form.get("marks"))
            except:
                message = "❌ Invalid marks!"
                return render_template("index.html", message=message, students=students)

            # Duplicate check
            for s in students:
                if s["roll"] == roll:
                    message = "❌ Roll number already exists!"
                    return render_template("index.html", message=message, students=students)

            # Save data
            try:
                with open(FILE_NAME, "a+") as file:
                    file.write(f"{name},{roll},{marks}\n")
                message = "✅ Student added!"
            except:
                message = "❌ Error saving data!"

        elif action == "topper":
            if students:
                topper = max(students, key=lambda x: x["marks"])

        elif action == "analysis":
            if students:
                total = sum(s["marks"] for s in students)
                average = total / len(students)

    return render_template(
        "index.html",
        message=message,
        students=students,
        topper=topper,
        average=average
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)