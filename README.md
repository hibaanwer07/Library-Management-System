# 📚 Library Management System – Flask Web App

**Library Management System** is a Flask-based web application built to streamline library operations such as book inventory, user registration, issuing, returning, and tracking books. It simplifies library workflows with a modern UI, admin controls, and database-backed functionality.

---

##  Features

- ** Admin & User Login System**  
  Separate access levels for librarians and users with secure authentication.

- **Book Inventory Management**  
  Add, update, delete, and search books in real time.

- ** Book Issuing & Return**  
  Track which user borrowed what book, with due dates and return functionality.

- **User Registration & Management**  
  Users can register, log in, and manage their book activity.

- ** Dashboard Interface**  
  Visual overview of books issued, available stock, user count, and activity logs.

- ** Smart Search**  
  Easily find books by title, author, or category.

- ** Transaction History**  
  Logs all issued/returned books for future reference and auditing.

---

## Project Structure

```plaintext
.
├── static/                    # Static assets like CSS, images, and JS
│   ├── style.css              # UI styling
│   └── icons/                 # Optional icons and images
├── templates/                 # HTML templates
│   ├── index.html             # Home / Dashboard
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── admin.html             # Admin dashboard
│   ├── add_book.html          # Form to add books
│   ├── issue_book.html        # Issue book interface
│   └── return_book.html       # Return book interface
├── database.py                # SQLite or MySQL DB operations
├── app.py                     # Main Flask application
├── config.py                  # App configuration
├── requirements.txt           # Project dependencies
└── README.md                  # This file
```
## Acknowledgments
Flask – The soul of the web app.
SQLite – Lightweight and reliable database.

