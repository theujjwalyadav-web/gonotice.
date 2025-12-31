from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
import os
import secrets
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- 1. CORE SECURITY TAGS ---
# Cryptographically strong keys for session protection
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(minutes=30)

# Secure Admin Credentials
ADMIN_USER = "UJJWALYADAV"
ADMIN_PASS_HASH = generate_password_hash("ujju@#7391$&4251")

# --- 2. PERSISTENT DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('gonotice.db')
    c = conn.cursor()
    # SQL Injection prevention through prepared schema
    c.execute('''CREATE TABLE IF NOT EXISTS notices 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, pub_time TEXT, start_date TEXT, 
                  last_date TEXT, fee_gen TEXT, fee_sc TEXT,
                  min_age TEXT, max_age TEXT,
                  total_post TEXT, eligibility TEXT, notif_link TEXT)''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- 3. PROFESSIONAL DESIGNS (Sarkari Style) ---

# HOME PAGE
HOME_HTML = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoNotice.in - Sarkari Result 2025</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f4f4f4; }
        .header-main { background: #1a237e; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 22px; }
        .nav-bar { background: #000; color: white; display: flex; justify-content: center; gap: 15px; padding: 10px; font-size: 13px; font-weight: bold; }
        .container { max-width: 1000px; margin: 20px auto; background: white; padding: 15px; border: 1px solid #ddd; }
        .section-title { background: #ff0000; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 18px; margin-bottom: 10px; }
        .job-list { list-style: none; padding: 0; }
        .job-item { border-bottom: 1px dashed #777; padding: 8px; }
        .job-link { color: #d32f2f; text-decoration: none; font-weight: bold; font-size: 15px; }
        .job-link:hover { background: #ffffcc; }
    </style>
</head>
<body>
    <div class="header-main">GoNotice.in</div>
    <div class="nav-bar"><span>HOME</span><span>LATEST JOBS</span><span>ADMIT CARD</span><span>RESULT</span></div>
    <div class="container">
        <div class="section-title">Latest Jobs / Online Form</div>
        <ul class="job-list">
            {% for post in notices %}
            <li class="job-item">
                <a href="/job/{{ post[0] }}" class="job-link">» {{ post[1] }} (Last Date: {{ post[4] }})</a>
            </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
'''

# DETAIL PAGE (Professional Table)
DETAIL_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ job[1] }} - GoNotice.in</title>
    <style>
        body { font-family: Arial; background: #fff; margin: 0; }
        .table-wrap { max-width: 850px; margin: 20px auto; border: 2px solid #000; }
        .header-red { background: #ff0000; color: #fff; text-align: center; padding: 15px; font-size: 22px; font-weight: bold; }
        .header-green { background: #008000; color: #fff; text-align: center; padding: 8px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; }
        td { border: 1px solid #777; padding: 12px; vertical-align: top; }
        .label-red { color: #ff0000; font-weight: bold; display: block; margin-bottom: 5px; text-decoration: underline; }
        .btn { display: inline-block; padding: 12px 30px; background: #0000ff; color: #fff; text-decoration: none; font-weight: bold; border-radius: 4px; margin-top: 10px; }
        .pub-date { text-align: right; font-size: 12px; padding: 5px; color: #555; }
    </style>
</head>
<body>
    <div class="table-wrap">
        <div class="header-red">{{ job[1] }}</div>
        <div class="pub-date">Posted Date: {{ job[2] }}</div>
        <table>
            <tr>
                <td width="50%"><span class="label-red">Important Dates</span>Start: {{ job[3] }}<br>Last Date: {{ job[4] }}</td>
                <td width="50%"><span class="label-red">Application Fee</span>Gen/OBC: ₹{{ job[5] }}<br>SC/ST: ₹{{ job[6] }}</td>
            </tr>
            <tr>
                <td><span class="label-red">Age Limit</span>Min: {{ job[7] }} | Max: {{ job[8] }}</td>
                <td><span class="label-red">Total Vacancy</span><strong>{{ job[9] }} Posts</strong></td>
            </tr>
            <tr><td colspan="2" class="header-green">Educational Eligibility</td></tr>
            <tr><td colspan="2" style="text-align:center; background:#f9f9f9;">{{ job[10] }}</td></tr>
            <tr>
                <td colspan="2" style="text-align:center; padding: 25px;">
                    <a href="{{ job[11] }}" class="btn" target="_blank">Click Here for Official Notification</a>
                </td>
            </tr>
        </table>
    </div>
    <div style="text-align:center; margin-bottom: 50px;"><a href="/">« Back to Home</a></div>
</body>
</html>
'''

ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Secure Admin Panel</title></head>
<body style="font-family:Arial; padding:20px; background:#f5f5f5;">
    <div style="max-width:650px; margin:auto; background:#fff; padding:30px; border-radius:8px; box-shadow:0 0 10px #ccc; border-top:10px solid #1a237e;">
        <h2 style="text-align:center; color:#1a237e;">Post New Job Update</h2>
        <form method="POST">
            <input name="title" placeholder="Notice Title (e.g. BPSC AEDO Exam 2025)" style="width:100%; padding:12px; margin:10px 0; border:1px solid #ddd;" required>
            <div style="display:flex; gap:10px;">
                <input name="start_date" placeholder="Start Date" style="width:50%; padding:10px;">
                <input name="last_date" placeholder="Last Date" style="width:50%; padding:10px;">
            </div>
            <div style="display:flex; gap:10px; margin-top:10px;">
                <input name="fee_gen" placeholder="Gen Fee (₹)" style="width:50%; padding:10px;">
                <input name="fee_sc" placeholder="SC/ST Fee (₹)" style="width:50%; padding:10px;">
            </div>
            <div style="display:flex; gap:10px; margin-top:10px;">
                <input name="min_age" placeholder="Min Age" style="width:50%; padding:10px;">
                <input name="max_age" placeholder="Max Age" style="width:50%; padding:10px;">
            </div>
            <input name="total_post" placeholder="Total Vacancy Count" style="width:100%; padding:10px; margin:10px 0;">
            <textarea name="eligibility" rows="4" style="width:100%; padding:10px; margin:10px 0;">Candidates Must Have Passed 10+2 (Intermediate) From Any Recognized Board In India To Be Eligible.</textarea>
            <input name="notif_link" placeholder="Notification URL (https://...)" style="width:100%; padding:10px; margin:10px 0;">
            <button type="submit" style="width:100%; padding:15px; background:#008000; color:#fff; border:none; font-weight:bold; cursor:pointer;">PUBLISH TO GONOTICE.IN</button>
        </form>
    </div>
</body>
</html>
'''

# --- 4. SECURE ROUTES ---

@app.route('/')
def index():
    conn = sqlite3.connect('gonotice.db')
    c = conn.cursor()
    c.execute("SELECT id, title, pub_time, start_date, last_date FROM notices ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template_string(HOME_HTML, notices=data)

@app.route('/job/<int:id>')
def job_detail(id):
    conn = sqlite3.connect('gonotice.db')
    c = conn.cursor()
    # Using parameterized query to prevent SQL Injection
    c.execute("SELECT * FROM notices WHERE id=?", (id,))
    job = c.fetchone()
    conn.close()
    if job:
        return render_template_string(DETAIL_HTML, job=job)
    return "<h1>Invalid Link: Job Not Found</h1>", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('u') == ADMIN_USER and check_password_hash(ADMIN_PASS_HASH, request.form.get('p')):
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template_string('<body style="text-align:center; padding-top:100px; font-family:Arial; background:#000; color:#fff;"><h2>SECURE ADMIN LOGIN</h2><form method="POST"><input name="u" placeholder="ID" style="padding:10px; margin:10px;"><br><input type="password" name="p" placeholder="Pass" style="padding:10px; margin:10px;"><br><button style="padding:10px 30px; cursor:pointer;">UNLOCK</button></form></body>')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        now = datetime.now().strftime("%B %d, %Y")
        conn = sqlite3.connect('gonotice.db')
        c = conn.cursor()
        c.execute("INSERT INTO notices (title, pub_time, start_date, last_date, fee_gen, fee_sc, min_age, max_age, total_post, eligibility, notif_link) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (request.form.get('title'), now, request.form.get('start_date'), request.form.get('last_date'),
                   request.form.get('fee_gen'), request.form.get('fee_sc'), request.form.get('min_age'),
                   request.form.get('max_age'), request.form.get('total_post'), request.form.get('eligibility'), request.form.get('notif_link')))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template_string(ADMIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Running in production mode to avoid revealing server info
    app.run(debug=False)
