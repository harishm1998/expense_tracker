from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import database
import subprocess
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
cmd="""termux-notification --title "Persistent Notification" --id "termux expenses" --content "This notification will remain until removed." --ongoing"""
cmdl = ['termux-notification','--title','Expense Tracker','--id','expense_tracker','--content','Current Remaining budget {}','--button1-text','Add expense','--button1-action','bash /data/data/com.termux/files/home/Desktop/python_scripts/flask_apps/expense_tracker/launch_gui.sh','--ongoing']


def update_notification(a,b):
    vl =  float(a)-float(b)
    cmdc = cmdl.copy()
    cmdc[6] = cmdc[6].format(vl)
    subprocess.run(cmdc)

# Initialize database
database.init_db()

# Helper functions
def get_current_user_id():
    return session.get('user_id')

def get_current_month_year():
    now = datetime.now()
    return now.month, now.year

def format_currency(amount):
    return f"₹{amount:,.2f}"  # Changed from $ to ₹

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = database.get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            conn = database.get_db_connection()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = get_current_user_id()
    month, year = get_current_month_year()

    conn = database.get_db_connection()

    # Get current month's budget
    budget = conn.execute('SELECT amount FROM budgets WHERE user_id = ? AND month = ? AND year = ?',
                          (user_id, month, year)).fetchone()

    # Get total expenses for current month
    expenses = conn.execute('''SELECT SUM(amount) as total FROM expenses
                              WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?''',
                              (user_id, f"{month:02d}", str(year))).fetchone()
    total_expenses = expenses['total'] or 0

    # Get active reservations
    reservations = conn.execute('''SELECT SUM(amount) as total FROM reservations
                                  WHERE user_id = ? AND is_used = 0''',
                                  (user_id,)).fetchone()
    total_reservations = reservations['total'] or 0

    # Get recent expenses
    recent_expenses = conn.execute('''SELECT * FROM expenses
                                    WHERE user_id = ?
                                    ORDER BY date DESC LIMIT 5''',
                                    (user_id,)).fetchall()

    conn.close()
    budgett=budget['amount'] if budget else 0
    #update_notification(f"{budgett}",f"{total_expenses}")
    return render_template('dashboard.html',
                          budget=budget['amount'] if budget else 0,
                          total_expenses=total_expenses,
                          total_reservations=total_reservations,
                          recent_expenses=recent_expenses,
                          format_currency=format_currency)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = get_current_user_id()
    month, year = get_current_month_year()
    amount = float(request.form['amount'])

    conn = database.get_db_connection()

    # Check if budget already exists for this month
    existing = conn.execute('SELECT id FROM budgets WHERE user_id = ? AND month = ? AND year = ?',
                           (user_id, month, year)).fetchone()

    if existing:
        conn.execute('UPDATE budgets SET amount = ? WHERE id = ?',
                    (amount, existing['id']))
    else:
        conn.execute('INSERT INTO budgets (user_id, month, year, amount) VALUES (?, ?, ?, ?)',
                    (user_id, month, year, amount))

    conn.commit()
    conn.close()

    flash('Budget updated successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = get_current_user_id()
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))

        conn = database.get_db_connection()
        conn.execute('''INSERT INTO expenses (user_id, amount, category, description, date)
                       VALUES (?, ?, ?, ?, ?)''',
                    (user_id, amount, category, description, date))
        conn.commit()
        conn.close()

        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_expense.html')

@app.route('/add_reservation', methods=['GET', 'POST'])
def add_reservation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = get_current_user_id()
        amount = float(request.form['amount'])
        purpose = request.form['purpose']

        conn = database.get_db_connection()
        conn.execute('''INSERT INTO reservations (user_id, amount, purpose, date_created)
                       VALUES (?, ?, ?, ?)''',
                    (user_id, amount, purpose, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()

        flash('Amount reserved successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_reservation.html')

@app.route('/view_expenses')
def view_expenses():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = get_current_user_id()
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    d1,d2=datetime.now().year - 5, datetime.now().year + 1
    dtv = datetime.now().strftime('%Y-%m-%d')
    conn = database.get_db_connection()
    expenses = conn.execute('''SELECT * FROM expenses
                             WHERE user_id = ?
                             AND strftime('%m', date) = ?
                             AND strftime('%Y', date) = ?
                             ORDER BY date DESC''',
                          (user_id, f"{int(month):02d}", str(year))).fetchall()
    conn.close()

    return render_template('view_expenses.html',
                         expenses=expenses,
                         month=month,
                         year=year,
                         format_currency=format_currency,dtv=dtv,d1=d1,d2=d2)

@app.route('/use_reservation/<int:expense_id>')
def use_reservation(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = get_current_user_id()

    conn = database.get_db_connection()

    # Get the expense
    expense = conn.execute('SELECT * FROM expenses WHERE id = ? AND user_id = ?',
                          (expense_id, user_id)).fetchone()

    if expense:
        # Find a reservation to use
        reservation = conn.execute('''SELECT * FROM reservations
                                    WHERE user_id = ? AND is_used = 0
                                    ORDER BY date_created LIMIT 1''',
                                 (user_id,)).fetchone()

        if reservation:
            # Mark reservation as used
            conn.execute('''UPDATE reservations SET is_used = 1, date_used = ?
                          WHERE id = ?''',
                        (datetime.now().strftime('%Y-%m-%d'), reservation['id']))

            # Update expense to reflect reservation usage
            conn.execute('''UPDATE expenses SET description = ? || ' (from reservation)'
                          WHERE id = ?''',
                        (expense['description'], expense_id))

            conn.commit()
            flash('Reservation applied to expense!', 'success')

    conn.close()
    return redirect(url_for('view_expenses'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
