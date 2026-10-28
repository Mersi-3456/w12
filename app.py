
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")

    if not name:
        return "Username cannot be empty", 400

    if not password:
        return "Password cannot be empty", 400

    if len(password) < 6:
        return "Password must be at least 6 characters long", 400

    return render_template("successful.html", name=name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)