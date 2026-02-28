import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from PIL import Image
from rembg import remove

app = Flask(__name__)
app.secret_key = "styleai_secret"

UPLOAD_FOLDER = "static/uploads"
DRESS_FOLDER = "static/dresses"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        users[request.form["username"]] = request.form["password"]
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


# ---------------- STYLE PAGE ----------------
@app.route("/style", methods=["POST"])
def style():
    file = request.files["photo"]
    dress_name = request.form["dress"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Remove background
    input_image = Image.open(filepath).convert("RGBA")
    output_image = remove(input_image)

    # Load selected dress
    dress_path = os.path.join(DRESS_FOLDER, dress_name)
    dress = Image.open(dress_path).convert("RGBA")

    # Resize dress to fit body width
    body_width = output_image.width
    dress_ratio = dress.height / dress.width
    new_width = int(body_width * 0.8)
    new_height = int(new_width * dress_ratio)
    dress = dress.resize((new_width, new_height))

    # Position dress
    position = (
        int((output_image.width - new_width) / 2),
        int(output_image.height * 0.35)
    )

    # Overlay
    output_image.paste(dress, position, dress)

    result_path = os.path.join(UPLOAD_FOLDER, "result_" + filename)
    output_image.save(result_path)

    return render_template("result.html",
                           result_image="uploads/result_" + filename)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
