from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a secure key

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'library_user',        # Your MySQL username
    'password': 'lib123',  # Your MySQL password
    'database': 'library_db'
}

# Database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Login Route (only one definition)
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['user_id'] = user[0]
                session['role'] = user[3]
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid credentials. Please try again."
        except Exception as e:
            error = f"Database error: {e}"
    return render_template('login.html', error=error)

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session['role'])

# All Available Books Route
@app.route('/all_available_books')
def all_available_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, type FROM books WHERE status = 'available'")
    books = cursor.fetchall()
    conn.close()
    return render_template('all_available_books.html', books=books)

# Available Books by Type Route
@app.route('/available_by_type', methods=['GET', 'POST'])
def available_by_type():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    selected_type = None
    available_books = []
    if request.method == 'POST':
        selected_type = request.form['type']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, type FROM books WHERE type = %s AND status = 'available'", 
                       (selected_type,))
        available_books = cursor.fetchall()
        conn.close()
    return render_template('available_by_type.html', books=available_books, selected_type=selected_type)

# Search Route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    results = []
    if request.method == 'POST':
        query = request.form['query']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, type FROM books WHERE (title LIKE %s OR type LIKE %s) AND status = 'available'", 
                       (f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()
        conn.close()
    return render_template('search.html', results=results)

# Borrow Route
@app.route('/borrow', methods=['GET', 'POST'])
def borrow():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    message = None
    if request.method == 'POST':
        book_id = request.form['book_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if book and book[0] == 'available':
            cursor.execute("UPDATE books SET status = 'borrowed' WHERE id = %s", (book_id,))
            cursor.execute("INSERT INTO transactions (user_id, book_id, borrow_date) VALUES (%s, %s, %s)", 
                           (session['user_id'], book_id, datetime.now()))
            conn.commit()
            message = "Book borrowed successfully!"
        else:
            message = "Book is not available!"
        conn.close()
    return render_template('borrow.html', message=message)

# Return Route
@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    message = None
    if request.method == 'POST':
        book_id = request.form['book_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s AND book_id = %s AND return_date IS NULL", 
                       (session['user_id'], book_id))
        transaction = cursor.fetchone()
        if transaction:
            cursor.execute("UPDATE books SET status = 'available' WHERE id = %s", (book_id,))
            cursor.execute("UPDATE transactions SET return_date = %s WHERE user_id = %s AND book_id = %s AND return_date IS NULL", 
                           (datetime.now(), session['user_id'], book_id))
            conn.commit()
            message = "Book returned successfully!"
        else:
            message = "No active borrowing record found!"
        conn.close()
    return render_template('return.html', message=message)

# Admin Route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    message = None
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, author, type, status FROM books")
    books = cursor.fetchall()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    if request.method == 'POST':
        if 'title' in request.form:
            title = request.form['title']
            author = request.form['author']
            type = request.form['type']
            cursor.execute("INSERT INTO books (title, author, type, status) VALUES (%s, %s, %s, 'available')", 
                           (title, author, type))
            conn.commit()
            message = "Book added successfully!"
        elif 'username' in request.form:
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                           (username, password, role))
            conn.commit()
            message = "User added successfully!"
        elif 'delete_user_id' in request.form:
            user_id_to_delete = request.form['delete_user_id']
            if int(user_id_to_delete) == session['user_id']:
                message = "Cannot delete yourself while logged in!"
            else:
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = %s AND return_date IS NULL", 
                               (user_id_to_delete,))
                active_transactions = cursor.fetchone()[0]
                if active_transactions > 0:
                    message = "Cannot delete user with active borrowed books!"
                else:
                    cursor.execute("DELETE FROM transactions WHERE user_id = %s", (user_id_to_delete,))
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id_to_delete,))
                    conn.commit()
                    message = "User deleted successfully!"
    
    cursor.execute("SELECT id, title, author, type, status FROM books")
    books = cursor.fetchall()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    
    conn.close()
    return render_template('admin.html', message=message, books=books, users=users)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)