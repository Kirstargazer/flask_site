from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")

        if not name or not phone:
            error = "Пожалуйста, заполните имя и телефон."
            return render_template("index.html", error=error)

        with open("leads.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([name, phone])

        print("Сохранено:", name, phone)

        return render_template("success.html", name=name)

    return render_template("index.html", error=error)

@app.route("/admin")
def admin():
    leads = []

    with open("leads.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            leads.append(row)

    return render_template("admin.html", leads=leads)


if __name__ == "__main__":
    app.run(debug=True)