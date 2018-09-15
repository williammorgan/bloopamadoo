# The makefile looks this way because for this project I am using spaces instead of tabs, which breaks make.
# For now I am avoiding the issue by not using indentation at all.
listen: demo_song.wav; totem demo_song.wav
demo_song.wav: *.py; python3 demo_song.py
test: ; python3 tests.py

