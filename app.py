from flask import Flask, render_template, request, send_from_directory
from urllib.parse import urlparse, parse_qs
import requests
import os
import uuid

app = Flask(__name__)

API_ENDPOINT = 'https://webbedwordycases.jamesgrant18.repl.co/api/v1/summarize'
RESULTS_DIR = 'results'  # The directory to store the results

# Create the RESULTS_DIR if it doesn't exist
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    youtube_url = request.form.get('youtube_url')

    if not is_youtube_url(youtube_url):
        return render_template('index.html', error='Invalid YouTube URL')

    try:
        response = requests.post(API_ENDPOINT, data={'youtube_url': youtube_url})

        if response.status_code == 200:
            result_id = str(uuid.uuid4())  # Generate a unique identifier
            file_path = os.path.join(RESULTS_DIR, f"{result_id}.txt")

            # Save the results to a file
            with open(file_path, "w") as result_file:
                result_file.write(response.text)

            # Read the results from the file
            with open(file_path, "r") as result_file:
                result_text = result_file.read()

            return render_template('result.html', result=result_text, result_id=result_id)
        else:
            error = "Error: " + str(response.status_code)
            return render_template('index.html', error=error)

    except Exception as e:
        error = "Error: " + str(e)
        return render_template('index.html', error=error)

@app.route('/result/<result_id>')
def serve_result(result_id):
    file_path = os.path.join(RESULTS_DIR, f"{result_id}.txt")

    # Read the results from the file
    with open(file_path, "r") as result_file:
        result_text = result_file.read()
    return render_template('result.html', result=result_text, result_id=result_id)

def is_youtube_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc == 'www.youtube.com' and parse_qs(parsed_url.query).get('v')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
