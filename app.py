from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "my_secret_key_123"


def init_db():
    connection = sqlite3.connect("leads.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")

        if not name or not phone:
            error = "Пожалуйста, заполните имя и телефон."
            return render_template("index.html", error=error)

        connection = sqlite3.connect("leads.db")
        cursor = connection.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO leads (name, phone, created_at)
            VALUES (?, ?, ?)
            """,
            (name, phone, created_at)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("success", name=name))

    return render_template("index.html", error=error)


@app.route("/success")
def success():
    name = request.args.get("name")
    return render_template("success.html", name=name)


@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    connection = sqlite3.connect("leads.db")
    cursor = connection.cursor()

    if search:
        cursor.execute(
            """
            SELECT id, name, phone, created_at
            FROM leads
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            """,
            (f"%{search}%", f"%{search}%")
        )
    else:
        cursor.execute(
            """
            SELECT id, name, phone, created_at
            FROM leads
            ORDER BY id DESC
            """
        )

    leads = cursor.fetchall()
    connection.close()

    return render_template(
        "admin.html",
        leads=leads,
        search=search
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "12345":
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Неверный логин или пароль."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/delete/<int:lead_id>", methods=["POST"])
def delete_lead(lead_id):
    connection = sqlite3.connect("leads.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))

@app.route("/edit/<int:lead_id>", methods=["GET", "POST"])
def edit_lead(lead_id):
    connection = sqlite3.connect("leads.db")
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")

        cursor.execute(
            "UPDATE leads SET name = ?, phone = ? WHERE id = ?",
            (name, phone, lead_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    cursor.execute("SELECT id, name, phone, created_at FROM leads WHERE id = ?", (lead_id,))
    lead = cursor.fetchone()

    connection.close()

    return render_template("edit.html", lead=lead)


if __name__ == "__main__":
    app.run(debug=True)