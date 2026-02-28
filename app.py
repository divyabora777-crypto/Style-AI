import os
import base64
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "styleai_secret_key"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OpenAI client (uses environment variable OPENAI_API_KEY)
client = OpenAI()

# Simple in-memory user storage
users = {}

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Credentials ❌")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        session["gender"] = request.form["gender"]
        session["style"] = request.form["style"]
        return redirect(url_for("style_page"))

    return render_template("dashboard.html")


# ---------------- STYLE PAGE ----------------
@app.route("/style", methods=["GET", "POST"])
def style_page():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files["photo"]

        if not file:
            return "No file uploaded"

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        gender = session.get("gender")
        style = session.get("style")

        prompt = f"""
        Transform this person into a trendy {style} outfit for a {gender}.
        Apply fashionable clothes.
        Add suitable hairstyle.
        Add soft natural makeup.
        Keep facial identity realistic.
        """

        # Read uploaded image
        with open(filepath, "rb") as image_file:
            image_bytes = image_file.read()

        # IMPORTANT: Use images.edit (NOT generate)
        response = client.images.edit(
            model="gpt-image-1",
            image=image_bytes,
            prompt=prompt
        )

        # Decode generated image
        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        styled_filename = "styled_" + filename
        styled_path = os.path.join(UPLOAD_FOLDER, styled_filename)

        with open(styled_path, "wb") as f:
            f.write(image_bytes)

        return render_template("result.html",
                               user_image=styled_filename)

    return render_template("style.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)