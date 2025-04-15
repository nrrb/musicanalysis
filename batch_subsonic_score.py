#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import numpy as np
import librosa
import scipy.signal as sps
from scipy.integrate import trapezoid
from tqdm import tqdm
import warnings
import contextlib
import subprocess

@contextlib.contextmanager
def suppress_stderr():
    """Temporarily redirect standard error to /dev/null."""
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def compute_subsonic_energy(audio, sr, low_freq=20, high_freq=150, scale_factor=1e6):
    """
    Compute the total energy present in the 20–150 Hz band of an audio signal,
    normalized by track duration and scaled to make values easier to work with.
    
    Parameters:
    -----------
    audio : array
        Audio signal data
    sr : int
        Sample rate
    low_freq : int
        Lower bound of frequency range (default: 20 Hz)
    high_freq : int
        Upper bound of frequency range (default: 150 Hz)
    scale_factor : float
        Factor to scale energy values (default: 1,000,000)
        
    Returns:
    --------
    float
        Scaled energy per second value, typically above 1 for most audio tracks
    """
    # Compute the periodogram (power spectral density) of the audio.
    f, Pxx = sps.periodogram(audio, sr)
    
    # Select frequencies in the 20–150 Hz band.
    idx = (f >= low_freq) & (f <= high_freq)
    if not np.any(idx):
        return 0.0

    # Calculate total energy in the subsonic band
    sub_energy = trapezoid(Pxx[idx], f[idx])
    
    # Normalize by track duration (in seconds)
    duration = len(audio) / sr
    normalized_energy = sub_energy / duration
    
    # Apply scaling to make values more spreadsheet-friendly
    scaled_energy = normalized_energy * scale_factor
    
    return scaled_energy

def worker_process(mp3_file):
    """Worker mode: load and process one file and print CSV output line."""
    try:
        with suppress_stderr(), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            audio, sr = librosa.load(mp3_file, sr=None, mono=True)
        scaled_energy = compute_subsonic_energy(audio, sr)
        duration = len(audio) / sr
        # Print a CSV-formatted line with file path, scaled energy, and duration.
        print(f'"{mp3_file}",{scaled_energy:.2f},{duration:.2f}', flush=True)
    except Exception as e:
        # Print error message (to stderr) so that the main process can detect the failure.
        sys.stderr.write(f"Error processing '{mp3_file}': {e}\n")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Recursively compute weighted subsonic energy scores (0 to 100) for all MP3 files '
                    'in a folder and output the results to a CSV file.'
    )
    parser.add_argument('folder', type=str, nargs='?', default=None,
                        help='Path to the folder containing MP3 files.')
    parser.add_argument('--output', type=str, default='subsonic_scores.csv',
                        help='Path to the output CSV file (default: subsonic_scores.csv).')
    parser.add_argument('--process-file', type=str,
                        help='(Internal) Process a single file; used by the main process.')
    args = parser.parse_args()

    # If --process-file argument is provided, run in worker mode.
    if args.process_file:
        worker_process(args.process_file)
        return

    # Otherwise, run in main mode.
    if not args.folder:
        print("Please specify a folder containing MP3 files.")
        sys.exit(1)

    folder_path = args.folder
    output_csv = args.output

    # Recursively collect MP3 files.
    mp3_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    
    if not mp3_files:
        print("No MP3 files found in the specified folder.")
        return

    print(f"Found {len(mp3_files)} MP3 file(s). Processing...")

    # Open the output CSV file for writing.
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['mp3_path', 'scaled_subsonic_energy', 'duration_seconds'])
        
        for mp3_file in tqdm(mp3_files, desc="Processing MP3 files", unit="file"):
            try:
                # Spawn a separate process for this file.
                result = subprocess.run(
                    [sys.executable, __file__, "--process-file", mp3_file],
                    capture_output=True, text=True, check=True
                )
                # Capture standard output (the CSV line).
                line = result.stdout.strip()
                if line:
                    # Write the output line (it already contains quotes if needed).
                    csv_file.write(line + "\n")
            except subprocess.CalledProcessError as e:
                tqdm.write(f"Error processing '{mp3_file}': {e.stderr.strip()}")
            # No need to keep worker processes, since they exit after each file.

    print(f"CSV file written to {output_csv}")

if __name__ == '__main__':
    main()
