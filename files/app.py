from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# -----------------------------
# Linked List Implementation
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


# -----------------------------
# Flask routes
# -----------------------------
health_records = LinkedList()

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
    health_records.add_record(record)
    return redirect(url_for('records'))

@app.route('/records')
def records():
    records_list = health_records.get_all_records()
    return render_template('records.html', records=records_list)

if __name__ == '__main__':
    app.run(debug=True)
