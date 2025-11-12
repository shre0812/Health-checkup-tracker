from flask import Flask, render_template, request, redirect, url_for, flash
from flask_apscheduler import APScheduler
import calendar, json, os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "health_data.json"
REMINDER_FILE = "reminders.json"

# Linked List for records
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add_record(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            temp = self.head
            while temp.next:
                temp = temp.next
            temp.next = new_node

    def get_all_records(self):
        records = []
        temp = self.head
        while temp:
            records.append(temp.data)
            temp = temp.next
        return records

    def load_from_list(self, data_list):
        for record in data_list:
            self.add_record(record)

# Helpers
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

health_records = LinkedList()
health_records.load_from_list(load_json(DATA_FILE))
reminders = load_json(REMINDER_FILE)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
last_record_time = datetime.now() if health_records.get_all_records() else None

# Reminder trigger
def send_reminder(reminder):
    now = datetime.now()
    if last_record_time and (now - last_record_time).seconds < 3600:
        return
    if reminder.get("snoozed_until") and now < datetime.fromisoformat(reminder["snoozed_until"]):
        return
    print(f"🔔 Reminder: {reminder['description']}")
    reminder["alert"] = True
    save_json(REMINDER_FILE, reminders)

# ROUTES
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', records=health_records.get_all_records(), reminders=reminders)

@app.route('/add', methods=['POST'])
def add_record():
    global last_record_time
    bp = request.form['blood_pressure']
    try:
        sys, dia = map(int, bp.split('/'))
    except ValueError:
        flash("⚠️ Invalid BP format (use 120/80)", "error")
        return redirect(url_for('dashboard'))
    record = {'date': request.form['date'], 'weight': request.form['weight'],
              'blood_pressure': bp, 'notes': request.form['notes']}
    health_records.add_record(record)
    save_json(DATA_FILE, health_records.get_all_records())
    last_record_time = datetime.now()
    if sys > 130 or dia > 85:
        flash("⚠️ High Blood Pressure Detected! Take necessary precautions.", "warning")
    flash("✅ Record added successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    freq = request.form['frequency']
    desc = request.form.get('description', '')
    day = request.form.get('day')
    date = request.form.get('month_date')
    reminder = {"frequency": freq, "description": desc, "day": day,
                "date": date, "alert": False, "snoozed_until": None}
    reminders.append(reminder)
    save_json(REMINDER_FILE, reminders)
    job_id = f"reminder_{len(reminders)}"
    if freq == 'daily':
        scheduler.add_job(id=job_id, func=send_reminder, args=[reminder], trigger='interval', minutes=1)
    elif freq == 'weekly' and day:
        weekday = list(calendar.day_name).index(day)
        scheduler.add_job(id=job_id, func=send_reminder, args=[reminder], trigger='cron', day_of_week=weekday, hour=9)
    elif freq == 'monthly' and date:
        scheduler.add_job(id=job_id, func=send_reminder, args=[reminder], trigger='cron', day=int(date), hour=9)
    flash(f"🔔 Reminder set: {freq.capitalize()} - {desc}", "info")
    return redirect(url_for('dashboard'))

@app.route('/delete_reminder/<int:i>')
def delete_reminder(i):
    if 0 <= i < len(reminders):
        reminders.pop(i)
        save_json(REMINDER_FILE, reminders)
        flash("🗑️ Reminder deleted!", "info")
    return redirect(url_for('dashboard'))

@app.route('/snooze/<int:i>')
def snooze(i):
    if 0 <= i < len(reminders):
        reminders[i]["snoozed_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()
        save_json(REMINDER_FILE, reminders)
        flash("😴 Snoozed for 30 minutes!", "info")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
