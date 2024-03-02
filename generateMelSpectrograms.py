import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import librosa

def melspect(mp3_path, save_path):
    y, sr = librosa.load(mp3_path)
    mel_spect = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512)
    mel_spect = librosa.power_to_db(mel_spect, ref=np.max)
    fig, ax = plt.subplots()
    img = librosa.display.specshow(mel_spect, x_axis='time', y_axis='mel', ax=ax)
    ax.set(title=mp3_path.split('/')[-1])
    # fig.colorbar(img, ax=ax, format="%+2.f dB")
    top = '/'.join(save_path.split('/')[:-1])
    Path(top).mkdir(parents=True, exist_ok=True)
    ax.axis('off')
    fig.savefig(save_path, bbox_inches='tight')
    plt.close(fig)

if __name__=="__main__":
    # Generate Mel Spectrograms for everything to start with
    for top, dirs, filenames in os.walk('/Users/nicholasbennett/Music/DJ Collection'):
        for filename in filenames:
            if filename.lower().endswith('.mp3'):
                path = os.path.join(top, filename)
                print(path)
                melspect(mp3_path=path, save_path=f"./images/all/{filename}.png")


