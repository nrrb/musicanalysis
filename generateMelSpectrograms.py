import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import librosa

def melspect(mp3_path, save_path, label=True, fmin=None, fmax=None, n_mels=None):
    y, sr = librosa.load(mp3_path)
    if not fmin:
        fmin = 0
    if not fmax:
        fmax = sr / 2.0
    if n_mels:
        mel_spect = librosa.feature.melspectrogram(y=y,
                                                   sr=sr,
                                                   n_fft=2048,
                                                   hop_length=512,
                                                   fmin=fmin,
                                                   fmax=fmax,
                                                   n_mels=n_mels)
    else:
        mel_spect = librosa.feature.melspectrogram(y=y,
                                                   sr=sr,
                                                   n_fft=2048,
                                                   hop_length=512,
                                                   fmin=fmin,
                                                   fmax=fmax)
    mel_spect = librosa.power_to_db(mel_spect, ref=np.max)
#    mel_spect = librosa.power_to_db(mel_spect, ref=np.median)
    fig, ax = plt.subplots()
    img = librosa.display.specshow(mel_spect, x_axis='time', y_axis='mel', ax=ax)
    if label:
        ax.set(title=mp3_path.split('/')[-1])
    # fig.colorbar(img, ax=ax, format="%+2.f dB")
    top = '/'.join(save_path.split('/')[:-1])
    Path(top).mkdir(parents=True, exist_ok=True)
    ax.axis('off')
    fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

if __name__=="__main__":
    # Generate Mel Spectrograms for everything to start with
    for top, dirs, filenames in os.walk('/Users/nicholasbennett/Music/DJ Collection'):
        for filename in filenames:
            if filename.lower().endswith('.mp3'):
                path = os.path.join(top, filename)
                print(path)
#                melspect(mp3_path=path, save_path=f"./images/all/{filename}.png")
                melspect(mp3_path=path,
                         save_path=f"./images/sub-bass/all/{filename}.png",
                         label=False,
                         fmin=20,
                         fmax=60,
                         n_mels=7)

