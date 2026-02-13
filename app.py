import os
from flask import Flask, jsonify, render_template, send_from_directory, request
from threading import Thread
from datetime import datetime, timezone, timedelta
import scaper
import excel_exporter
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


os.makedirs("res", exist_ok=True)
key = os.getenv('KEY')

@app.route("/")
def index():
    # list files in the res directory and render simple HTML with links
    try:
        files = sorted(os.listdir("res"))
    except Exception:
        files = []
    
    # build html
    links = "".join(
        f'<li><a href="/res/{fname}" download>{fname}</a></li>' for fname in files
    )
    html = f"""
    <html>
    <head><title>Available exports</title></head>
    <body>
      <h1>Available files</h1>
      <ul>
        {links}
      </ul>
    </body>
    </html>
    """
    return html

def _perform_update(frm, to, url):
    """Worker function running in background thread."""
    data = scaper.scrape_data(FROM=frm, TO=to, URL=url)
    # compute current date/time in IST (UTC+5:30)
    ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    timestamp = ist.strftime("%d-%m-%Y")
    filename = f"res/export-[{frm} - {to}] [Date Updated - {timestamp}].xlsx"
    excel_exporter.export_to_excel(data, filename)


@app.route("/update", methods=["GET"])
def update_excel():
    # top‑level security: require key query parameter matching environment
    provided_key = request.args.get('key')
    if provided_key is None or provided_key != key:
        return jsonify({"error": "invalid or missing key"}), 403

    # accept `from` and `to` as query parameters; fall back to 0 if absent or invalid
    try:
        frm = int(request.args.get('from', 0))
    except ValueError:
        frm = 0
    try:
        to = int(request.args.get('to', 0))
    except ValueError:
        to = 0

    URL = os.getenv('URL')
    # launch background thread so the request returns immediately
    Thread(target=_perform_update, args=(frm, to, URL), daemon=True).start()

    return 'Update started; data will be available on / when complete.'

@app.route("/res/<path:filename>")
def serve_res_files(filename):
    return send_from_directory("res", filename)

if __name__ == "__main__":
    app.run()
