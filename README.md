# AI PRACTICE - Flask Login/Register Example

Minimal Flask app that stores user credentials in SQLite and appends a plaintext log for compatibility.

## Setup (Windows PowerShell)

Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # or use Activate.bat on cmd
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the app

```powershell
.\.venv\Scripts\python.exe flask_app.py
```

Open http://127.0.0.1:5000/ in your browser.

## Files of interest
- `flask_app.py` — main application; creates `data.sqlite3` and writes `logi.txt`.
- `data.sqlite3` — SQLite database storing the `users` table.
- `logi.txt` — plaintext append log (for backwards compatibility).
- `templates/` — HTML templates (`index.html`, `login.html`, `register.html`, `success.html`).

## Inspect the database
Use the SQLite CLI or Python snippet to view contents (see README earlier messages for examples).

## Notes
- `requirements.txt` lists external packages to install. Standard-library modules (e.g., `os`, `sqlite3`) do not appear in it but still must be `import`ed in code.
- Passwords are now stored as hashes using `werkzeug.security.generate_password_hash`. For general security, never store raw passwords in production.
