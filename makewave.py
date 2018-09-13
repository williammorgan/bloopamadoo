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

def adsr_generator(attack, decay, sustain, release, samples_per_second):
    """
    Returns a generator object that produces a series of values
    ramping over time from 0 to 1 to the sustain level and back to 0.
    attack, decay, and release are measured in seconds.
    Send True to the generator to signal the note has been released.
    """
    value = 0.0
    released = None
    attack_rate = 1.0 / (attack * samples_per_second)
    decay_rate = (1.0 - sustain) / (decay * samples_per_second)
    release_rate = sustain / (release * samples_per_second)
    while value < 1.0 and not released:
        value += attack_rate
        released = (yield value)
    while value > sustain and not released:
        value -= decay_rate
        released = (yield value)
    while not released:
        released = (yield value)
    while value > 0.0:
        value -= release_rate
        yield value

class Voice:
    def __init__(self, waveform, samples_per_second):
        self.waveform = waveform
        self.time_between_calls = 1.0 / samples_per_second
        self.time_in_seconds = 0.0
        self.volume = 1.0
        self.midi_note_number = 69
        self.adsr = adsr_generator(0.01, 0.01, 0.75, 0.1, samples_per_second)
        self.released = None
        self.stopped = False

    def set_volume(self, volume):
        self.volume = volume
    def change_volume(self, delta):
        self.volume += delta
    def set_pitch(self, midi_note_number):
        self.midi_note_number = midi_note_number
    def change_pitch(self, delta):
        self.midi_note_number += delta
    def release(self):
        self.released = True
    def stop(self):
        self.stopped = True

    def __next__(self):
        if self.stopped:
            raise StopIteration
        frequency = mtof(self.midi_note_number)
        sample = self.waveform.render(self.time_in_seconds, frequency)
        sample *= self.volume
        sample *= self.adsr.send(self.released)

        self.time_in_seconds += self.time_between_calls
        return sample

class Sine:
    def render(self, time_in_seconds, frequency):
        return math.sin(math.pi * 2 * time_in_seconds * frequency)

class Square:
    def render(self, time_in_seconds, frequency):
        from_zero_to_one = round(math.fmod(time_in_seconds * frequency, 1.0))
        return from_zero_to_one * 2.0 - 1.0

class Saw:
    def render(self, time_in_seconds, frequency):
        from_zero_to_one = math.fmod(time_in_seconds * frequency, 1.0)
        return from_zero_to_one * 2.0 - 1.0

class BassDrum:
    def render(self, time_in_seconds, frequency):
        frequency = 1.0 / (time_in_seconds / 100 + 0.0001)
        #frequency = lerp(440, 10, time_in_seconds)
        #return math.sin(math.pi * 2 * time_in_seconds * frequency)
        from_zero_to_one = math.fmod(time_in_seconds * frequency, 1.0)
        return from_zero_to_one * 2.0 - 1.0

class Noise:
    def render(self, time_in_seconds, frequency):
        return random.uniform(-1.0, 1.0)

#notes = [0, 4, 7, 0 + 12, 4 + 12, 7 + 12, 24, 7 + 12, 4 + 12, 12, 7, 4]
major_scale_notes = [0, 2, 4, 5, 7, 9, 11]
major_triad = [0, 4, 7]
#notes = major_scale_notes + [12, 14, 12] + major_scale_notes[::-1] 
#notes = [0, 2, 3, 5, 7]
notes = major_triad * 6
#make notes absoulute from middle a, instead of relative.
notes = [x + 69 for x in notes]


samples_per_second = 44100
data = bytearray()

timed_commands = []
voices = []

beat_pattern = ['bass', None, None, None, 'noise', None, 'bass', 'bass', 'bass', None, 'bass', None, 'noise', None, None, None]
beat = beat_pattern * 2
for i in range(len(beat)):
    if beat[i] == 'bass':
        voice = Voice(BassDrum(), samples_per_second)
    elif beat[i] == 'noise':
        voice = Voice(Noise(), samples_per_second)
    else:
        continue;
    def note_on_command(voice = voice):
        voice.set_volume(0.1)
        voices.append(voice)
    timed_note_on_command = (i * 44100 / 8, note_on_command)
    timed_commands.append(timed_note_on_command)
    def note_off_command(voice = voice):
        voice.release()
    timed_note_off_command = ((i * 44100 / 8) + (44100 / 16), note_off_command)
    timed_commands.append(timed_note_off_command)

for i in range(len(notes)):
    voice = Voice(Saw(), samples_per_second)
    def note_on_command(voice = voice, i = i): # I don't like that I have to do this for the closure to work correctly
        voice.set_pitch(notes[i])
        voice.set_volume(.05)
        voices.append(voice)
    timed_note_on_command = (i * 44100 / 4, note_on_command)
    timed_commands.append(timed_note_on_command)
    def note_off_command(voice = voice):
        voice.release()
    timed_note_off_command = ((i * 44100 / 4) + (44100 / 8), note_off_command)
    timed_commands.append(timed_note_off_command)

timed_commands.sort(key = lambda a: a[0])

current_sample = 0
while len(timed_commands) > 0 or len(voices) > 0:
    while len(timed_commands) > 0 and timed_commands[0][0] <= current_sample:
        timed_command = timed_commands.pop(0)
        timed_command[1]()

    sample = 0.0

    voices_to_remove = []
    for i in range(len(voices)):
        try:
            sample += next(voices[i])
        except StopIteration:
            voices_to_remove.append(i)
    new_voices = []
    for i in range(len(voices)):
        if i not in voices_to_remove:
            new_voices.append(voices[i])
    voices = new_voices

    unitless = sample / 2.0 + .5
    value = unitless * 255
    trimmed = min(max(value, 0), 255)
    data.append(int(trimmed))
    current_sample += 1

wave_write = wave.open('billtest.wav', mode='wb')
wave_write.setnchannels(1)
wave_write.setframerate(samples_per_second)
wave_write.setsampwidth(1)
wave_write.writeframes(data)
wave_write.close()

