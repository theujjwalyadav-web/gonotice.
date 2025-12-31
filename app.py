from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24) 
app.permanent_session_lifetime = timedelta(minutes=30)

# Admin Details
ADMIN_USER = "UJJWALYADAV"
ADMIN_PASS = "ujju@#7391$&4251" 

# Database Setup (All columns included)
def init_db():
    conn = sqlite3.connect('sarkari_notice.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS notices 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  category TEXT, title TEXT, 
                  start_date TEXT, last_date TEXT, fee_pay_last TEXT,
                  fee_gen_obc_ews TEXT, fee_sc_st TEXT, 
                  min_age TEXT, max_age TEXT, total_post TEXT,
                  eligibility TEXT, apply_link TEXT, notification_link TEXT)''')
    conn.commit()
    conn.close()

init_db()

# UI Layout (Home screen kept original)
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoNotice.in - Fast Latest Jobs, Admit Card & Results</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f4f4; font-family: 'Verdana', sans-serif; }
        .top-header { background-color: #ff0000; color: white; text-align: center; padding: 15px; border-bottom: 5px solid #000080; }
        .top-header h1 { margin: 0; font-weight: bold; }
        .main-nav { background-color: #000080; padding: 8px; text-align: center; }
        .main-nav a { color: white; text-decoration: none; margin: 0 10px; font-weight: bold; font-size: 13px; }
        .main-nav a:hover { color: #ffff00; }
        
        .job-table { width: 100%; border: 1px solid #000; background: #fff; margin-bottom: 20px; border-collapse: collapse; }
        .job-table td { border: 1px solid #777; padding: 10px; font-size: 14px; }
        .header-row { background: #000080; color: white; text-align: center; font-weight: bold; font-size: 16px; }
        .sub-header { background: #ff0000; color: white; text-align: center; font-weight: bold; }
        .label { font-weight: bold; color: #000080; }
        .post-title { color: #ff0000; font-weight: bold; text-align: center; padding: 10px; font-size: 22px; border-bottom: 2px solid #000; margin-bottom: 15px; }
        
        .box { border: 2px solid #000080; min-height: 450px; background: white; margin-bottom: 20px; }
        .box-head { background: #000080; color: white; padding: 8px; text-align: center; font-weight: bold; font-size: 18px; }
        .job-link { color: #d00; text-decoration: none; font-weight: bold; display: block; padding: 8px; border-bottom: 1px dashed #ccc; font-size: 13px; }
        footer { background: #333; color: white; text-align: center; padding: 20px; margin-top: 30px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="top-header"><h1>GO NOTICE</h1><p>WWW.GONOTICE.IN</p></div>
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

        {% elif mode == 'detail' %}
            <div class="card p-3 shadow-sm bg-white">
                <div class="post-title">{{ item[2] }}</div>
                <table class="job-table">
                    <tr class="header-row"><td colspan="2">Important Dates & Application Fee</td></tr>
                    <tr>
                        <td width="50%">
                            <span class="label">Apply Start:</span> {{ item[3] }}<br>
                            <span class="label">Last Date:</span> <span class="text-danger">{{ item[4] }}</span>
                        </td>
                        <td>
                            <span class="label">Gen / OBC / EWS :</span> Rs. {{ item[6] }}/-<br>
                            <span class="label">SC / ST :</span> Rs. {{ item[7] }}/-
                        </td>
                    </tr>
                    <tr class="header-row"><td colspan="2">Vacancy Details & Eligibility</td></tr>
                    <tr class="sub-header"><td>Post Name & Total</td><td>Eligibility Details</td></tr>
                    <tr>
                        <td class="text-center align-middle"><b>Total: {{ item[10] }} Posts</b></td>
                        <td>
                            <ul style="margin:0; padding-left:20px;">
                                {% for line in item[11].split('\\n') if line.strip() %}
                                <li>{{ line.strip() }}</li>
                                {% endfor %}
                            </ul>
                        </td>
                    </tr>
                    <tr class="header-row"><td colspan="2">Important Links</td></tr>
                    <tr class="text-center"><td><span class="label">Download Notification</span></td><td><a href="{{ item[13] }}" target="_blank" class="btn btn-warning btn-sm">Click Here</a></td></tr>
                    <tr class="text-center"><td><span class="label">Apply Online / Result</span></td><td><a href="{{ item[12] }}" target="_blank" class="btn btn-primary btn-sm">Click Here</a></td></tr>
                </table>
                <div class="text-center mt-3"><a href="/" class="btn btn-dark btn-sm">Back to Home</a></div>
            </div>

        {% elif mode == 'admin' %}
            <div class="card p-4 shadow">
                <h4 class="text-primary">{% if edit_item %}Edit Notice{% else %}Add New Notice{% endif %}</h4>
                <form method="POST" action="{% if edit_item %}/edit/{{ edit_item[0] }}{% else %}/admin{% endif %}">
                    <div class="row g-2">
                        <div class="col-md-4"><select name="cat" class="form-select">
                            <option {% if edit_item and edit_item[1]=='Latest Job' %}selected{% endif %}>Latest Job</option>
                            <option {% if edit_item and edit_item[1]=='Admit Card' %}selected{% endif %}>Admit Card</option>
                            <option {% if edit_item and edit_item[1]=='Result' %}selected{% endif %}>Result</option>
                        </select></div>
                        <div class="col-md-8"><input name="title" value="{{ edit_item[2] if edit_item }}" placeholder="Job Title" class="form-control" required></div>
                        <div class="col-md-3"><input name="start" value="{{ edit_item[3] if edit_item }}" placeholder="Start Date" class="form-control"></div>
                        <div class="col-md-3"><input name="last" value="{{ edit_item[4] if edit_item }}" placeholder="Last Date" class="form-control"></div>
                        <div class="col-md-3"><input name="f_gen" value="{{ edit_item[6] if edit_item }}" placeholder="Fee Gen/OBC" class="form-control"></div>
                        <div class="col-md-3"><input name="f_sc" value="{{ edit_item[7] if edit_item }}" placeholder="Fee SC/ST" class="form-control"></div>
                        <div class="col-md-4"><input name="total" value="{{ edit_item[10] if edit_item }}" placeholder="Total Posts" class="form-control"></div>
                        <div class="col-md-4"><input name="link" value="{{ edit_item[12] if edit_item }}" placeholder="Action URL" class="form-control"></div>
                        <div class="col-md-4"><input name="n_link" value="{{ edit_item[13] if edit_item }}" placeholder="Notification PDF Link" class="form-control"></div>
                        <div class="col-12"><textarea name="elig" placeholder="Eligibility (Enter for new point)" class="form-control" rows="4">{{ edit_item[11] if edit_item }}</textarea></div>
                    </div>
                    <button class="btn btn-success mt-2 w-100">{% if edit_item %}Update Changes{% else %}Publish Notice{% endif %}</button>
                </form>
                <hr>
                <h5>Recent Posts (Manage)</h5>
                <div class="table-responsive">
                    <table class="table table-sm table-bordered">
                        <thead><tr><th>Title</th><th>Actions</th></tr></thead>
                        <tbody>
                            {% for i in data %}
                            <tr><td>{{ i[2] }}</td><td><a href="/edit/{{ i[0] }}">Edit</a> | <a href="/delete/{{ i[0] }}" class="text-danger">Delete</a></td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        {% elif mode == 'login' %}
            <div class="mt-5 text-center">
                <form method="POST" class="card p-4 mx-auto shadow" style="max-width:350px;">
                    <h4 class="mb-3">Admin Login</h4>
                    <input name="user" placeholder="Username" class="form-control mb-2" required>
                    <input name="pass" type="password" placeholder="Password" class="form-control mb-3" required>
                    <button class="btn btn-primary w-100">Login</button>
                </form>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect('sarkari_notice.db')
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(HTML_LAYOUT, mode='home', data=data)

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
        vals = (request.form['cat'], request.form['title'], request.form['start'], request.form['last'], "", 
                request.form['f_gen'], request.form['f_sc'], "", "", request.form['total'], 
                request.form['elig'], request.form['link'], request.form['n_link'])
        conn.execute("INSERT INTO notices (category,title,start_date,last_date,fee_pay_last,fee_gen_obc_ews,fee_sc_st,min_age,max_age,total_post,eligibility,apply_link,notification_link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", vals)
        conn.commit()
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(HTML_LAYOUT, mode='admin', data=data)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = sqlite3.connect('sarkari_notice.db')
    if request.method == 'POST':
        vals = (request.form['cat'], request.form['title'], request.form['start'], request.form['last'], 
                request.form['f_gen'], request.form['f_sc'], request.form['total'], 
                request.form['elig'], request.form['link'], request.form['n_link'], id)
        conn.execute("UPDATE notices SET category=?, title=?, start_date=?, last_date=?, fee_gen_obc_ews=?, fee_sc_st=?, total_post=?, eligibility=?, apply_link=?, notification_link=? WHERE id=?", vals)
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    
    edit_item = conn.execute("SELECT * FROM notices WHERE id = ?", (id,)).fetchone()
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(HTML_LAYOUT, mode='admin', data=data, edit_item=edit_item)

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('logged_in'):
        conn = sqlite3.connect('sarkari_notice.db')
        conn.execute("DELETE FROM notices WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form['user'] == ADMIN_USER and request.form['pass'] == ADMIN_PASS:
        session['logged_in'] = True
        return redirect(url_for('admin'))
    return render_template_string(HTML_LAYOUT, mode='login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
