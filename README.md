# Bloopamadoo
This project is a minimalist toy music synthesizer made purely for fun.

It requires python 3.6 and nothing else, no 3rd party libraries or anything.
All the synthesis is done from scratch.

To listen to the demonstration wave file, enter:

    python3 demo_song.py

and then listen to the generated 'demo_song.wav' file in your favorite media player.

If you are on Ubuntu, you can simply type `make` or `make listen` and the demo song wave file will be created and played in one step with the default installed 'totem' media player.  This method allows faster iterations.

The intended usage is that you just `import bloopamadoo` into your song file 
and then write python code to create and structure your song.  

Your song file makes sounds by adding `Voice`s to the `Writer` with commands to manipulate the voices at certain times.
Then call `Writer.write_output()` and the writer goes sample by sample, asking the voices for their samples and executing any commands scheduled for that time.  Look at `demo_song.py` for an example.

## Potential future work:
 * Improved score notation in the song file, including rythm.
 * Vibrato demonstration
 * Group Filters
 * longer demo song
 * ADSR change messages on a playing voice without restarting the adsr_generator.

