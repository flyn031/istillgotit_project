# I Still Got It - Player Showcase Platform

## Overview

"I Still Got It" is a Django/PostgreSQL web application designed for young or returning football (soccer), cricket, and rugby players. It allows them to create detailed profiles, upload highlight videos, list performance statistics, and potentially connect with scouts, agents, and teams.

## Features

*   User Authentication (Sign Up, Log In, Log Out) using Django's built-in system + Custom User Model
*   Player Profile Creation & Editing (Bio, Sport, DOB, Location, Avatar)
*   Video Uploads & Management (Title, Description, Thumbnail, Comments)
*   Statistical Tracking:
    *   Physical Stats (Height, Weight, Speed, Agility tests, etc.)
    *   Match Recording (Opponent, Competition, Date)
    *   Detailed Performance Stats per Match (Goals, Assists, Runs, Wickets, Tries, Tackles, etc.)
*   Profile Browsing/Searching (Basic implementation)
*   Form Rendering using Crispy Forms with Bootstrap 5 styling
*   [Add any other key features, e.g., Video Rating, Player Levels]

## Technology Stack

*   **Backend:** Python 3.9+, Django 4.2+
*   **Database:** PostgreSQL
*   **Frontend:** HTML, CSS, Bootstrap 5
*   **Forms:** Django Forms, django-crispy-forms, crispy-bootstrap5
*   **Environment Variables:** python-dotenv
*   **Deployment (Example):** Gunicorn/Nginx (or Heroku, PythonAnywhere, etc.)

## Prerequisites

*   Python (version 3.9 or as specified in `runtime.txt` if created)
*   PostgreSQL Server (running locally or accessible)
*   Git

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/flyn031/istillgotit_project.git
    cd istillgotit_project
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows use: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project root directory (`istillgotit_project/`).
    *   Copy the following structure, replacing placeholder values with your actual settings (especially `SECRET_KEY` and `DB_PASSWORD`):
        ```dotenv
        # .env
        SECRET_KEY='your_strong_random_secret_```markdown
# I Still Got It - Player Showcase Platform

## Overview

"I Still Got It" is a Django/PostgreSQL web application designed for young or returning football (soccer), cricket, and rugby players. It allows them to create detailed profiles, upload highlight videos, list performance statistics, and potentially connect with scouts, agents, and teams.

## Features

*   User Authentication (Sign Up, Log In, Log Out)
*   Player Profile Creation & Editing (Bio, Sport, DOB, Location, Avatar)
*   Video Uploads & Management (Title, Description, Thumbnail, Comments)
*   Statistical Tracking:
    *   Physical Stats (Height, Weight, Speed, Agility tests, etc.)
    *   Match Recording (Opponent, Competition, Date)
    *   Detailed Performance Stats per Match (Goals, Assists, Runs, Wickets, Tries, Tackles, etc.)
*   Profile Browsing/Searching (Basic implementation)
*   [Add any other key features, e.g., Video Rating, Player Levels]

## Technology Stack

*   **Backend:** Python 3.9+, Django 4.2+
*   **Database:** PostgreSQL
*   **Frontend:** HTML, CSS, Bootstrap 5
*   **Forms:** Django Forms, django-crispy-forms, crispy-bootstrap5
*   **Environment Variables:** python-dotenv
*   **Deployment (Example):** Gunicorn/Nginx (or Heroku, PythonAnywhere, etc.)

## Prerequisites

*   Python (version specified in `runtime.txt` or >= 3.9)
*   PostgreSQL Server (running locally or accessible)
*   Git

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/flyn031/istkey_here' # Replace this!
        DEBUG=True
        ALLOWED_HOSTS=localhost,127.0.0.1

        DB_NAME=istillgotit_db
        DB_USER=your_postgres_username # e.g., isgi_illgotit_project.git
    cd istillgotit_project
    ```

2.  **Create and Activate Virtual Environment:**
    ```admin or your OS username (james.oflynn)
        DB_PASSWORD=your_postgres_password #bash
    python3 -m venv venv
    source venv/bin/activate Replace this!
        DB_HOST=localhost # Or your DB host if different
        DB_PORT=5432      
    # On Windows use: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project root directory (`istillgotit_project/`).
    *   Copy the contents of `.env.example` (if you create one) or add the following structure, replacing placeholder values with your actual settings:
        ```dotenv
        # .env
        SECRET_KEY='your_strong_random_secret_key_here'
        DEBUG=True
        ALLOWED_HOSTS=localhost,127.0.0.1

        DB_NAME=istillgotit_db
        DB_USER=your_postgres_username # e.g., isgi_admin or your OS username
        DB_PASSWORD=your_postgres_password# Or your DB port if different

        # Optional: Email settings
        # EMAIL_HOST=...
        # ...
        ```
    *   **Important:** Generate a strong `SECRET_KEY`. Do *not* use the default insecure key. Change the example `DB_PASSWORD`.

5.  **Setup PostgreSQL Database:**
    *   Ensure your PostgreSQL server is running.
    *   Ensure the database user specified in `DB_USER` exists (e.g., `isgi_admin` or `james.oflynn`).
    *   Ensure the database specified in `DB_NAME` exists and is owned by `DB_USER`. If you needed to reset it earlier, you can use commands like these (run as a PostgreSQL superuser like `james.oflynn`):
        ```
        DB_HOST=localhost # Or your DB host if different
        DB_PORT=5432bash
        # Example commands if needed:
        psql -U your_superuser -h localhost -d postgres -c "DROP DATABASE IF EXISTS istillgotit_db;"
        psql -U your_superuser -h localhost -d postgres -c "CREATE DATABASE istillgotit_db OWNER your_db_user;"
        # Replace your_superuser (e.g., james.ofly      # Or your DB port if different

        # Optional: Email settings
        # EMAIL_HOST=...
        # ...
        ```
    *   **Important:** Generate a strong `SECRET_KEY`. Do *not* use the default insecure key. Change the example database password.

5.  **Setup PostgreSQL Database:**
    *   Ensure your PostgreSQL server is running.
    *   Create the database user specified in `DB_USER` if it doesn't exist.
    *   Create the database specified in `DB_NAME`. The user `DB_USER` needs to be the owner or have sufficient privileges. Example using `psql` (run as a PostgreSQL superuser like `postgres` or your OS username):
        ```bash
        # Connect as superuser first if needed
        psql -U your_superuser -h localhost -d postgres

        # Inside psql or as separate commands:
        CREATE DATABASE istillgotit_db OWNER your_db_user;
        # Ifnn) and your_db_user (e.g., isgi_admin)
         user doesn't exist: CREATE USER your_db_user WITH PASSWORD 'your_postgres_password';
        # If user needs privileges:```

6.  **Apply Database Migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Create Superuser (Admin):**
    ``` GRANT ALL PRIVILEGES ON DATABASE istillgotit_db TO your_db_user;
        bash
    python manage.py createsuperuser
    ```

6.  **Apply Database Migrations:**
    ``````
    (Follow prompts for username, email, password)

8.  **Run Development Server:**
    ```bash
    python manage.py runserver
    ```

9.  **Access the Application:** Open your web browser and go to `http://127.0.0.1:8000/`. Access the admin interface at `http://127.0.0.1:8000/admin/`.

## [Optional Sections]

### Running Tests

```bash
    python manage.py migrate
    ```

7.  **Create Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    bash
# (Ass```
    (Follow prompts for username, email, password)

8.  **Run Development Server:**
    ```bash
    python manage.umes you have written tests in tests.py files)
python manage.py test