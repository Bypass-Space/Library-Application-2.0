import sqlite3

class LibrarySystem:
    def __init__(self):
        # Establish a connection to the database
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # Create tables (books, members, records)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                Book TEXT,
                                Author TEXT,
                                DatePublished TEXT,
                                Copies INTEGER
                            )''')

        # Check if the members table exists
        self.cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='members'")
        table_exists = self.cursor.fetchone()[0]

        if not table_exists:
            self.cursor.execute('''CREATE TABLE members (
                                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Name TEXT,
                                    Email TEXT
                                )''')

            # Commit the changes to the database
            self.conn.commit()

            print("Members table created successfully.")
        else:
            print()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                MemberID INTEGER,
                                BookID INTEGER,
                                BorrowedDate TEXT,
                                ReturnedDate TEXT,
                                FOREIGN KEY (MemberID) REFERENCES members(ID),
                                FOREIGN KEY (BookID) REFERENCES books(ID)
                            )''')

        # Commit the changes to the database
        self.conn.commit()

    def start(self):
        username = input("Username: ('GUEST')  ")
        password = input("Password:  ")

        if username == "GUEST" and password == "root":
            return username, password
        else:
            print("INVALID CREDENTIALS - TRY AGAIN")
            self.start()

    def run_library_system(self):
        self.create_tables()

        username, password = self.start()

        # Menu options
        menu = """
        Select an action:
        1. Check out a book
        2. Return a book
        3. Add a member
        4. Add a book
        5. View all books
        6. View all members
        7. Delete a book
        8. Delete a member
        Enter 'q' to quit.
        """

        while True:
            print(menu)
            choice = input("Enter your choice: ")

            if choice == '1':
                # Check out a book
                book_id = input("Enter the book ID to check out: ")
                member_id = input("Enter the member ID: ")

                # Check if the book exists
                book = self.cursor.execute("SELECT * FROM books WHERE ID=?", (book_id,)).fetchone()
                if book:
                    # Check if the member exists
                    member = self.cursor.execute("SELECT * FROM members WHERE ID=?", (member_id,)).fetchone()
                    if member:
                        # Check if copies are available
                        copies_available = book[4]
                        if copies_available > 0:
                            # Insert record into the records table
                            self.cursor.execute("INSERT INTO records (MemberID, BookID, BorrowedDate, ReturnedDate) VALUES (?, ?, DATE('now'), NULL)",
                                               (member_id, book_id))

                            # Update the copies count in the books table
                            copies = copies_available - 1
                            self.cursor.execute("UPDATE books SET Copies=? WHERE ID=?", (copies, book_id))

                            # Commit the changes to the database
                            self.conn.commit()

                            print("Book checked out successfully.")
                        else:
                            print("Book not available. All copies are currently checked out.")
                    else:
                        print("Member not found.")
                else:
                    print("Book not found.")

            elif choice == '2':
                # Return a book
                book_id = input("Enter the book ID to return: ")

                # Check if the book exists
                book = self.cursor.execute("SELECT * FROM books WHERE ID=?", (book_id,)).fetchone()
                if book:
                    # Check if the book is currently borrowed
                    record = self.cursor.execute("SELECT * FROM records WHERE BookID=? AND ReturnedDate IS NULL", (book_id,)).fetchone()
                    if record:
                        # Update the returned date in the records table
                        self.cursor.execute("UPDATE records SET ReturnedDate=DATE('now') WHERE ID=?", (record[0],))

                        # Update the copies count in the books table
                        copies = book[4] + 1
                        self.cursor.execute("UPDATE books SET Copies=? WHERE ID=?", (copies, book_id))

                        # Commit the changes to the database
                        self.conn.commit()

                        print("Book returned successfully.")
                    else:
                        print("The book is not currently borrowed.")
                else:
                    print("Book not found.")

            elif choice == '3':
                # Add a member
                admin_pin = input("Enter the admin PIN: ")

                if admin_pin == "admin123":
                    member_name = input("Enter the member name: ")
                    email = input("Enter the email: ")

                    # Insert member information into the members table
                    self.cursor.execute("INSERT INTO members (Name, Email) VALUES (?, ?)",
                                       (member_name, email))

                    # Commit the changes to the database
                    self.conn.commit()

                    print("Member added successfully.")
                else:
                    print("Incorrect admin PIN. Member addition failed.")

            elif choice == '4':
                # Add a book
                admin_pin = input("Enter the admin PIN: ")

                if admin_pin == "admin123":
                    book_name = input("Enter the book name: ")
                    author = input("Enter the author name: ")
                    date_published = input("Enter the date published (YYYY-MM-DD): ")
                    copies = int(input("Enter the number of copies: "))

                    # Insert book information into the books table
                    self.cursor.execute("INSERT INTO books (Book, Author, DatePublished, Copies) VALUES (?, ?, ?, ?)",
                                       (book_name, author, date_published, copies))

                    # Commit the changes to the database
                    self.conn.commit()

                    print("Book added successfully.")
                else:
                    print("Incorrect admin PIN. Book addition failed.")

            elif choice == '5':
                # View all books
                books = self.cursor.execute("SELECT * FROM books").fetchall()

                if books:
                    print("All books in the library:")
                    for book in books:
                        print(f"Book ID: {book[0]}")
                        print(f"Book Name: {book[1]}")
                        print(f"Author: {book[2]}")
                        print(f"Date Published: {book[3]}")
                        print(f"Copies Available: {book[4]}")
                        print()
                else:
                    print("No books found in the library.")

            elif choice == '6':
                # View all members
                members = self.cursor.execute("SELECT * FROM members").fetchall()

                if members:
                    print("All members:")
                    for member in members:
                        print(f"Member ID: {member[0]}")
                        print(f"Member Name: {member[1]}")
                        print(f"Email: {member[2]}")
                        print()
                else:
                    print("No members found.")

            elif choice == '7':
                # Delete a book
                admin_pin = input("Enter the admin PIN: ")

                if admin_pin == "admin123":
                    book_id = input("Enter the book ID to delete: ")

                    # Check if the book exists
                    book = self.cursor.execute("SELECT * FROM books WHERE ID=?", (book_id,)).fetchone()
                    if book:
                        # Delete the book from the books table
                        self.cursor.execute("DELETE FROM books WHERE ID=?", (book_id,))

                        # Delete the associated records from the records table
                        self.cursor.execute("DELETE FROM records WHERE BookID=?", (book_id,))

                        # Commit the changes to the database
                        self.conn.commit()

                        print("Book deleted successfully.")
                    else:
                        print("Book not found.")
                else:
                    print("Incorrect admin PIN. Book deletion failed.")

            elif choice == '8':
                # Delete a member
                admin_pin = input("Enter the admin PIN: ")

                if admin_pin == "admin123":
                    member_id = input("Enter the member ID to delete: ")

                    # Check if the member exists
                    member = self.cursor.execute("SELECT * FROM members WHERE ID=?", (member_id,)).fetchone()
                    if member:
                        # Delete the member from the members table
                        self.cursor.execute("DELETE FROM members WHERE ID=?", (member_id,))

                        # Delete the associated records from the records table
                        self.cursor.execute("DELETE FROM records WHERE MemberID=?", (member_id,))

                        # Commit the changes to the database
                        self.conn.commit()

                        print("Member deleted successfully.")
                    else:
                        print("Member not found.")
                else:
                    print("Incorrect admin PIN. Member deletion failed.")

            elif choice.lower() == 'q':
                # Quit the library system
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    library_system = LibrarySystem()
    library_system.run_library_system()
