from flask import Flask, render_template, request, redirect, url_for, flash
from flask_apscheduler import APScheduler
import calendar

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -----------------------------
# Linked List for Health Records
# -----------------------------
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


health_records = LinkedList()
scheduler = APScheduler()
reminders = []  # store all reminders as dictionaries


# -----------------------------
# Scheduler job function
# -----------------------------
def send_reminder(reminder):
    print(f"🔔 Reminder: {reminder['description']}")
    reminder["alert"] = True


scheduler.init_app(app)
scheduler.start()


# -----------------------------
# Flask Routes
# -----------------------------
@app.route('/')
def index():
    # Pass all records and reminders to UI
    records_list = health_records.get_all_records()
    return render_template('index.html', records=records_list, reminders=reminders)


@app.route('/add', methods=['POST'])
def add_record():
    record = {
        'date': request.form['date'],
        'weight': request.form['weight'],
        'blood_pressure': request.form['blood_pressure'],
        'notes': request.form['notes'],
    }
    health_records.add_record(record)
    flash("✅ Health record added successfully!", "success")
    return redirect(url_for('index'))


@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    freq = request.form['frequency']
    desc = request.form.get('description', '')
    day = request.form.get('day')
    date = request.form.get('month_date')

    reminder = {"frequency": freq, "description": desc, "day": day, "date": date, "alert": False}
    reminders.append(reminder)

    job_id = f"reminder_{len(reminders)}"

    # Schedule based on frequency
    if freq == 'daily':
        scheduler.add_job(id=job_id, func=send_reminder, args=[reminder], trigger='interval', days=1)
    elif freq == 'weekly' and day:
        weekday = list(calendar.day_name).index(day)
        scheduler.add_job(id=job_id, func=send_reminder, args=[reminder], trigger='cron', day_of_week=weekday, hour=9)
    elif freq == 'monthly' and date:
        scheduler.add_job(id=job_id, func=send_reminder, args=[reminder], trigger='cron', day=int(date), hour=9)

    flash(f"🔔 Reminder set: {freq.capitalize()} - {desc}", "info")
    return redirect(url_for('index'))


@app.route('/delete_reminder/<int:index>')
def delete_reminder(index):
    if 0 <= index < len(reminders):
        reminders.pop(index)
        flash("🗑️ Reminder deleted successfully!", "info")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
