
Smart Lost & Found — Local website with QR support
-------------------------------------------------

What it does
- Owner registers an item and gets a short Item ID and QR code image.
- QR code links to a public item page (http://127.0.0.1:5000/item/<item_id>).
- Finder opens the link (or scans QR) and submits a report; report saved in the local database.
- Admin page shows all items and reports.

How to run (Windows)
1. Unzip the package.
2. Open folder in terminal or Visual Studio Code terminal.
3. Run:
   python -m venv venv
   venv\\Scripts\\activate
   pip install -r requirements.txt
   python app.py
4. Open http://127.0.0.1:5000

How to run (macOS / Linux)
1. Unzip, open terminal in folder
2. Run:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 app.py
3. Open http://127.0.0.1:5000

Notes
- QR images are saved in static/qrcodes.
- This app runs locally. For production you'd secure the admin pages, use HTTPS, and optionally add email/SMS notifications.
