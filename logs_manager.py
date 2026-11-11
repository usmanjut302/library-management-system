
from pathlib import Path


LOG_FILE = Path(__file__).parent / "logs" / "library.log"


# ==========================================
# READ LOG FILE
# ==========================================

def read_logs():

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return file.readlines()

    except FileNotFoundError:
        print("\nLog file does not exist.")
        return []

    except PermissionError:
        print("\nPermission denied while reading log file.")
        return []

    except OSError as error:
        print(f"\nUnable to read log file: {error}")
        return []


# ==========================================
# VIEW ALL LOGS
# ==========================================

def view_all_logs():

    print("\n========== ALL ACTIVITY LOGS ==========")

    logs = read_logs()

    if not logs:
        print("\nNo log records found.")
        return

    for log in logs:
        print(log, end="")

    print(f"\nTotal Log Records: {len(logs)}")


# ==========================================
# VIEW RECENT LOGS
# ==========================================

def view_recent_logs():

    print("\n========== RECENT ACTIVITY LOGS ==========")

    logs = read_logs()

    if not logs:
        print("\nNo log records found.")
        return

    try:
        limit = int(input("\nHow many recent logs do you want to view? "))

        if limit <= 0:
            print("\nPlease enter a positive number.")
            return

    except ValueError:
        print("\nInvalid number.")
        return

    recent_logs = logs[-limit:]

    for log in recent_logs:
        print(log, end="")

    print(f"\nDisplayed {len(recent_logs)} recent log records.")


# ==========================================
# SEARCH LOGS
# ==========================================

def search_logs():

    print("\n========== SEARCH ACTIVITY LOGS ==========")

    logs = read_logs()

    if not logs:
        print("\nNo log records found.")
        return

    keyword = input("\nEnter a keyword to search: ").strip()

    if not keyword:
        print("\nSearch keyword cannot be empty.")
        return

    matching_logs = [
        log for log in logs
        if keyword.lower() in log.lower()
    ]

    if not matching_logs:
        print("\nNo matching log records found.")
        return

    for log in matching_logs:
        print(log, end="")

    print(f"\nMatching Records: {len(matching_logs)}")


# ==========================================
# VIEW ERROR LOGS
# ==========================================

def view_error_logs():

    print("\n========== ERROR LOGS ==========")

    logs = read_logs()

    error_logs = [
        log for log in logs
        if "| ERROR |" in log or "| CRITICAL |" in log
    ]

    if not error_logs:
        print("\nNo error records found.")
        return

    for log in error_logs:
        print(log, end="")

    print(f"\nTotal Error Records: {len(error_logs)}")
