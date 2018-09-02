# The makefile looks this way because for this project I am using spaces instead of tabs, which breaks make.
# For now I am avoiding the issue by not using indentation at all.

billtest.wav: makewave.py; python3 makewave.py
listen: billtest.wav; totem billtest.wav

