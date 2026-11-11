
from datetime import date, timedelta

import mysql.connector
from database import get_connection
from logger_config import logger

def borrow_book():
    """Issue books to a library member and record the borrowing."""

    connection = None
    cursor = None

    try:
        print("\n========== BORROW BOOK ==========")

        # Step 1: Get and validate Book ID
        book_id_input = input("Enter Book ID: ").strip()

        try:
            book_id = int(book_id_input)
        except ValueError:
            raise ValueError("Book ID must be a valid integer.")

        if book_id <= 0:
            raise ValueError("Book ID must be greater than zero.")

        # Step 2: Get and validate Member ID
        member_id_input = input("Enter Member ID: ").strip()

        try:
            member_id = int(member_id_input)
        except ValueError:
            raise ValueError("Member ID must be a valid integer.")

        if member_id <= 0:
            raise ValueError("Member ID must be greater than zero.")

        # Step 3: Get and validate borrowing quantity
        quantity_input = input("Enter quantity to borrow: ").strip()

        try:
            quantity = int(quantity_input)
        except ValueError:
            raise ValueError("Quantity must be a valid integer.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        # Step 4: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 5: Start database transaction
        connection.start_transaction()

        # Step 6: Find and lock the selected book
        book_query = """
            SELECT id, title, total_copies, available_copies
            FROM books
            WHERE id = %s
            FOR UPDATE
        """

        cursor.execute(book_query, (book_id,))
        book = cursor.fetchone()

        if book is None:
            connection.rollback()
            logger.warning(
                "Borrowing rejected | Book ID not found: %s",
                book_id
            )    
            print("\nBook not found. Please check the Book ID.")
            return

        # Step 7: Check whether the member exists
        member_query = """
            SELECT id, name, email
            FROM members
            WHERE id = %s
        """

        cursor.execute(member_query, (member_id,))
        member = cursor.fetchone()

        if member is None:
            connection.rollback()
            logger.warning(
                "Borrowing rejected | Member ID not found: %s",
                member_id
                )    
            print("\nMember not found. Please check the Member ID.")
            return

        # Step 8: Check available copies
        available_copies = book[3]

        if quantity > available_copies:
            connection.rollback()
            logger.warning(
                "Borrowing rejected | Insufficient copies | Book ID: %s | Available: %s | Requested: %s",
                book_id,
                available_copies,
                quantity
                )    

            print("\nInsufficient book copies.")
            print(f"Available copies: {available_copies}")
            print(f"Requested copies: {quantity}")
            return

        # Step 9: Calculate borrowing and due dates
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=14)

        # Step 10: Insert borrowing record
        insert_query = """
            INSERT INTO borrowings
            (book_id, member_id, quantity, borrow_date, due_date)
            VALUES (%s, %s, %s, %s, %s)
        """

        insert_values = (
            book_id,
            member_id,
            quantity,
            borrow_date,
            due_date
        )

        cursor.execute(insert_query, insert_values)

        borrowing_id = cursor.lastrowid

        # Step 11: Reduce available book copies
        update_query = """
            UPDATE books
            SET available_copies = available_copies - %s
            WHERE id = %s
            AND available_copies >= %s
        """

        update_values = (
            quantity,
            book_id,
            quantity
        )

        cursor.execute(update_query, update_values)

        # Ensure the book quantity was actually updated
        if cursor.rowcount != 1:
            raise RuntimeError(
                "Book availability could not be updated."
            )

        # Step 12: Commit both database operations
        connection.commit()
        logger.info(
            "Book borrowed successfully | Borrowing ID: %s | Book ID: %s | Member ID: %s | Quantity: %s",
            borrowing_id,
            book_id,
            member_id,
            quantity
        )
        # Step 13: Display borrowing confirmation
        print("\n========== BORROWING SUCCESSFUL ==========")
        print(f"Borrowing ID:       {borrowing_id}")
        print(f"Book ID:            {book[0]}")
        print(f"Book Title:         {book[1]}")
        print(f"Member ID:          {member[0]}")
        print(f"Member Name:        {member[1]}")
        print(f"Quantity Borrowed:  {quantity}")
        print(f"Borrow Date:        {borrow_date}")
        print(f"Due Date:           {due_date}")
        print(
            f"Remaining Copies:   {available_copies - quantity}"
        )

    except ValueError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning("Borrowing rejected due to invalid input: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning(
            "Borrowing failed due to database integrity constraint"
            )
        print("\nDatabase Integrity Error:")
        print(f"Details: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error during book borrowing")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error during book borrowing")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Step 14: Release database resources
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()





def view_borrowings():
    """Display all book borrowing records."""

    connection = None
    cursor = None

    try:
        print("\n========== BORROWING RECORDS ==========")

        # Step 1: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 2: Join borrowing, book, and member tables
        query = """
            SELECT
                borrowings.id,
                books.title,
                members.name,
                borrowings.quantity,
                borrowings.borrow_date,
                borrowings.due_date,
                borrowings.return_date,
                borrowings.status
            FROM borrowings
            INNER JOIN books
                ON borrowings.book_id = books.id
            INNER JOIN members
                ON borrowings.member_id = members.id
            ORDER BY borrowings.id DESC
        """

        # Step 3: Execute query
        cursor.execute(query)

        # Step 4: Retrieve all borrowing records
        borrowings = cursor.fetchall()

        # Step 5: Check whether records exist
        if not borrowings:
            logger.info("View borrowings completed | No records found")
            print("\nNo borrowing records found.")
            return
        logger.info(
    "Borrowing records retrieved successfully | Total records: %s",
    len(borrowings)
)
        # Step 6: Display borrowing records
        for borrowing in borrowings:

            print("\n----------------------------------")

            print(f"Borrowing ID:    {borrowing[0]}")
            print(f"Book Title:      {borrowing[1]}")
            print(f"Member Name:     {borrowing[2]}")
            print(f"Quantity:        {borrowing[3]}")
            print(f"Borrow Date:     {borrowing[4]}")
            print(f"Due Date:        {borrowing[5]}")
            print(
                f"Return Date:     {borrowing[6] or 'Not returned'}"
            )
            print(f"Status:          {borrowing[7].capitalize()}")

        print("\n----------------------------------")
        print(f"Total Borrowing Records: {len(borrowings)}")

    except mysql.connector.Error as error:
        logger.exception("MySQL error while retrieving borrowing records")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        logger.exception("Unexpected error while retrieving borrowing records")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Step 7: Close database resources
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()




def return_book():
    """Return borrowed books and update inventory safely."""

    connection = None
    cursor = None

    try:
        print("\n========== RETURN BOOK ==========")

        # Step 1: Get and validate Borrowing ID
        borrowing_id_input = input(
            "Enter Borrowing ID: "
        ).strip()

        try:
            borrowing_id = int(borrowing_id_input)
        except ValueError:
            raise ValueError(
                "Borrowing ID must be a valid integer."
            )

        if borrowing_id <= 0:
            raise ValueError(
                "Borrowing ID must be greater than zero."
            )

        # Step 2: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 3: Start transaction
        connection.start_transaction()

        # Step 4: Find and lock borrowing record
        borrowing_query = """
            SELECT id, book_id, member_id, quantity, status
            FROM borrowings
            WHERE id = %s
            FOR UPDATE
        """

        cursor.execute(
            borrowing_query,
            (borrowing_id,)
        )

        borrowing = cursor.fetchone()

        if borrowing is None:
            connection.rollback()
            logger.warning(
                "Return rejected | Borrowing ID not found: %s",
                borrowing_id
                )
            print("\nBorrowing record not found.")
            return

        # Step 5: Prevent duplicate returns
        if borrowing[4] == "returned":
            connection.rollback()
            logger.warning(
                "Return rejected | Already returned | Borrowing ID: %s",
                borrowing_id
                )
            print("\nThis borrowing record has already been returned.")
            return

        book_id = borrowing[1]
        quantity = borrowing[3]

        # Step 6: Find and lock the book record
        book_query = """
            SELECT id, title, total_copies, available_copies
            FROM books
            WHERE id = %s
            FOR UPDATE
        """

        cursor.execute(book_query, (book_id,))
        book = cursor.fetchone()

        if book is None:
            raise RuntimeError(
                "The book associated with this borrowing record "
                "could not be found."
            )

        # Step 7: Check inventory limit
        total_copies = book[2]
        available_copies = book[3]

        if available_copies + quantity > total_copies:
            raise RuntimeError(
                "Returning these copies would exceed the "
                "book's total inventory."
            )

        # Step 8: Update book availability
        update_book_query = """
            UPDATE books
            SET available_copies = available_copies + %s
            WHERE id = %s
            AND available_copies + %s <= total_copies
        """

        cursor.execute(
            update_book_query,
            (quantity, book_id, quantity)
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                "Book availability could not be updated."
            )

        # Step 9: Update borrowing status and return date
        return_date = date.today()

        update_borrowing_query = """
            UPDATE borrowings
            SET return_date = %s,
                status = 'returned'
            WHERE id = %s
            AND status = 'borrowed'
        """

        cursor.execute(
            update_borrowing_query,
            (return_date, borrowing_id)
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                "Borrowing record could not be updated."
            )

        # Step 10: Commit both database updates
        connection.commit()
        logger.info(
            "Book returned successfully | Borrowing ID: %s | Book ID: %s | Quantity: %s",
            borrowing_id,
            book_id,
            quantity
            )

        # Step 11: Display return confirmation
        print("\n========== BOOK RETURNED SUCCESSFULLY ==========")
        print(f"Borrowing ID:       {borrowing_id}")
        print(f"Book ID:            {book[0]}")
        print(f"Book Title:         {book[1]}")
        print(f"Quantity Returned:  {quantity}")
        print(f"Return Date:        {return_date}")
        print(
            f"Available Copies:   {available_copies + quantity}"
        )

    except ValueError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning("Book return rejected due to invalid input: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning("Book return failed due to database integrity constraint")
        print(f"\nDatabase Integrity Error: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error during book return")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error during book return")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Step 12: Release database resources
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
