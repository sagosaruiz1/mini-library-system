import sqlite3
import os

DB_NAME = "library.db"

def connect_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Exception as e:
        print("Error connecting to DB:", e)
        return None
    
def setup_db(conn):

    sql_script = """ 
    DROP TABLE IF EXISTS Borrowings;
    DROP TABLE IF EXISTS Students;
    DROP TABLE IF EXISTS Books;

    CREATE TABLE Books (
        book_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        genre TEXT,
        copies_available INTEGER NOT NULL CHECK(copies_available >= 0)
    );

    CREATE TABLE Students (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        course TEXT,
        year_level INTEGER
    );

    CREATE TABLE Borrowings (
        borrow_id INTEGER PRIMARY KEY,
        student_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        date_borrowed DATE NOT NULL,
        date_due DATE NOT NULL,
        date_returned DATE,
        FOREIGN KEY(student_id) REFERENCES Students(student_id),
        FOREIGN KEY(book_id) REFERENCES Books(book_id)
    );

    CREATE INDEX idx_books_title ON Books(title);

    INSERT INTO Books (book_id, title, author, genre, copies_available) VALUES
    (1, 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 4),
    (2, '1984', 'George Orwell', 'Dystopian', 5),
    (3, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Classic', 3),
    (4, 'Pride and Prejudice', 'Jane Austen', 'Romance', 4),
    (5, 'The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 2),
    (6, 'The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 6),
    (7, 'Fahrenheit 451', 'Ray Bradbury', 'Dystopian', 5),
    (8, 'Moby-Dick', 'Herman Melville', 'Adventure', 3),
    (9, 'War and Peace', 'Leo Tolstoy', 'Historical', 3),
    (10, 'Jane Eyre', 'Charlotte Bronte', 'Gothic', 4);

    INSERT INTO Students (student_id, name, course, year_level) VALUES
    (2023305664, 'Ruiz Sagosa', 'BSCS', 2);

    INSERT INTO Borrowings (borrow_id, student_id, book_id, date_borrowed, date_due, date_returned) VALUES
    (1001, 2023305664, 1, '2025-12-08', '2025-12-25', '2025-12-20');
    
    CREATE TRIGGER trg_before_insert_borrow
    BEFORE INSERT ON Borrowings
    FOR EACH ROW
    BEGIN
        SELECT
            CASE
                WHEN (SELECT copies_available FROM Books WHERE book_id = NEW.book_id) <= 0
                THEN RAISE(ABORT, 'No copies available for this book.')
            END;
        UPDATE Books
            SET copies_available = copies_available - 1
            WHERE book_id = NEW.book_id;
    END;

    CREATE TRIGGER trg_after_update_return
    AFTER UPDATE OF date_returned ON Borrowings
    FOR EACH ROW
    WHEN NEW.date_returned IS NOT NULL AND OLD.date_returned IS NULL
    BEGIN
        UPDATE Books
            SET copies_available = copies_available + 1
            WHERE book_id = NEW.book_id;
    END;
    """

    try:
        conn.executescript(sql_script)
        conn.commit()
        print("Database setup complete.")
    except Exception as e:
        print("Error seting up database:", e)


# -----------CRUD OPERATIONS-----------

# CREATE (Insert)

def add_student(conn, student_id, name, course, year_level):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Students (student_id, name, course, year_level)
            VALUES (?, ?, ?, ?)
        """, (student_id, name, course, year_level))
        conn.commit()
        print("Student added successfully.")
    except Exception as e:
        print("Error adding student:", e)


# READ (Select)

def view_books(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Books ORDER BY book_id")
        rows = cur.fetchall()
        print("\n-------- BOOKS LIST --------")
        for r in rows:
            print(r)
    except Exception as e:
        print("Error retreiving books:", e)

def view_students(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Students ORDER BY student_id")
        rows = cur.fetchall()
        print("\n-------- STUDENTS LIST --------")
        for r in rows:
            print(f"ID: {r[0]}, Name: {r[1]}, Course: {r[2]}, Year Level: {r[3]}")
    except Exception as e:
        print("Error retreiving students:", e)


#UPDATE

def update_student_year(conn, student_id, new_year_level):
    try:
        cur = conn.cursor()
        cur.execute(""" 
            UPDATE Students
            SET year_level = ?
            WHERE student_id = ?
        """, (new_year_level, student_id))

        if cur.rowcount == 0:
            print("Student not found.")
        else:
            conn.commit()
            print("Student year updated.")
    except Exception as e:
        print("Error updating student:", e)


# DELETE

def delete_student(conn, student_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Students WHERE student_id = ?", (student_id,))
        
        if cur.rowcount == 0:
            print("Student not found.")
        else:
            conn.commit()
            print("Student deleted.")
    except Exception as e:
        print("Error deleting student:", e)


# JOIN Query

def view_borrowings(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT br.borrow_id, s.student_id, s.name, bk.title, br.date_borrowed, br.date_due, br.date_returned
            FROM Borrowings br
            JOIN Students s ON br.student_id = s.student_id
            JOIN Books bk ON br.book_id = bk.book_id
            ORDER BY br.date_borrowed DESC
        """)
        rows = cur.fetchall()
        print("\n-------- BORROWING RECORDS --------")
        for r in rows:
            print(f"Borrow ID: {r[0]}\n Student ID: {r[1]}\n Name: {r[2]}\n Book: {r[3]}\n Borrowed: {r[4]}\n Due: {r[5]}\n Returned: {r[6]}\n-------\n")
    except Exception as e:
        print("Error retrieving borrowings:", e)


# TRANSACTION Example

def borrow_book_transaction(conn, student_id, book_id, date_borrowed, date_due):
    try:
        cur = conn.cursor()
        print("\nStarting transaction...")
    
        conn.execute("BEGIN")

        cur.execute("""
            INSERT INTO Borrowings (student_id, book_id, date_borrowed, date_due)
            VALUES (?, ?, ?, ?)
        """, (student_id, book_id, date_borrowed, date_due))


        conn.commit()
        print("Transaction successful. Book borrowed.")
    except Exception as e:
        conn.rollback()
        print("Transaction failed. Rolled back.", e)




def main():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    conn = connect_db()
    setup_db(conn)


    
    while True:
        print("\n--- Library System Menu ---")
        print("1. View Books")
        print("2. View Students")
        print("3. Add Student")
        print("4. Update Student Year Level")
        print("5. Delete Student")
        print("6. View Borrowings")
        print("7. Borrow Book (Transaction)")
        print("8. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            view_books(conn)

        elif choice == '2':
            view_students(conn)

        elif choice == '3':
            sid = input("Student ID: ").strip()
            name = input("Name: ").strip()
            course = input("Course: ").strip()
            year = input("Year Level: ").strip()      
            if not sid.isdigit() or not year.isdigit():
                print("Student ID and Year level must be numbers.")
                continue
            add_student(conn, int(sid), name, course, int(year))

        elif choice == '4':
            sid = input("Student ID: ").strip()
            year = input("New Year Level: ").strip()
            if not sid.isdigit() or not year.isdigit():
                print("Student ID and Year level must be numbers.")
                continue
            update_student_year(conn, int(sid), int(year))

        elif choice == '5':
            sid = input("Student ID to delete: ").strip()
            if not sid.isdigit():
                print("Student ID must be a number.")
                continue
            delete_student(conn, int(sid))

        elif choice == '6':
            view_borrowings(conn)

        elif choice == '7':
            sid = input("Student ID: ").strip()
            bid = input("Book ID: ").strip()
            d_borrow = input("Date Borrowed (YYYY-MM-DD): ").strip()
            d_due = input("Date Due (YYYY-MM-DD): ").strip()
            d_returned = input("Date Returned (YYYY-MM-DD) [Leave Blank if Not Returned]: ").strip()
            if not sid.isdigit() or not bid.isdigit():
                print("Student ID and Book ID must be numbers.")
                continue
            borrow_book_transaction(conn, int(sid), int(bid), d_borrow, d_due)

        elif choice == '8':
            conn.close()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()

if __name__ == "__main__":

    main()
