# The makefile looks this way because for this project I am using spaces instead of tabs, which breaks make.
# For now I am avoiding the issue by not using indentation at all.
test: makewave.py; python3 tests.py
demo_song.wav: demo_song.py; python3 demo_song.py
listen: demo_song.wav; totem demo_song.wav

