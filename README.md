# Library System

A command-line Library Management System built with **Python** and **SQLite**. It supports full CRUD operations, book borrowing with transaction handling, and automated inventory management through database triggers.

---

## Features

- **View Books & Students** — Browse all available books and registered students
- **Add / Update / Delete Students** — Full student record management
- **Borrow a Book** — Transaction-safe borrowing that automatically decrements available copies
- **Return Tracking** — Returning a book automatically restores copy count via a trigger
- **Borrowing Records** — View all borrow history with a JOIN across Books and Students
- **Data Integrity** — Foreign keys, CHECK constraints, and triggers enforce clean data
- **Auto-reset on launch** — Database is re-initialized fresh every run

---

## Database Schema

```
Books
├── book_id (PK)
├── title
├── author
├── genre
└── copies_available (≥ 0)

Students
├── student_id (PK)
├── name
├── course
└── year_level

Borrowings
├── borrow_id (PK)
├── student_id (FK → Students)
├── book_id (FK → Books)
├── date_borrowed
├── date_due
└── date_returned
```

### Triggers
| Trigger | Event | Action |
|---|---|---|
| `trg_before_insert_borrow` | BEFORE INSERT on Borrowings | Checks copies available; decrements count |
| `trg_after_update_return` | AFTER UPDATE on date_returned | Increments copy count when book is returned |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3` | Application logic |
| `sqlite3` | Built-in database (no install needed) |
| `os` | Database file management |

---

## Run on Google Colab

You can run this project directly in your browser — no setup needed:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1gW2owvf1xI0bObXaEoaPwUZKnjPjaCkL?usp=sharing)

---



**1. Clone the repository**
```bash
git clone https://github.com/sagosaruiz1/your-repo-name.git
cd your-repo-name
```

**2. Run the app** *(no dependencies to install — uses Python's built-in sqlite3)*
```bash
python library_system.py
```

> The database (`library.db`) is dropped and re-created every time the program starts. Any data added during a session will be lost on restart.

---

## Usage

On launch, the system seeds the database with 10 books and 1 sample student, then presents a menu:

```
--- Library System Menu ---
1. View Books
2. View Students
3. Add Student
4. Update Student Year Level
5. Delete Student
6. View Borrowings
7. Borrow Book (Transaction)
8. Exit
```

**Borrowing a book (Option 7)** uses a transaction — if the book has no available copies, the trigger raises an error and the transaction is rolled back automatically.

---

## Project Structure

```
├── library_system.py   # Main app: DB setup, CRUD functions, menu loop
└── library.db          # Auto-generated SQLite database (created on run)
```

---

## Author

**Ruiz Sagosa** — Computer Science Student

---

## License

This project is for educational purposes.
