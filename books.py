from multiprocessing.dummy import connection

from database import get_connection

from database import get_connection
import mysql.connector
from logger_config import logger

from database import get_connection
import mysql.connector


def add_book():
    """Add a new book to the library database."""

    connection = None
    cursor = None

    try:
        # Step 1: Collect book information
        print("\n========== ADD NEW BOOK ==========")

        title = input("Enter book title: ").strip()
        author = input("Enter author name: ").strip()
        isbn = input("Enter ISBN: ").strip()
        category = input("Enter book category: ").strip()

        # Step 2: Validate required information
        if not title:
            raise ValueError("Book title cannot be empty.")

        if not author:
            raise ValueError("Author name cannot be empty.")

        if not isbn:
            raise ValueError("ISBN cannot be empty.")

        # Step 3: Validate total copies
        try:
            total_copies = int(input("Enter total copies: "))
        except ValueError:
            raise ValueError("Total copies must be a valid integer.")

        if total_copies <= 0:
            raise ValueError("Total copies must be greater than zero.")

        # Step 4: Prepare parameterized SQL query
        query = """
            INSERT INTO books
            (title, author, isbn, category,
             total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            title,
            author,
            isbn,
            category or None,
            total_copies,
            total_copies
        )

        # Step 5: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 6: Execute query
        cursor.execute(query, values)

        # Step 7: Save changes
        connection.commit()
        

        logger.info(
            "Book added successfully | Book ID: %s",
            cursor.lastrowid
        )

        
        print("\nBook added successfully!")
        print(f"Book ID: {cursor.lastrowid}")
        print(f"Title: {title}")
        print(f"Available copies: {total_copies}")

    except ValueError as error:
        logger.warning("Add book rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection and connection.is_connected():
            connection.rollback()
        logger.warning("Book creation failed due to integrity error: %s", error)
        print(f"\nDatabase Integrity Error: {error}")

    except mysql.connector.Error as error:
        if connection and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error while adding a book")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error while adding a book")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Step 8: Release database resources
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()








def view_books():
    """Display all books registered in the library."""

    connection = None
    cursor = None

    try:
        print("\n========== LIBRARY BOOKS ==========")

        # Step 1: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 2: Prepare and execute SQL query
        query = "SELECT * FROM books ORDER BY id"
        cursor.execute(query)

        # Step 3: Retrieve all records
        books = cursor.fetchall()

        # Step 4: Check whether books exist
        if not books:
            logger.info("View books completed | No books found")
            print("\nNo books found in the library.")
            return

        # Step 5: Display book information
        for book in books:
            print("\n----------------------------------")
            print(f"Book ID:          {book[0]}")
            print(f"Title:            {book[1]}")
            print(f"Author:           {book[2]}")
            print(f"ISBN:             {book[3]}")
            print(f"Category:         {book[4] or 'Not specified'}")
            print(f"Total Copies:     {book[5]}")
            print(f"Available Copies: {book[6]}")

        print("\n----------------------------------")
        print(f"Total Books: {len(books)}")

    except mysql.connector.Error as error:
        logger.exception("MySQL error while viewing books")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        logger.exception("Unexpected error while viewing books")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Step 6: Close database resources
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()




def search_book():
    """Search for books by ID, title, or author."""

    connection = None
    cursor = None

    try:
        print("\n========== SEARCH BOOKS ==========")
        print("1. Search by Book ID")
        print("2. Search by Book Title")
        print("3. Search by Author")
        print("4. Back")

        choice = input("\nChoose a search option: ").strip()

        # Search by Book ID
        if choice == "1":

            book_id_input = input("Enter Book ID: ").strip()

            try:
                book_id = int(book_id_input)
            except ValueError:
                raise ValueError("Book ID must be a valid integer.")

            if book_id <= 0:
                raise ValueError("Book ID must be greater than zero.")

            query = """
                SELECT * FROM books
                WHERE id = %s
            """

            values = (book_id,)

        # Search by Book Title
        elif choice == "2":

            title = input("Enter book title or keyword: ").strip()

            if not title:
                raise ValueError("Book title cannot be empty.")

            query = """
                SELECT * FROM books
                WHERE title LIKE %s
                ORDER BY id
            """

            values = (f"%{title}%",)

        # Search by Author
        elif choice == "3":

            author = input("Enter author name or keyword: ").strip()

            if not author:
                raise ValueError("Author name cannot be empty.")

            query = """
                SELECT * FROM books
                WHERE author LIKE %s
                ORDER BY id
            """

            values = (f"%{author}%",)

        elif choice == "4":
            logger.info("Book search cancelled")
            print("\nReturning to the previous menu.")
            return

        else:
            raise ValueError("Invalid option. Please choose 1, 2, 3, or 4.")

        # Connect to the database
        connection = get_connection()
        cursor = connection.cursor()

        # Execute the selected search query
        cursor.execute(query, values)

        # Retrieve all matching records
        books = cursor.fetchall()

        if not books:
            logger.info("Book search completed | No matching books found")
            print("\nNo matching books found.")
            return

        # Display matching books
        print("\n========== SEARCH RESULTS ==========")

        for book in books:
            print("\n----------------------------------")
            print(f"Book ID:          {book[0]}")
            print(f"Title:            {book[1]}")
            print(f"Author:           {book[2]}")
            print(f"ISBN:             {book[3]}")
            print(f"Category:         {book[4] or 'Not specified'}")
            print(f"Total Copies:     {book[5]}")
            print(f"Available Copies: {book[6]}")

        print("\n----------------------------------")
        logger.info(
            "Book search completed successfully | Matching books: %s",
                len(books)
                )
        print(f"Matching Books: {len(books)}")

    except ValueError as error:
        logger.warning("Book search rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.Error as error:
        logger.exception("MySQL error while searching books")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        logger.exception("Unexpected error while searching books")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Close the cursor if it was created
        if cursor is not None:
            cursor.close()

        # Close the database connection if it is open
        if connection is not None and connection.is_connected():
            connection.close()


def update_book():
    """Update the details of an existing book."""

    connection = None
    cursor = None

    try:
        print("\n========== UPDATE BOOK ==========")

        # Get and validate Book ID
        book_id_input = input("Enter Book ID to update: ").strip()

        try:
            book_id = int(book_id_input)
        except ValueError:
            raise ValueError("Book ID must be a valid integer.")

        if book_id <= 0:
            raise ValueError("Book ID must be greater than zero.")

        # Establish database connection
        connection = get_connection()
        cursor = connection.cursor()

        # Check whether the book exists
        select_query = """
            SELECT title, author, isbn, category,
                   total_copies, available_copies
            FROM books
            WHERE id = %s
        """

        cursor.execute(select_query, (book_id,))
        book = cursor.fetchone()

        if book is None:
            logger.warning("Book update failed | Book ID not found: %s", book_id)
            print("\nBook not found. Please check the Book ID.")
            return

        # Display current information
        print("\n========== CURRENT BOOK DETAILS ==========")
        print(f"Title:            {book[0]}")
        print(f"Author:           {book[1]}")
        print(f"ISBN:             {book[2]}")
        print(f"Category:         {book[3] or 'Not specified'}")
        print(f"Total Copies:     {book[4]}")
        print(f"Available Copies: {book[5]}")

        print("\nEnter new details.")
        print("Press ENTER to keep the existing value.")

        # Collect updated information
        title_input = input("\nNew title: ").strip()
        author_input = input("New author: ").strip()
        isbn_input = input("New ISBN: ").strip()
        category_input = input("New category: ").strip()
        total_copies_input = input("New total copies: ").strip()

        # Keep old values if the user enters nothing
        new_title = title_input if title_input else book[0]
        new_author = author_input if author_input else book[1]
        new_isbn = isbn_input if isbn_input else book[2]
        new_category = category_input if category_input else book[3]

        # Validate total copies
        if total_copies_input:
            try:
                new_total_copies = int(total_copies_input)
            except ValueError:
                raise ValueError("Total copies must be a valid integer.")
        else:
            new_total_copies = book[4]

        if not new_title:
            raise ValueError("Book title cannot be empty.")

        if not new_author:
            raise ValueError("Author name cannot be empty.")

        if not new_isbn:
            raise ValueError("ISBN cannot be empty.")

        if new_total_copies <= 0:
            raise ValueError("Total copies must be greater than zero.")

        # Calculate the number of books currently borrowed
        borrowed_copies = book[4] - book[5]

        # Prevent total copies from becoming less than borrowed copies
        if new_total_copies < borrowed_copies:
            raise ValueError(
                f"Cannot set total copies below {borrowed_copies}. "
                "Some copies are currently borrowed."
            )

        # Calculate updated available copies
        new_available_copies = new_total_copies - borrowed_copies

        # SQL UPDATE query
        update_query = """
            UPDATE books
            SET title = %s,
                author = %s,
                isbn = %s,
                category = %s,
                total_copies = %s,
                available_copies = %s
            WHERE id = %s
        """

        values = (
            new_title,
            new_author,
            new_isbn,
            new_category or None,
            new_total_copies,
            new_available_copies,
            book_id
        )

        # Execute update
        cursor.execute(update_query, values)

        # Save changes permanently
        connection.commit()
        logger.info("Book updated successfully | Book ID: %s", book_id)

        print("\nBook updated successfully!")
        print(f"Book ID:          {book_id}")
        print(f"Title:            {new_title}")
        print(f"Author:           {new_author}")
        print(f"ISBN:             {new_isbn}")
        print(f"Category:         {new_category or 'Not specified'}")
        print(f"Total Copies:     {new_total_copies}")
        print(f"Available Copies: {new_available_copies}")

    except ValueError as error:
        logger.warning("Book update rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning(
            "Book update failed due to integrity error | Book ID: %s",
            book_id
        )

        print(f"\nDatabase Integrity Error: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()

        logger.exception("MySQL error while updating book")

        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error while updating book")
        print(f"\nUnexpected Error: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()            





def delete_book():
    """Delete a book if it has no borrowing history."""

    connection = None
    cursor = None

    try:
        print("\n========== DELETE BOOK ==========")

        # Step 1: Get and validate Book ID
        book_id_input = input("Enter Book ID to delete: ").strip()

        try:
            book_id = int(book_id_input)
        except ValueError:
            raise ValueError("Book ID must be a valid integer.")

        if book_id <= 0:
            raise ValueError("Book ID must be greater than zero.")

        # Step 2: Connect to the database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 3: Check whether the book exists
        select_query = """
            SELECT id, title, author, isbn, category,
                   total_copies, available_copies
            FROM books
            WHERE id = %s
        """

        cursor.execute(select_query, (book_id,))
        book = cursor.fetchone()

        if book is None:
            logger.warning("Book deletion failed | Book ID not found: %s", book_id)
            print("\nBook not found. Please check the Book ID.")
            return

        # Step 4: Display book details
        print("\n========== BOOK DETAILS ==========")
        print(f"Book ID:          {book[0]}")
        print(f"Title:            {book[1]}")
        print(f"Author:           {book[2]}")
        print(f"ISBN:             {book[3]}")
        print(f"Category:         {book[4] or 'Not specified'}")
        print(f"Total Copies:     {book[5]}")
        print(f"Available Copies: {book[6]}")

        # Step 5: Ask for confirmation
        confirmation = input(
            "\nAre you sure you want to delete this book? (y/n): "
        ).strip().lower()

        if confirmation == "n":
            logger.info("Book deletion cancelled | Book ID: %s", book_id)
            print("\nBook deletion cancelled.")
            return

        if confirmation != "y":
            raise ValueError(
                "Invalid confirmation. Please enter y or n."
            )

        # Step 6: Delete the book
        delete_query = """
            DELETE FROM books
            WHERE id = %s
        """

        cursor.execute(delete_query, (book_id,))

        # Step 7: Save the change
        connection.commit()
        logger.info("Book deleted successfully | Book ID: %s", book_id)

        print("\nBook deleted successfully!")

    except ValueError as error:
        logger.warning("Book deletion rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning(
            "Book deletion blocked by database integrity constraint | Book ID: %s",
            book_id
        )
        print(
            "\nDatabase Integrity Error: "
            "This book cannot be deleted because it may have "
            "borrowing history."
        )

        print(f"Details: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error while deleting book")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error while deleting book")
        print(f"\nUnexpected Error: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
