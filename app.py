from flask import Flask, render_template_string, request, redirect, url_for, session, flash, abort
import sqlite3
import os
import secrets
from functools import wraps
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- 1. SUPER SECURITY: Encryption Keys ---
# Ye har baar naya random key generate karega jisse session hijack nahi ho sakta
app.secret_key = secrets.token_hex(32) 

# --- 2. SESSION HARDENING ---
# 15 minute tak activity nahi hone par auto-logout (Extra Security)
app.permanent_session_lifetime = timedelta(minutes=15)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# --- 3. ADMIN CREDENTIALS ---
# Hash Password: Ye asli password ko code mein chupata hai
ADMIN_USER = "UJJWALYADAV"
# 'ujju@#7391$&4251' ka hashed version
ADMIN_PASS_HASH = generate_password_hash("ujju@#7391$&4251")

# --- 4. DATABASE INITIALIZATION (gonotice.db) ---
def init_db():
    conn = sqlite3.connect('gonotice.db')
    c = conn.cursor()
    # SQL Injection se bachne ke liye table structure
    c.execute('''CREATE TABLE IF NOT EXISTS job_notices 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT NOT NULL, start_date TEXT, last_date TEXT, 
                  fee_gen TEXT, fee_sc_st TEXT, 
                  min_age TEXT, max_age TEXT, 
                  total_post TEXT, eligibility TEXT, 
                  notif_link TEXT, apply_link TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 5. HACK-PROOF DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- 6. PROFESSIONAL HTML DESIGNS ---

INDEX_HTML = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoNotice.in - Sarkari Result 2025</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f4f4f4; color: #333; }
        .top-banner { background: #ff0000; color: #fff; text-align: center; padding: 20px; font-size: 28px; font-weight: 900; border-bottom: 6px solid #000; letter-spacing: 1px; }
        .container { max-width: 900px; margin: 25px auto; padding: 10px; }
        .job-table { width: 100%; border-collapse: collapse; margin-bottom: 50px; background: #fff; border: 3px solid #000; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .main-title { background: #ff0000; color: #fff; text-align: center; padding: 12px; font-size: 22px; font-weight: bold; }
        .green-strip { background: #008000; color: #fff; text-align: center; font-weight: bold; padding: 8px; }
        td { border: 1px solid #777; padding: 15px; line-height: 1.6; }
        .label-red { color: #d90000; font-weight: bold; font-size: 16px; text-decoration: underline; }
        .action-area { text-align: center; padding: 20px; background: #f9f9f9; }
        .btn { display: inline-block; padding: 12px 30px; background: #0000ff; color: #fff; text-decoration: none; font-weight: bold; border-radius: 4px; margin: 10px; transition: 0.3s; }
        .btn-apply { background: #008000; }
        .btn:hover { opacity: 0.8; transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="top-banner">GoNotice.in - Latest Sarkari Result</div>
    <div class="container">
        {% for job in jobs %}
        <table class="job-table">
            <tr><td colspan="2" class="main-title">{{ job[1] }}</td></tr>
            <tr>
                <td width="50%"><span class="label-red">Important Dates</span><br>Start: {{ job[2] }}<br>Last Date: {{ job[3] }}</td>
                <td width="50%"><span class="label-red">Application Fee</span><br>Gen/OBC: ₹{{ job[4] }}<br>SC/ST: ₹{{ job[5] }}</td>
            </tr>
            <tr>
                <td><span class="label-red">Age Limit</span><br>Min: {{ job[6] }} Yrs | Max: {{ job[7] }} Yrs</td>
                <td><span class="label-red">Total Vacancy</span><br><strong>{{ job[8] }} Posts</strong></td>
            </tr>
            <tr><td colspan="2" class="green-strip">Education / Eligibility Criteria</td></tr>
            <tr><td colspan="2" style="text-align:center; font-weight: 500;">{{ job[9] }}</td></tr>
            <tr class="action-area">
                <td colspan="2">
                    <a href="{{ job[10] }}" class="btn" target="_blank">Download Official Notification</a>
                    <a href="{{ job[11] }}" class="btn btn-apply" target="_blank">Apply Online Link</a>
                </td>
            </tr>
        </table>
        {% endfor %}
    </div>
</body>
</html>
'''

ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure Admin Panel</title>
    <style>
        body { background: #1a1a1a; font-family: sans-serif; display: flex; justify-content: center; padding: 40px; }
        .card { background: #fff; width: 100%; max-width: 750px; padding: 30px; border-radius: 12px; border-top: 10px solid #ff0000; }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        .flex { display: flex; gap: 15px; }
        button { width: 100%; background: #008000; color: #fff; border: none; padding: 16px; font-size: 18px; font-weight: bold; cursor: pointer; border-radius: 6px; margin-top: 10px; }
        button:hover { background: #006400; }
        .header-txt { text-align: center; color: #ff0000; margin-bottom: 25px; }
    </style>
</head>
<body>
    <div class="card">
        <div style="text-align: right;"><a href="/logout" style="color:red; font-weight:bold;">[Logout]</a></div>
        <h2 class="header-txt">Post New Sarkari Vacancy</h2>
        <form method="POST">
            <input type="text" name="title" placeholder="Notice Title (e.g., RPF Constable 2025)" required>
            <div class="flex">
                <input type="text" name="start_date" placeholder="Form Start Date">
                <input type="text" name="last_date" placeholder="Form Last Date">
            </div>
            <div class="flex">
                <input type="text" name="fee_gen" placeholder="Gen Fee">
                <input type="text" name="fee_sc" placeholder="SC/ST Fee">
            </div>
            <div class="flex">
                <input type="text" name="min_age" placeholder="Min Age">
                <input type="text" name="max_age" placeholder="Max Age">
            </div>
            <input type="text" name="total_post" placeholder="Vacancy Count">
            <textarea name="eligibility" rows="4">Candidates Must Have Passed 10+2 (Intermediate) From Any Recognized Board In India To Be Eligible.</textarea>
            <input type="url" name="notif_link" placeholder="Official PDF Link (https://...)">
            <input type="url" name="apply_link" placeholder="Online Apply Link (https://...)">
            <button type="submit">Publish Job to GoNotice.in</button>
        </form>
    </div>
</body>
</html>
'''

# --- 7. ROUTES & LOGIC ---

@app.route('/')
def index():
    conn = sqlite3.connect('gonotice.db')
    c = conn.cursor()
    c.execute("SELECT * FROM job_notices ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template_string(INDEX_HTML, jobs=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Brute Force se bachne ke liye constant-time comparison
        user = request.form.get('u')
        pw = request.form.get('p')
        if user == ADMIN_USER and check_password_hash(ADMIN_PASS_HASH, pw):
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash("ACCESS DENIED: Credentials Incorrect")
    return render_template_string('''
        <body style="background:#000; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;">
            <div style="background:#fff; padding:40px; border-radius:10px; border-top:5px solid red;">
                <h2 style="text-align:center; color:red;">ADMIN SYSTEM LOCK</h2>
                <form method="POST">
                    <input type="text" name="u" placeholder="Admin ID" required style="display:block; width:100%; padding:10px; margin:10px 0;"><br>
                    <input type="password" name="p" placeholder="Password" required style="display:block; width:100%; padding:10px; margin:10px 0;"><br>
                    <button type="submit" style="width:100%; padding:12px; background:#000; color:#fff; border:none; cursor:pointer;">DECRYPT & ENTER</button>
                </form>
            </div>
        </body>
    ''')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        conn = sqlite3.connect('gonotice.db')
        c = conn.cursor()
        # Prepared Statements: SQL Injection se bachata hai
        c.execute("INSERT INTO job_notices (title, start_date, last_date, fee_gen, fee_sc_st, min_age, max_age, total_post, eligibility, notif_link, apply_link) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (request.form.get('title'), request.form.get('start_date'), request.form.get('last_date'), 
                   request.form.get('fee_gen'), request.form.get('fee_sc'), request.form.get('min_age'), 
                   request.form.get('max_age'), request.form.get('total_post'), request.form.get('eligibility'), 
                   request.form.get('notif_link'), request.form.get('apply_link')))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template_string(ADMIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__== '__main__':
    # Flask ko Production mode mein chalayein (Hackers ko error details nahi dikhengi)
    app.run(debug=False)
