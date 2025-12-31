from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "gonotice_final_v1"

# --- Database Setup (Clean & Updated) ---
def init_db():
    conn = sqlite3.connect('go_notice.db')
    c = conn.cursor()
    # EWS added, PH removed from SC/ST
    c.execute('''CREATE TABLE IF NOT EXISTS notices 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  category TEXT, title TEXT, 
                  start_date TEXT, last_date TEXT, fee_pay_last TEXT,
                  fee_gen_obc_ews TEXT, fee_sc_st TEXT, 
                  min_age TEXT, max_age TEXT, total_post TEXT,
                  eligibility TEXT, apply_link TEXT)''')
    conn.commit()
    conn.close()

init_db()

ADMIN_USER = "admin"
ADMIN_PASS = "pass123"

# --- Master UI Design (GoNotice.in Branding) ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoNotice.in - Latest Sarkari Jobs, Results, Admit Card</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f4f4; font-family: 'Verdana', sans-serif; }
        .top-header { background-color: #ff0000; color: white; text-align: center; padding: 15px; border-bottom: 5px solid #000080; }
        .top-header h1 { margin: 0; font-weight: bold; letter-spacing: 1px; }
        .main-nav { background-color: #000080; padding: 8px; text-align: center; }
        .main-nav a { color: white; text-decoration: none; margin: 0 10px; font-weight: bold; font-size: 13px; }
        .main-nav a:hover { color: #ffff00; }
        
        /* Table Styles from your photos */
        .job-table { width: 100%; border: 1px solid #000; background: #fff; margin-bottom: 20px; border-collapse: collapse; }
        .job-table td { border: 1px solid #777; padding: 10px; font-size: 14px; }
        .header-row { background: #000080; color: white; text-align: center; font-weight: bold; font-size: 16px; }
        .sub-header { background: #ff0000; color: white; text-align: center; font-weight: bold; }
        .label { font-weight: bold; color: #000080; }
        .post-title { color: #ff0000; font-weight: bold; text-align: center; padding: 10px; font-size: 22px; border-bottom: 2px solid #000; margin-bottom: 15px; }
        
        .box { border: 2px solid #000080; min-height: 450px; background: white; margin-bottom: 20px; }
        .box-head { background: #000080; color: white; padding: 8px; text-align: center; font-weight: bold; font-size: 18px; }
        .job-link { color: #d00; text-decoration: none; font-weight: bold; display: block; padding: 8px; border-bottom: 1px dashed #ccc; font-size: 13px; }
        .job-link:hover { background: #f9f9f9; color: blue; }
        
        footer { background: #333; color: white; text-align: center; padding: 20px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="top-header">
        <h1>GO NOTICE</h1>
        <p style="margin:0;">WWW.GONOTICE.IN</p>
    </div>
    <div class="main-nav">
        <a href="/">HOME</a>
        <a href="/category/Latest Job">LATEST JOBS</a>
        <a href="/category/Admit Card">ADMIT CARD</a>
        <a href="/category/Result">RESULT</a>
    </div>

    <div class="container mt-3">
        {% if mode == 'home' %}
            <div class="row">
                {% for cat in ['Result', 'Admit Card', 'Latest Job'] %}
                <div class="col-md-4">
                    <div class="box">
                        <div class="box-head">{{ cat }}</div>
                        {% for item in data if item[1] == cat %}
                        <a href="/notice/{{ item[0] }}" class="job-link">{{ item[2] }}</a>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>

        {% elif mode == 'category_view' %}
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="box">
                        <div class="box-head">{{ selected_cat }} Updates</div>
                        {% for item in data %}
                        <a href="/notice/{{ item[0] }}" class="job-link">{{ item[2] }}</a>
                        {% else %}
                        <p class="p-3 text-center">Stay tuned for updates!</p>
                        {% endfor %}
                    </div>
                </div>
            </div>

        {% elif mode == 'detail' %}
            <div class="card p-3 shadow-sm bg-white">
                <div class="post-title">{{ item[2] }}</div>
                <table class="job-table">
                    <tr class="header-row"><td colspan="2">Important Dates & Application Fee</td></tr>
                    <tr>
                        <td width="50%">
                            <span class="label">Apply Start:</span> {{ item[3] }}<br>
                            <span class="label">Last Date:</span> <span class="text-danger">{{ item[4] }}</span><br>
                            <span class="label">Fee Last Date:</span> {{ item[5] }}
                        </td>
                        <td>
                            <span class="label">Gen / OBC / EWS :</span> <span class="text-danger">Rs. {{ item[6] }}/-</span><br>
                            <span class="label">SC / ST :</span> <span class="text-danger">Rs. {{ item[7] }}/-</span><br>
                            <span class="label">Mode:</span> Online
                        </td>
                    </tr>
                    <tr class="sub-header"><td colspan="2">Age Limit As On {{ item[4] }}</td></tr>
                    <tr class="text-center">
                        <td colspan="2">
                            <span class="label">Minimum Age:</span> {{ item[8] }} Years | 
                            <span class="label">Maximum Age:</span> {{ item[9] }} Years
                        </td>
                    </tr>
                    <tr class="sub-header"><td colspan="2">Vacancy Details: Total {{ item[10] }} Post</td></tr>
                    <tr><td colspan="2" class="text-center"><span class="label">Eligibility:</span> {{ item[11] }}</td></tr>
                    <tr class="header-row"><td colspan="2">Useful Important Links</td></tr>
                    
                    {% if item[1] == 'Latest Job' %}
                    <tr class="text-center"><td><span class="label">Apply Online Link</span></td><td><a href="{{ item[12] }}" target="_blank" class="btn btn-primary btn-sm">Click Here</a></td></tr>
                    {% elif item[1] == 'Admit Card' %}
                    <tr class="text-center"><td><span class="label">Download Admit Card</span></td><td><a href="{{ item[12] }}" target="_blank" class="btn btn-success btn-sm">Click Here</a></td></tr>
                    <tr class="text-center"><td><span class="label">Check Exam City/Date</span></td><td><a href="{{ item[12] }}" target="_blank" class="btn btn-info btn-sm">Click Here</a></td></tr>
                    {% elif item[1] == 'Result' %}
                    <tr class="text-center"><td><span class="label">Download Result</span></td><td><a href="{{ item[12] }}" target="_blank" class="btn btn-danger btn-sm">Click Here</a></td></tr>
                    {% endif %}
                </table>
                <div class="text-center mt-3"><a href="/" class="btn btn-dark">Back to Home</a></div>
            </div>

        {% elif mode == 'admin' %}
            <div class="card p-4">
                <h4>GoNotice.in - Admin Panel</h4>
                <form method="POST" class="row g-2">
                    <div class="col-md-4"><select name="cat" class="form-select"><option>Latest Job</option><option>Admit Card</option><option>Result</option></select></div>
                    <div class="col-md-8"><input name="title" placeholder="Notice Title" class="form-control" required></div>
                    <div class="col-md-4"><input name="start" placeholder="Apply Start" class="form-control"></div>
                    <div class="col-md-4"><input name="last" placeholder="Apply Last Date" class="form-control"></div>
                    <div class="col-md-4"><input name="f_last" placeholder="Fee Last Date" class="form-control"></div>
                    <div class="col-md-6"><input name="f_gen" placeholder="Fee (Gen/OBC/EWS)" class="form-control"></div>
                    <div class="col-md-6"><input name="f_sc" placeholder="Fee (SC/ST)" class="form-control"></div>
                    <div class="col-md-3"><input name="min" placeholder="Min Age" class="form-control"></div>
                    <div class="col-md-3"><input name="max" placeholder="Max Age" class="form-control"></div>
                    <div class="col-md-3"><input name="total" placeholder="Total Posts" class="form-control"></div>
                    <div class="col-md-3"><input name="link" placeholder="Main Link" class="form-control"></div>
                    <div class="col-12"><textarea name="elig" placeholder="Eligibility Detail" class="form-control" rows="3"></textarea></div>
                    <button class="btn btn-success">Publish Now</button>
                </form>
                <hr>
                <table class="table mt-2">
                    {% for i in data %}
                    <tr><td>{{ i[2] }} ({{ i[1] }})</td><td><a href="/delete/{{ i[0] }}" class="btn btn-danger btn-sm">Delete</a></td></tr>
                    {% endfor %}
                </table>
                <a href="/logout" class="btn btn-dark btn-sm">Logout</a>
            </div>
        {% elif mode == 'login' %}
            <div class="mt-5 text-center"><form method="POST" class="card p-4 mx-auto" style="max-width:320px;"><h4>Admin Login</h4><input name="user" class="form-control mb-2"><input name="pass" type="password" class="form-control mb-2"><button class="btn btn-primary w-100">Login</button></form></div>
        {% endif %}
    </div>

    <footer>
        <p>© 2025 GoNotice.in - All Rights Reserved</p>
        <p>Follow us on Telegram | WhatsApp | Facebook</p>
    </footer>
</body>
</html>
"""

# --- All Routes ---
@app.route('/')
def home():
    conn = sqlite3.connect('sarkari_notice.db')
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(HTML_LAYOUT, mode='home', data=data)

@app.route('/category/<cat_name>')
def category_filter(cat_name):
    conn = sqlite3.connect('sarkari_notice.db')
    data = conn.execute("SELECT * FROM notices WHERE category = ? ORDER BY id DESC", (cat_name,)).fetchall()
    conn.close()
    return render_template_string(HTML_LAYOUT, mode='category_view', data=data, selected_cat=cat_name)

@app.route('/notice/<int:id>')
def detail(id):
    conn = sqlite3.connect('sarkari_notice.db')
    item = conn.execute("SELECT * FROM notices WHERE id = ?", (id,)).fetchone()
    conn.close()
    if item: return render_template_string(HTML_LAYOUT, mode='detail', item=item)
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = sqlite3.connect('sarkari_notice.db')
    if request.method == 'POST':
        vals = (request.form['cat'], request.form['title'], request.form['start'], request.form['last'], 
                request.form['f_last'], request.form['f_gen'], request.form['f_sc'], 
                request.form['min'], request.form['max'], request.form['total'], 
                request.form['elig'], request.form['link'])
        conn.execute("INSERT INTO notices (category,title,start_date,last_date,fee_pay_last,fee_gen_obc_ews,fee_sc_st,min_age,max_age,total_post,eligibility,apply_link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", vals)
        conn.commit()
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(HTML_LAYOUT, mode='admin', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == ADMIN_USER and request.form['pass'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template_string(HTML_LAYOUT, mode='login')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('logged_in'):
        conn = sqlite3.connect('sarkari_notice.db')
        conn.execute("DELETE FROM notices WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
