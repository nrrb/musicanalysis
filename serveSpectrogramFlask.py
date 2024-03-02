import os
from tempfile import NamedTemporaryFile
from flask import Flask, request, send_file
import librosa
import librosa.display
from matplotlib.figure import Figure
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            # Process the file and generate spectrogram
            temp_file = NamedTemporaryFile(delete=False)
            file.save(temp_file.name)
            spectrogram_image = generate_spectrogram(temp_file.name, file.filename)
            os.unlink(temp_file.name)  # Delete the temp file
            return send_file(spectrogram_image, mimetype='image/png')
    return '''
    <!doctype html>
    <title>Upload MP3 File</title>
    <h1>Upload MP3 File to Generate Spectrogram</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['mp3']

def generate_spectrogram(file_path, original_filename):
    y, sr = librosa.load(file_path, sr=None)
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    fig = Figure()
    ax = fig.subplots()
    img = librosa.display.specshow(D, sr=sr, ax=ax, x_axis='time', y_axis='log')
    ax.set(title=f"Spectrogram - {original_filename.split('/')[-1]}")
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    temp_image = NamedTemporaryFile(delete=False, suffix='.png')
    fig.savefig(temp_image.name)
    return temp_image.name

if __name__ == '__main__':
    app.run(debug=False)
