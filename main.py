from flask import Flask, render_template, request

app = Flask(__name__)

FILE_NAME = "students.txt"

@app.route("/", methods=["GET", "POST"])
def home():
    students = []
    message = ""
    topper = None

    # 📥 Read file
    try:
        with open(FILE_NAME, "r") as file:
            for line in file:
                try:
                    name, roll, marks = line.strip().split(",")
                    students.append({
                        "name": name,
                        "roll": roll,
                        "marks": int(marks)
                    })
                except:
                    continue
    except FileNotFoundError:
        pass

    # 🔥 HANDLE FORM
    if request.method == "POST":
        action = request.form.get("action")

        # ➕ ADD STUDENT
        if action == "add":
            name = request.form.get("name")
            roll = request.form.get("roll")

            try:
                marks = int(request.form.get("marks"))
                if marks < 0:
                    message = "❌ Marks cannot be negative!"
                    return render_template("index.html", students=students, message=message)
            except:
                message = "❌ Invalid marks!"
                return render_template("index.html", students=students, message=message)

            # Duplicate check
            for s in students:
                if s["roll"] == roll:
                    message = "❌ Roll already exists!"
                    return render_template("index.html", students=students, message=message)

            with open(FILE_NAME, "a") as file:
                file.write(f"{name},{roll},{marks}\n")

            message = "✅ Student added!"

        # 🔍 SEARCH
        elif action == "search":
            search_roll = request.form.get("search_roll")
            students = [s for s in students if s["roll"] == search_roll]

        # 🗑️ DELETE
        elif action == "delete":
            delete_roll = request.form.get("delete_roll")

            new_data = []
            for s in students:
                if s["roll"] != delete_roll:
                    new_data.append(f"{s['name']},{s['roll']},{s['marks']}")

            with open(FILE_NAME, "w") as file:
                for line in new_data:
                    file.write(line + "\n")

            message = "🗑️ Student deleted!"

        # ✏️ EDIT
        elif action == "edit":
            edit_roll = request.form.get("edit_roll")

            try:
                new_marks = int(request.form.get("new_marks"))
                if new_marks < 0:
                    message = "❌ Marks cannot be negative!"
                    return render_template("index.html", students=students, message=message)
            except:
                message = "❌ Invalid marks!"
                return render_template("index.html", students=students, message=message)

            new_data = []

            for s in students:
                if s["roll"] == edit_roll:
                    new_data.append(f"{s['name']},{s['roll']},{new_marks}")
                else:
                    new_data.append(f"{s['name']},{s['roll']},{s['marks']}")

            with open(FILE_NAME, "w") as file:
                for line in new_data:
                    file.write(line + "\n")

            message = "✏️ Marks updated!"

        # 🏆 TOPPER
        elif action == "topper":
            if students:
                topper = max(students, key=lambda x: x["marks"])

        # 📊 ANALYSIS + CGPA
        elif action == "analysis":
            if students:
                total = sum(s["marks"] for s in students)
                average = total / len(students)

                for s in students:
                    s["cgpa"] = round(s["marks"] / 10, 2)

                message = f"📊 Average Marks: {round(average, 2)}"

    return render_template("index.html", students=students, message=message, topper=topper)


if __name__ == "__main__":
    app.run(debug=True)
