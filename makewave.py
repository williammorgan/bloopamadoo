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

def adsr(attack, decay, sustain, release, samples_per_second):
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

from enum import Enum
class Commands(Enum):
    set_volume = 1
    change_volume = 2
    set_pitch = 3
    change_pitch = 4
    release = 5
    stop = 6

def sine(commands, samples_per_second):
    time_between_calls = 1.0 / samples_per_second
    time_in_seconds = 0.0
    volume = 1.0
    midi_note_number = 69
    my_adsr = adsr(0.01, 0.01, 0.75, 0.1, samples_per_second)
    released = None
    while True:
        if commands is not None:
            for command, param in commands:
                if (command == Commands.set_volume):
                    volume = param
                elif (command == Commands.change_volume):
                    volume += param
                elif (command == Commands.set_pitch):
                    midi_note_number = param
                elif (command == Commands.change_pitch):
                    midi_note_number += param
                elif (command == Commands.release):
                    released = True
                elif (command == Commands.stop):
                    raise StopIteration

        frequency = mtof(midi_note_number)
        sample = math.sin(math.pi * 2 * time_in_seconds * frequency)
        sample *= volume
        sample *= my_adsr.send(released)

        commands = (yield sample)
        time_in_seconds += time_between_calls

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

instrument = Sine()
notes = [0, 4, 7, 0 + 12, 4 + 12, 7 + 12, 24, 7 + 12, 4 + 12, 12, 7, 4]
major_scale_notes = [0, 2, 4, 5, 7, 9, 11]
major_triad = [0, 4, 7]
notes = major_scale_notes + [12, 14, 12] + major_scale_notes[::-1] 
#notes = [0, 2, 3, 5, 7]



samples_per_second = 44100
song_length_seconds = 2
data = bytearray()

timed_commands = []
for i in range(len(notes)):
    note_on_command = (Commands.set_pitch, notes[i] + 69.0)
    timed_note_on_command = (i * 44100 / 4, note_on_command)
    timed_commands.append(timed_note_on_command)
    note_off_command = (Commands.release, None)
    timed_note_off_command = ((i * 44100 / 4) + (44100 / 8), note_off_command)
    timed_commands.append(timed_note_off_command)

current_sample = 1
voices = [];
while len(timed_commands) > 0 or len(voices) > 0:
    command = None
    if len(timed_commands) > 0 and timed_commands[0][0] < current_sample:
        timed_command = timed_commands.pop(0)
        if timed_command[1][0] == Commands.set_pitch:
            voices.append(sine([timed_command[1]], samples_per_second))
            command = None
        else:
            command = [timed_command[1]]
    sample = 0
    for voice in voices:
        try:
            sample += voice.send(command)
        except StopIteration:
            voices = []
    unitless = sample / 2.0 + .5
    value = unitless * 255
    trimmed = min(max(value, 0), 255)
    data.append(int(trimmed))
    current_sample += 1

'''
for x in range(0, song_length_seconds * samples_per_second):
    time_in_seconds = x / samples_per_second
    progress_through_song = time_in_seconds / song_length_seconds
    note = 69 + notes[int(progress_through_song * len(notes)*1) % len(notes)]
    positive_or_negative = instrument.render(time_in_seconds, note)
    unitless = positive_or_negative / 2.0 + .5
    value = unitless * 255
    data.append(int(value))
'''
wave_write = wave.open('billtest.wav', mode='wb')
wave_write.setnchannels(1)
wave_write.setframerate(samples_per_second)
wave_write.setsampwidth(1)
wave_write.writeframes(data)
wave_write.close()

