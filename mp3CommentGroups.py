from collections import defaultdict
import os
from generateMelSpectrograms import melspect
import eyed3

music_library_path = '/Users/nicholasbennett/Music/DJ Collection'

files_by_tag = defaultdict(lambda: set())

for top, dirs, filenames in os.walk(music_library_path):
    for filename in filenames:
        if filename.lower().endswith('.mp3'):
            path = os.path.join(top, filename)
            audio = eyed3.load(path)
            if len(audio.tag.comments) > 0:
                tags = audio.tag.comments[0].text.split(' ')
                for tag in tags:
                    files_by_tag[tag].add(path)

for tag in sorted(files_by_tag):
    print(f"{tag.upper()}:")
    for filename in sorted(files_by_tag[tag]):
        print(f"\t{filename}")

print(f"Now generating Mel Spectrograms for tag groups of >=10 files.")
for tag, files in files_by_tag.items():
    if len(files) >= 10:
        print(f"Tag '{tag}' has {len(files)} files.")
        for file in files:
            save_path = f"./images/tag-{tag}/{file.split('/')[-1]}.png"
            melspect(file, save_path)

