from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# 1. Load the "Kitchen" (The Data)
# This reads your CSV file into the app's memory.
DATA_FILE = 'Simplified_Model_LED_Summary.csv'
df = pd.read_csv(DATA_FILE)

@app.route('/')
def home():
    # This finds all the UNIQUE model names for the dropdown menu.
    model_list = sorted(df['model'].unique().tolist())
    return render_template('index.html', models=model_list)

@app.route('/api/<model_name>')
def get_model_data(model_name):
    # This searches the CSV for the model you picked and gets the board info.
    model_info = df[df['model'] == model_name]
    # We turn it into a format the web page understands (JSON).
    return jsonify(model_info.to_dict(orient='records'))

if __name__ == '__main__':
    # This starts your "Waiter" service.
    print("App is starting! Go to http://127.0.0.1:5000 in your browser.")
    app.run(debug=True)