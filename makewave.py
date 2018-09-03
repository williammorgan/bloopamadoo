import wave
import math
import random

def mtof(midi_note_number):
    """
    Turns midi note number into frequency
    """
    return 440.0 * pow(2, (midi_note_number - 69) / 12);

def ftom(frequency):
    """
    Turns frequency into midi note number
    """
    return 69 + 12 * math.log(frequency / 440.0, 2)

def lerp(a, b, t):
    """
    Linearly interpolate between a and b,
    producing a value that is t bettween a and b.
    """
    return a + (b-a) * t

class Sine:
    def render(self, time_in_seconds, midi_note_number):
        frequency = mtof(midi_note_number)
        return math.sin(math.pi * 2 * time_in_seconds * frequency)

class Square:
    def render(self, time_in_seconds, midi_note_number):
        frequency = mtof(midi_note_number)
        from_zero_to_one = round(math.fmod(time_in_seconds * frequency, 1.0))
        return from_zero_to_one * 2.0 - 1.0

class Saw:
    def render(self, time_in_seconds, midi_note_number):
        frequency = mtof(midi_note_number)
        from_zero_to_one = math.fmod(time_in_seconds * frequency, 1.0)
        return from_zero_to_one * 2.0 - 1.0

class BassDrum:
    def render(self, time_in_seconds, midi_note_number):
        frequency = 1.0 / (time_in_seconds / 100 + 0.0001)
        #frequency = lerp(440, 10, time_in_seconds)
        #return math.sin(math.pi * 2 * time_in_seconds * frequency)
        from_zero_to_one = math.fmod(time_in_seconds * frequency, 1.0)
        return from_zero_to_one * 2.0 - 1.0

class Noise:
    def render(self, time_in_seconds, midi_note_number):
        return random.uniform(-1.0, 1.0)

instrument = Noise();
notes = [0, 4, 7, 0 + 12, 4 + 12, 7 + 12, 24, 7 + 12, 4 + 12, 12, 7, 4]

samples_per_second = 44100
song_length_seconds = 2
data = bytearray()
for x in range(0, song_length_seconds * samples_per_second):
    time_in_seconds = x / samples_per_second
    progress_through_song = time_in_seconds / song_length_seconds
    note = 69 + notes[int(progress_through_song * len(notes)*1) % len(notes)]
    positive_or_negative = instrument.render(time_in_seconds, note)
    unitless = positive_or_negative / 2.0 + .5
    value = unitless * 255
    data.append(int(value))

wave_write = wave.open('billtest.wav', mode='wb')
wave_write.setnchannels(1)
wave_write.setframerate(samples_per_second)
wave_write.setsampwidth(1)
wave_write.writeframes(data)
wave_write.close()

