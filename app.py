import os
from flask import Flask, render_template, request, redirect, session
import pandas as pd

app = Flask(__name__)
# Lấy secret_key từ biến môi trường, fallback nếu chạy local
app.secret_key = os.environ.get("SECRET_KEY", "fallback-key")  

# Đọc file Excel
df = pd.read_excel("schedule_october_all.xlsx")

# Chuẩn hóa tên: gạch dưới và lowercase
def normalize_username(name):
    return name.lower().replace(" ", "_")

# Tạo dict user: password mặc định 123456
users = {normalize_username(name): "123456" for name in df["Name"].unique()}
users["admin"] = "5671077Aa!"  # Choose a secure password


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    username = session["user"]

    if username == "admin":
        # Admin sees all schedule records
        all_records = df.to_dict(orient="records")
        return render_template("admin.html", records=all_records, name="Admin")

    # Normal user sees only their own schedule
    name_display = " ".join([word.capitalize() for word in username.split("_")])
    filtered_df = df[df["Name"].str.lower() == name_display.lower()]
    records = filtered_df.to_dict(orient="records")

    return render_template("index.html", records=records, name=name_display)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    # Port 10000 chỉ để test local, Render sẽ dùng 10000 hoặc PORT env
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
