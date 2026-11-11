
import mysql.connector

from database import get_connection
from logger_config import logger

def register_member():
    """Register a new member in the library."""

    connection = None
    cursor = None

    try:
        print("\n========== REGISTER NEW MEMBER ==========")

        # Step 1: Collect member information
        name = input("Enter member name: ").strip()
        email = input("Enter member email: ").strip()
        phone = input("Enter member phone (optional): ").strip()

        # Step 2: Validate member information
        if not name:
            raise ValueError("Member name cannot be empty.")

        if not email:
            raise ValueError("Member email cannot be empty.")

        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Please enter a valid email address.")

        # Step 3: Prepare SQL query
        query = """
            INSERT INTO members
            (name, email, phone)
            VALUES (%s, %s, %s)
        """

        values = (
            name,
            email,
            phone or None
        )

        # Step 4: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 5: Execute query
        cursor.execute(query, values)

        # Step 6: Save database changes
        connection.commit()
        logger.info(
            "Member registered successfully | Member ID: %s",
            cursor.lastrowid
        )
        # Step 7: Display confirmation
        print("\nMember registered successfully!")
        print(f"Member ID: {cursor.lastrowid}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone or 'Not provided'}")

    except ValueError as error:
        logger.warning("Member registration rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
            logger.warning(
                "Member registration failed due to database integrity constraint"
            )
        print("\nDatabase Integrity Error:")
        print("This email may already be registered.")
        print(f"Details: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error during member registration")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error during member registration")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Close cursor and database connection
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()








def view_members():
    """Display all registered library members."""

    connection = None
    cursor = None

    try:
        print("\n========== REGISTERED MEMBERS ==========")

        # Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Retrieve all members
        query = """
            SELECT id, name, email, phone, created_at
            FROM members
            ORDER BY id
        """

        cursor.execute(query)

        members = cursor.fetchall()

        # Check whether members exist
        if not members:
            logger.info("View members completed | No members found")
            print("\nNo members registered yet.")
            return
        logger.info(
            "Members retrieved successfully | Total members: %s",
            len(members)
            )
        # Display each member
        for member in members:
            print("\n----------------------------------")
            print(f"Member ID:   {member[0]}")
            print(f"Name:        {member[1]}")
            print(f"Email:       {member[2]}")
            print(f"Phone:       {member[3] or 'Not provided'}")
            print(f"Joined Date: {member[4]}")

        print("\n----------------------------------")
        print(f"Total Members: {len(members)}")

    except mysql.connector.Error as error:
        logger.exception("MySQL error while retrieving members")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        logger.exception("Unexpected error while retrieving members")
        print(f"\nUnexpected Error: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()







def search_member():
    """Search for library members by ID, name, or email."""

    connection = None
    cursor = None

    try:
        print("\n========== SEARCH MEMBERS ==========")
        print("1. Search by Member ID")
        print("2. Search by Member Name")
        print("3. Search by Email")
        print("4. Back")

        choice = input("\nChoose a search option: ").strip()

        # Search by Member ID
        if choice == "1":

            member_id_input = input("Enter Member ID: ").strip()

            try:
                member_id = int(member_id_input)
            except ValueError:
                raise ValueError(
                    "Member ID must be a valid integer."
                )

            if member_id <= 0:
                raise ValueError(
                    "Member ID must be greater than zero."
                )

            query = """
                SELECT id, name, email, phone, created_at
                FROM members
                WHERE id = %s
            """

            values = (member_id,)
            search_type = "single"

        # Search by Member Name
        elif choice == "2":

            name = input(
                "Enter member name or keyword: "
            ).strip()

            if not name:
                raise ValueError(
                    "Member name cannot be empty."
                )

            query = """
                SELECT id, name, email, phone, created_at
                FROM members
                WHERE name LIKE %s
                ORDER BY id
            """

            values = (f"%{name}%",)
            search_type = "multiple"

        # Search by Email
        elif choice == "3":

            email = input(
                "Enter email or keyword: "
            ).strip()

            if not email:
                raise ValueError(
                    "Email cannot be empty."
                )

            query = """
                SELECT id, name, email, phone, created_at
                FROM members
                WHERE email LIKE %s
                ORDER BY id
            """

            values = (f"%{email}%",)
            search_type = "multiple"

        # Return to previous menu
        elif choice == "4":
            logger.info("Member search cancelled")
            print("\nReturning to the previous menu.")
            return

        else:

            raise ValueError(
                "Invalid option. Please choose 1, 2, 3, or 4."
            )

        # Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Execute search query
        cursor.execute(query, values)

        # Retrieve matching records
        if search_type == "single":
            members = cursor.fetchone()

            if members is not None:
                members = [members]
            else:
                members = []

        else:
            members = cursor.fetchall()

        # Check search results
        if not members:
            logger.info("Member search completed | No matching members found")
            print("\nNo matching members found.")
            return

        # Display matching members
        print("\n========== SEARCH RESULTS ==========")

        for member in members:

            print("\n----------------------------------")
            print(f"Member ID:   {member[0]}")
            print(f"Name:        {member[1]}")
            print(f"Email:       {member[2]}")
            print(f"Phone:       {member[3] or 'Not provided'}")
            print(f"Joined Date: {member[4]}")

        print("\n----------------------------------")
        logger.info(
            "Member search completed successfully | Matching members: %s",
            len(members)
            )
        print(f"Matching Members: {len(members)}")

    except ValueError as error:
        logger.warning("Member search rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.Error as error:
        logger.exception("MySQL error during member search")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        logger.exception("Unexpected error during member search")
        print(f"\nUnexpected Error: {error}")

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()





def update_member():
    """Update an existing library member's information."""

    connection = None
    cursor = None

    try:
        print("\n========== UPDATE MEMBER ==========")

        # Step 1: Get and validate Member ID
        member_id_input = input("Enter Member ID to update: ").strip()

        try:
            member_id = int(member_id_input)
        except ValueError:
            raise ValueError("Member ID must be a valid integer.")

        if member_id <= 0:
            raise ValueError("Member ID must be greater than zero.")

        # Step 2: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 3: Retrieve existing member
        select_query = """
            SELECT id, name, email, phone
            FROM members
            WHERE id = %s
        """

        cursor.execute(select_query, (member_id,))
        member = cursor.fetchone()

        if member is None:
            logger.warning(
                "Member update failed | Member ID not found: %s",
                member_id
            )
            print("\nMember not found. Please check the Member ID.")
            return

        # Step 4: Display existing information
        print("\n========== CURRENT MEMBER DETAILS ==========")
        print(f"Member ID: {member[0]}")
        print(f"Name:      {member[1]}")
        print(f"Email:     {member[2]}")
        print(f"Phone:     {member[3] or 'Not provided'}")

        # Step 5: Collect new information
        print("\nEnter new details.")
        print("Press ENTER to keep the existing value.")
        print("For phone, type 'clear' to remove the existing number.")

        name_input = input("\nNew name: ").strip()
        email_input = input("New email: ").strip()
        phone_input = input("New phone: ").strip()

        # Step 6: Decide which values to keep or update
        new_name = name_input if name_input else member[1]
        new_email = email_input if email_input else member[2]

        if phone_input.lower() == "clear":
            new_phone = None
        elif phone_input:
            new_phone = phone_input
        else:
            new_phone = member[3]

        # Step 7: Validate new information
        if not new_name:
            raise ValueError("Member name cannot be empty.")

        if not new_email:
            raise ValueError("Member email cannot be empty.")

        if "@" not in new_email or "." not in new_email.split("@")[-1]:
            raise ValueError("Please enter a valid email address.")

        # Step 8: Prepare UPDATE query
        update_query = """
            UPDATE members
            SET name = %s,
                email = %s,
                phone = %s
            WHERE id = %s
        """

        values = (
            new_name,
            new_email,
            new_phone,
            member_id
        )

        # Step 9: Execute and save changes
        cursor.execute(update_query, values)
        connection.commit()
        logger.info(
            "Member updated successfully | Member ID: %s",
            member_id
            )
        # Step 10: Display updated information
        print("\nMember updated successfully!")
        print(f"Member ID: {member_id}")
        print(f"Name:      {new_name}")
        print(f"Email:     {new_email}")
        print(f"Phone:     {new_phone or 'Not provided'}")

    except ValueError as error:
        logger.warning("Member update rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()

        logger.warning(
            "Member update failed due to database integrity constraint"
            )
        print("\nDatabase Integrity Error:")
        print("This email may already belong to another member.")
        print(f"Details: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error during member update")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error during member update")
        print(f"\nUnexpected Error: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()





def delete_member():
    """Delete a member if no borrowing history prevents deletion."""

    connection = None
    cursor = None

    try:
        print("\n========== DELETE MEMBER ==========")

        # Step 1: Get and validate Member ID
        member_id_input = input("Enter Member ID to delete: ").strip()

        try:
            member_id = int(member_id_input)
        except ValueError:
            raise ValueError("Member ID must be a valid integer.")

        if member_id <= 0:
            raise ValueError("Member ID must be greater than zero.")

        # Step 2: Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Step 3: Check whether member exists
        select_query = """
            SELECT id, name, email, phone, created_at
            FROM members
            WHERE id = %s
        """

        cursor.execute(select_query, (member_id,))
        member = cursor.fetchone()

        if member is None:
            logger.warning(
                "Member deletion failed | Member ID not found: %s",
                member_id
                )
            print("\nMember not found. Please check the Member ID.")
            return

        # Step 4: Display member information
        print("\n========== MEMBER DETAILS ==========")
        print(f"Member ID:   {member[0]}")
        print(f"Name:        {member[1]}")
        print(f"Email:       {member[2]}")
        print(f"Phone:       {member[3] or 'Not provided'}")
        print(f"Joined Date: {member[4]}")

        # Step 5: Ask for deletion confirmation
        confirmation = input(
            "\nAre you sure you want to delete this member? (y/n): "
        ).strip().lower()

        if confirmation == "n":
            logger.info(
                "Member deletion cancelled by user | Member ID: %s",
                member_id
                )
            print("\nMember deletion cancelled.")
            return

        if confirmation != "y":
            logger.info(
                "invalid confirmation | Member ID: %s",
                member_id
                )
            raise ValueError(
                "Invalid confirmation. Please enter y or n."
            )

        # Step 6: Delete member
        delete_query = """
            DELETE FROM members
            WHERE id = %s
        """

        cursor.execute(delete_query, (member_id,))

        # Step 7: Save changes
        connection.commit()
        logger.info(
            "Member deleted successfully | Member ID: %s",
            member_id
            )

        print("\nMember deleted successfully!")

    except ValueError as error:
        logger.warning("Member deletion rejected: %s", error)
        print(f"\nInput Error: {error}")

    except mysql.connector.IntegrityError as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.warning(
            "Member deletion blocked by database integrity constraint | Member ID: %s",
            member_id
            )
        print("\nDatabase Integrity Error:")
        print(
            "This member cannot be deleted because borrowing "
            "history may reference this member."
        )
        print(f"Details: {error}")

    except mysql.connector.Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("MySQL error during member deletion")
        print(f"\nMySQL Error: {error}")

    except Exception as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        logger.exception("Unexpected error during member deletion")
        print(f"\nUnexpected Error: {error}")

    finally:
        # Step 8: Release database resources
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
