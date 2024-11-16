from flask import Flask
from flask import Flask, render_template, request, jsonify
import files


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='Study Flow')

@app.route('/uploadForm', methods=['GET', 'POST'])
def uploadFiles():
    return render_template("uploadFile.html", title = "Upload Files Form")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    return files.handle_file_upload(file)

if __name__ == '__main__':
    app.run(debug=True)
