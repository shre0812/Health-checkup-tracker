from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory health records store (for demo)
health_records = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_record():
    record = {
        'date': request.form['date'],
        'weight': request.form['weight'],
        'blood_pressure': request.form['blood_pressure'],
        'notes': request.form['notes'],
    }
    health_records.append(record)
    return redirect(url_for('records'))

@app.route('/records')
def records():
    return render_template('records.html', records=health_records)

if __name__ == '__main__':
    app.run(debug=True)
