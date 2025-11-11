
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import sqlite3, os, uuid
import qrcode

app = Flask(__name__)
app.secret_key = "change-this-in-production"

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "lost_found.db")
QR_DIR = os.path.join(BASE_DIR, "static", "qrcodes")
os.makedirs(QR_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id TEXT PRIMARY KEY, owner_name TEXT, contact TEXT, item_name TEXT, description TEXT, location TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT, finder_name TEXT, finder_contact TEXT, message TEXT, date_reported TEXT)''')
    conn.commit()
    conn.close()

def generate_qr(item_id):
    qr_path = os.path.join(QR_DIR, f"{item_id}.png")
    # If already exists, return path
    if os.path.exists(qr_path):
        return qr_path
    url = f"http://127.0.0.1:5000/item/{item_id}"
    img = qrcode.make(url)
    img.save(qr_path)
    return qr_path

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        owner_name = request.form.get("owner_name","").strip()
        contact = request.form.get("contact","").strip()
        item_name = request.form.get("item_name","").strip()
        description = request.form.get("description","").strip()
        location = request.form.get("location","").strip()
        date = request.form.get("date","").strip()
        item_id = str(uuid.uuid4())[:8]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO items (id, owner_name, contact, item_name, description, location, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (item_id, owner_name, contact, item_name, description, location, date))
        conn.commit()
        conn.close()
        generate_qr(item_id)
        flash(f"Item registered! Your Item ID: {item_id}. QR code saved in static/qrcodes/{item_id}.png")
        return redirect(url_for("item_page", item_id=item_id))
    return render_template("register.html")

@app.route("/item/<item_id>", methods=["GET","POST"])
def item_page(item_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, owner_name, contact, item_name, description, location, date FROM items WHERE id = ?", (item_id,))
    item = c.fetchone()
    if not item:
        conn.close()
        return render_template("item_not_found.html", item_id=item_id), 404
    if request.method == "POST":
        finder_name = request.form.get("finder_name","").strip()
        finder_contact = request.form.get("finder_contact","").strip()
        message = request.form.get("message","").strip()
        date_reported = request.form.get("date_reported","").strip()
        c.execute("INSERT INTO reports (item_id, finder_name, finder_contact, message, date_reported) VALUES (?, ?, ?, ?, ?)",
                  (item_id, finder_name, finder_contact, message, date_reported))
        conn.commit()
        conn.close()
        flash("Thank you! The report has been recorded. The owner contact details are shown on this page so you can reach them directly.")
        return redirect(url_for("item_page", item_id=item_id))
    c.execute("SELECT finder_name, finder_contact, message, date_reported FROM reports WHERE item_id = ? ORDER BY id DESC", (item_id,))
    reports = c.fetchall()
    conn.close()
    qr_url = url_for('static', filename=f"qrcodes/{item_id}.png")
    return render_template("item.html", item=item, reports=reports, qr_url=qr_url)

@app.route("/admin/items")
def admin_items():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, owner_name, contact, item_name, description, location, date FROM items ORDER BY rowid DESC")
    items = c.fetchall()
    c.execute("SELECT id, item_id, finder_name, finder_contact, message, date_reported FROM reports ORDER BY id DESC")
    reports = c.fetchall()
    conn.close()
    return render_template("admin.html", items=items, reports=reports)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
