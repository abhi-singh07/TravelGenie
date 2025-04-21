from flask import Flask, render_template, request, jsonify
import json
import os
import requests
from main import run_full_pipeline

app = Flask(__name__)

# Ensure static/assets directory exists
os.makedirs(os.path.join('static', 'assets'), exist_ok=True)

# Path to the video file
video_path = os.path.join('static', 'assets', 'travel-bg.mp4')

# Dropbox direct download URL
download_url = 'https://www.dropbox.com/scl/fi/e915eel69xzp21fps8rx8/travel-bg.mp4?rlkey=vtbhd7k90lmtter12sgruxcll&st=ziwuirvm&dl=1'

# Function to download file with error handling
def download_file(url, destination):
    print(f"Downloading travel-bg.mp4 from {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("travel-bg.mp4 downloaded successfully.")
            return True
        else:
            print(f"Failed to download travel-bg.mp4. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading travel-bg.mp4: {e}")
        return False

# Check if travel-bg.mp4 exists, attempt download if it doesn't
if not os.path.exists(video_path):
    if not download_file(download_url, video_path):
        print("Warning: Could not download travel-bg.mp4. Please place the file manually in static/assets or verify the download URL.")
else:
    print("travel-bg.mp4 already exists.")

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    usr_input = ""
    rag_data = {"user_info": {}}
    
    if request.method == 'POST':
        # Capture form data
        form_data = {
            'country': request.form['country'],
            'budget_in_usd': float(request.form['budget_in_usd']),
            'from_date': request.form['from_date'],
            'to_date': request.form['to_date'],
            'num_cities': request.form['num_cities'],
            'num_people': int(request.form['num_people']),
            'user_pref': request.form['user_pref']
        }

        # Store form data as JSON string
        usr_input = json.dumps(form_data)

        # Write to user_inputs.json
        with open("user_inputs.json", "w") as f:
            json.dump(form_data, f, indent=2)

        # Update rag_data for template rendering
        rag_data['user_info'] = form_data

        # Generate itinerary
        itinerary_result = run_full_pipeline()  # Assumed to read user_inputs.json and return itinerary text
        return jsonify({'itinerary': itinerary_result})

    return render_template('index.html', rag_data=rag_data, usr_input=usr_input)

if __name__ == '__main__':
    app.run(debug=True)