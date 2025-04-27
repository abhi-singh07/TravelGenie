from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import requests
from main import run_full_pipeline

app = Flask(__name__)

# Ensure static/assets directory exists
os.makedirs(os.path.join('static', 'assets'), exist_ok=True)

video_path = os.path.join('static', 'assets', 'travel-bg.mp4')
download_url = 'https://www.dropbox.com/scl/fi/e915eel69xzp21fps8rx8/travel-bg.mp4?rlkey=vtbhd7k90lmtter12sgruxcll&st=ziwuirvm&dl=1'

def download_file(url, destination):
    print(f"Downloading travel-bg.mp4 from {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("travel-bg.mp4 downloaded successfully.")
            return True
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

if not os.path.exists(video_path):
    if not download_file(download_url, video_path):
        print("⚠️ Place travel-bg.mp4 manually in static/assets if download fails.")
else:
    print("✅ travel-bg.mp4 already exists.")

@app.route('/', methods=['GET', 'POST'])
def index():
    usr_input = ""
    rag_data = {"user_info": {}}

    if request.method == 'POST':
        form_data = {
            'country': request.form['country'],
            'budget_in_usd': float(request.form['budget_in_usd']),
            'from_date': request.form['from_date'],
            'to_date': request.form['to_date'],
            'num_cities': request.form['num_cities'],
            'num_people': int(request.form['num_people']),
            'user_pref': request.form['user_pref']
        }

        usr_input = json.dumps(form_data)

        with open("user_inputs.json", "w") as f:
            json.dump(form_data, f, indent=2)

        rag_data['user_info'] = form_data

        # Run pipeline
        itinerary_result = run_full_pipeline()

        # Save as markdown
        markdown_path = "static/assets/generated_itinerary.md"
        with open(markdown_path, "w") as f:
            f.write("# ✈️ AI-Generated Travel Itinerary\n\n")
            f.write(itinerary_result)

        return jsonify({'itinerary': itinerary_result, 'download_link': '/download_md'})

    return render_template('index.html', rag_data=rag_data, usr_input=usr_input)

@app.route('/download_md')
def download_md():
    return send_file("static/assets/generated_itinerary.md", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
