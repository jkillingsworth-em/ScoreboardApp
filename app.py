# --- Imports ---
# Flask is the web framework that runs our app and handles web requests.
# render_template sends an HTML page to the browser.
# jsonify converts Python data into JSON format that web pages can read.
from flask import Flask, render_template, jsonify

# pandas is a library for reading and working with spreadsheet/CSV data.
import pandas as pd


# --- App Setup ---
# Create the Flask application. __name__ tells Flask where to find
# supporting files like templates and static assets.
app = Flask(__name__)


# --- Load Data ---
# Read the CSV file into memory once when the app starts.
# 'df' is short for "DataFrame" — think of it as a table of rows and columns
# loaded from the spreadsheet, stored in memory so every request can use it
# without re-reading the file each time.
DATA_FILE = 'Simplified_Model_LED_Summary.csv'
try:
    df = pd.read_csv(DATA_FILE)
    print(f"[OK] Loaded '{DATA_FILE}' — {len(df)} rows, {len(df.columns)} columns.")
except FileNotFoundError:
    # The CSV is missing: print a clear message and use an empty DataFrame
    # so the app still starts and routes return empty results instead of crashing.
    print(f"[ERROR] Data file '{DATA_FILE}' not found. "
          f"Place the CSV in the same folder as app.py and restart.")
    df = pd.DataFrame()
except Exception as e:
    # Catch any other read errors (bad encoding, corrupt file, etc.)
    print(f"[ERROR] Could not load '{DATA_FILE}': {e}")
    df = pd.DataFrame()


# --- Home Page Route ---
# The @app.route('/') decorator tells Flask: "when someone visits the root URL
# of the site (e.g. http://127.0.0.1:5000/), run the function below."
@app.route('/')
def home():
    # Pull every unique value from the 'model' column and sort them
    # alphabetically. This list powers the dropdown menu on the page.
    # If the CSV failed to load, df will be empty and we send an empty list.
    model_list = sorted(df['model'].unique().tolist()) if 'model' in df.columns else []

    # Render the HTML template and pass the model list into it so the
    # template can build the dropdown options dynamically.
    return render_template('index.html', models=model_list)


# --- Data API Route ---
# This route responds to requests like /api/SomeModelName.
# The <model_name> part is a URL variable — whatever the browser sends
# there gets passed into the function as the model_name argument.
@app.route('/api/<model_name>')
def get_model_data(model_name):
    # Guard: if the CSV wasn't loaded there's nothing to filter.
    if 'model' not in df.columns:
        return jsonify([])

    # Filter the DataFrame to only the rows where the 'model' column
    # exactly matches the model name sent in the URL.
    model_info = df[df['model'] == model_name]

    # Convert pandas NaN values into JSON-safe nulls so blank CSV cells
    # don't produce invalid JSON in the browser.
    model_info = model_info.astype(object).where(pd.notna(model_info), None)

    # Drop any unnamed/blank columns produced by trailing commas in the CSV.
    model_info = model_info[[c for c in model_info.columns if c.strip() != '' and not c.startswith('Unnamed:')]]

    # Convert the filtered rows to a list of dictionaries, then wrap them
    # in jsonify so Flask sends back a proper JSON response the browser
    # (and JavaScript on the page) can easily parse.
    return jsonify(model_info.to_dict(orient='records'))


# --- Entry Point ---
# This block only runs when you execute this file directly (e.g. `python app.py`).
# It will NOT run if the file is imported as a module by another script.
if __name__ == '__main__':
    print("App is starting! Go to http://127.0.0.1:5000 in your browser.")
    # debug=True enables auto-reload when you save the file and shows
    # detailed error pages in the browser — useful during development,
    # but should be set to False in a production environment.
    app.run(debug=True)