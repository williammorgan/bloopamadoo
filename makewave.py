import wave
import math

def mtof(midi_note_number):
    """
    Turns midi note number into frequency
    """
    #d = 69 + 12 log(base = 2, of = (f / 440.0))
    #(d - 69) / 12 = log(base = 2, of = (f / 440.0))
    #pow(base = 2, of = (d - 69) / 12) = f / 440.0
    #440.0 * pow(base = 2, of = (d - 69) / 12) = f
    return 440.0 * pow(2, (midi_note_number - 69) / 12);

notes = [0, 4, 7, 0 + 12, 4 + 12, 7 + 12, 24, 7 + 12, 4 + 12, 12, 7, 4]

samples_per_second = 44100
song_length_seconds = 2
data = bytearray()
for x in range(0, song_length_seconds * samples_per_second):
    time_in_seconds = x / samples_per_second
    progress_through_song = time_in_seconds / song_length_seconds
    frequency = mtof(69+notes[int(progress_through_song * len(notes)*1) % len(notes)])
    positive_or_negative = math.sin(math.pi * 2 * time_in_seconds * frequency)
    unitless = positive_or_negative / 2.0 + .5
    value = unitless * 255
    data.append(int(value))

wave_write = wave.open('billtest.wav', mode='wb')
wave_write.setnchannels(1)
wave_write.setframerate(samples_per_second)
wave_write.setsampwidth(1)
wave_write.writeframes(data)
wave_write.close()

