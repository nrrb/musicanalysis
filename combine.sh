ffmpeg -framerate 2.5 -pattern_type glob -i 'tag-techno/*.png' -vf scale=512:400,format=yuv420p tag-techno-noaudio.mp4

ffmpeg -i tag-techno-noaudio.mp4 -i '/Users/nicholasbennett/Music/DJ Collection/Delayron - Research.mp3' -c:a copy -shortest -codec:v libx264 -codec:a aac -b:a 320k tag-techno.mp4


ffmpeg -framerate 2.53 -pattern_type glob -i 'all/*.png' -vf scale=512:400,format=yuv420p all-noaudio.mp4

ffmpeg -i all-noaudio.mp4 -i "/Users/nicholasbennett/Music/DJ Collection/No_4mat - 1992.mp3" -c:a copy -shortest -codec:v libx264 -codec:a aac -b:a 320k all.mp4