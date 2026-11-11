# Library Management System

A Python and MySQL-based command-line Library Management System designed to manage books, members, borrowing operations, and library activity logs.

## Features

### Book Management
- Add new books
- View all books
- Search books
- Update book information
- Delete books safely

### Member Management
- Register members
- View all members
- Search members
- Update member information
- Delete members safely

### Borrowing Management
- Borrow books
- Return books
- Track borrowing history
- Automatically update available copies
- Calculate borrowing due dates

### Additional Features
- Input validation
- Exception handling
- MySQL database integration
- Environment variables using `.env`
- Logging with rotating log files
- Automated tests using pytest
- Transaction handling and database integrity

## Technologies Used

- Python 3.14
- MySQL
- mysql-connector-python
- python-dotenv
- Logging
- pytest
- Git and GitHub

## Project Structure

```text
library_management_system/
│
├── books.py
├── member.py
├── borrowing.py
├── database.py
├── logger_config.py
├── logs_manager.py
├── main.py
├── requirements.txt
├── .gitignore
├── .env
│
└── tests/
    ├── test_books.py
    ├── test_member.py
    ├── test_borrowing.py
    └── test_database.py
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/usmanjut302/library-management-system.git
cd library-management-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=library_management
```

Never upload your actual `.env` file or database credentials to GitHub.

### 5. Configure MySQL

Create a MySQL database named:

```sql
CREATE DATABASE library_management;
```

Create the required `books`, `members`, and `borrowings` tables using the project database schema.

### 6. Run the application

```bash
python main.py
```

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The project has previously passed 62 automated tests.

## Database Tables

| Table | Purpose |
|---|---|
| books | Stores book information and inventory |
| members | Stores registered library members |
| borrowings | Tracks borrowing and return history |

## Author

**Usman Jutt**

GitHub: https://github.com/usmanjut302

## License

This project is available for educational and portfolio purposes.