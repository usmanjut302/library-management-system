
from database import get_connection

from books import (
    add_book,
    delete_book,
    search_book,
    update_book,
    view_books
)

from member import (
    delete_member,
    register_member,
    search_member,
    update_member,
    view_members
)

from borrowing import (
    borrow_book,
    view_borrowings,
    return_book
)
from logs_manager import (
    view_all_logs,
    view_recent_logs,
    search_logs,
    view_error_logs
)

from logger_config import logger


# ==========================================
# APPLICATION STARTUP
# ==========================================

def check_database_connection():

    connection = None

    try:
        connection = get_connection()

        if connection.is_connected():
            print(
                "\nSuccessfully connected to "
                "Library Management System database!"
            )

            logger.info("Database connection successful")

            return True

    except Exception:
        logger.exception("Database connection failed")
        print("\nDatabase connection failed. Check your configuration.")

        return False

    finally:
        if connection is not None and connection.is_connected():
            connection.close()


# ==========================================
# ACTION EXECUTION
# ==========================================

def execute_action(action, action_name):

    logger.info("%s menu option selected", action_name)

    try:
        action()

    except Exception:
        logger.exception("Unexpected error while executing %s", action_name)
        print("\nAn unexpected error occurred.")

    input("\nPress Enter to continue...")


# ==========================================
# BOOK MANAGEMENT MENU
# ==========================================

def book_menu():

    while True:

        print("\n========== BOOK MANAGEMENT ==========")
        print("1. Add Book")
        print("2. View Books")
        print("3. Search Book")
        print("4. Update Book")
        print("5. Delete Book")
        print("6. Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            execute_action(add_book, "Add Book")

        elif choice == "2":
            execute_action(view_books, "View Books")

        elif choice == "3":
            execute_action(search_book, "Search Book")

        elif choice == "4":
            execute_action(update_book, "Update Book")

        elif choice == "5":
            execute_action(delete_book, "Delete Book")

        elif choice == "6":
            logger.info("Returned from Book Management menu")
            break

        else:
            logger.warning("Invalid Book Management menu choice: %s", choice)
            print("\nInvalid choice. Please try again.")


# ==========================================
# MEMBER MANAGEMENT MENU
# ==========================================

def member_menu():

    while True:

        print("\n========== MEMBER MANAGEMENT ==========")
        print("1. Register Member")
        print("2. View Members")
        print("3. Search Member")
        print("4. Update Member")
        print("5. Delete Member")
        print("6. Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            execute_action(register_member, "Register Member")

        elif choice == "2":
            execute_action(view_members, "View Members")

        elif choice == "3":
            execute_action(search_member, "Search Member")

        elif choice == "4":
            execute_action(update_member, "Update Member")

        elif choice == "5":
            execute_action(delete_member, "Delete Member")

        elif choice == "6":
            logger.info("Returned from Member Management menu")
            break

        else:
            logger.warning("Invalid Member Management menu choice: %s", choice)
            print("\nInvalid choice. Please try again.")


# ==========================================
# BORROWING AND RETURNING MENU
# ==========================================

def borrowing_menu():

    while True:

        print("\n========== BORROWING & RETURNING ==========")
        print("1. Borrow Book")
        print("2. View Borrowing Records")
        print("3. Return Book")
        print("4. Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            execute_action(borrow_book, "Borrow Book")

        elif choice == "2":
            execute_action(view_borrowings, "View Borrowings")

        elif choice == "3":
            execute_action(return_book, "Return Book")

        elif choice == "4":
            logger.info("Returned from Borrowing menu")
            break

        else:
            logger.warning("Invalid Borrowing menu choice: %s", choice)
            print("\nInvalid choice. Please try again.")



# ==========================================
# ACTIVITY LOGS MENU
# ==========================================

def logs_menu():

    while True:

        print("\n========== ACTIVITY LOGS ==========")
        print("1. View All Logs")
        print("2. View Recent Logs")
        print("3. Search Logs")
        print("4. View Error Logs")
        print("5. Back to Main Menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            execute_action(view_all_logs, "View All Logs")

        elif choice == "2":
            execute_action(view_recent_logs, "View Recent Logs")

        elif choice == "3":
            execute_action(search_logs, "Search Logs")

        elif choice == "4":
            execute_action(view_error_logs, "View Error Logs")

        elif choice == "5":
            logger.info("Returned from Activity Logs menu")
            break

        else:
            logger.warning("Invalid Activity Logs menu choice: %s", choice)
            print("\nInvalid choice. Please try again.")



# ==========================================
# MAIN MENU
# ==========================================

def main():

    if not check_database_connection():
        return

    logger.info("Library Management System started")

    while True:

        print("\n")
        print("=" * 45)
        print("       LIBRARY MANAGEMENT SYSTEM")
        print("=" * 45)

        print("1. Book Management")
        print("2. Member Management")
        print("3. Borrowing & Returning")
        print("4. Activity Logs")
        print("5. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            logger.info("Book Management menu opened")
            book_menu()

        elif choice == "2":
            logger.info("Member Management menu opened")
            member_menu()

        elif choice == "3":
            logger.info("Borrowing & Returning menu opened")
            borrowing_menu()

        elif choice == "4":
            logger.info("Activity Logs menu opened")
            logs_menu()

        elif choice == "5":
            logger.info("Library Management System closed")
            print("\nThank you for using Library Management System!")
            break

        else:
            logger.warning("Invalid main menu choice: %s", choice)
            print("\nInvalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        logger.warning("Application interrupted by user")
        print("\n\nApplication interrupted. Goodbye!")
