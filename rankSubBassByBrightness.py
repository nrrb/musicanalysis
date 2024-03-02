import os
from pathlib import Path
import shutil
import cv2
import numpy as np

brightnesses = []

for top, dirs, filenames in os.walk('./images/sub-bass/all'):
    for filename in filenames:
        if filename.endswith('.png'):
            path = os.path.join(top, filename)
            img = cv2.imread(path)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            avg = np.mean(hsv[:,:, 2])
            brightnesses.append([path, avg])

brightnesses.sort(key=lambda pair: pair[1])

for rank, (src, brightness) in enumerate(brightnesses):
    print(f"{'{:3.2f}'.format(brightness)}: {src}")
    new_file = f"{str(rank).zfill(4)}-{src.split('/')[-1]}"
    top = './images/sub-bass/ranked'
    Path(top).mkdir(parents=True, exist_ok=True)
    dest = os.path.join(top, new_file)
    shutil.copyfile(src, dest)