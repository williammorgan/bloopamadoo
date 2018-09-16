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

class Noise:
    def render(self, time_in_seconds, frequency):
        return random.uniform(-1.0, 1.0)

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
        value = min(value + attack_rate, 1.0)
        released = (yield value)
    while value > sustain and not released:
        value = max(value - decay_rate, sustain)
        released = (yield value)
    while not released:
        released = (yield value)
    while value > 0.0:
        value = max(value - release_rate, 0.0)
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

    def __iter__(self):
        return self

    def __next__(self):
        if self.stopped:
            raise StopIteration
        frequency = mtof(self.midi_note_number)
        sample = self.waveform.render(self.time_in_seconds, frequency)
        sample *= self.volume
        sample *= self.adsr.send(self.released)

        self.time_in_seconds += self.time_between_calls
        return sample

class Writer:
    def __init__(self, samples_per_second):
        self.samples_per_second = samples_per_second
        self.timed_commands = []
        self.voices = []

    def add_command(self, time, command):
        self.timed_commands.append((time, command))

    def add_voice(self, voice):
        self.voices.append(voice)

    def write_output(self, filename):
        final_data = bytearray()
        self.timed_commands.sort(key = lambda a: a[0])
        current_sample = 0
        while len(self.timed_commands) > 0 or len(self.voices) > 0:
            current_seconds = current_sample / 44100
            while len(self.timed_commands) > 0 and self.timed_commands[0][0] <= current_seconds:
                timed_command = self.timed_commands.pop(0)
                timed_command[1]()

            sample = 0.0
            new_voices = []
            for voice in self.voices:
                try:
                    sample += next(voice)
                    new_voices.append(voice)
                except StopIteration:
                    pass
            self.voices = new_voices

            unitless = sample / 2.0 + .5
            value = unitless * 255
            trimmed = min(max(value, 0), 255)
            final_data.append(int(trimmed))
            current_sample += 1

        wave_write = wave.open(filename, mode='wb')
        wave_write.setnchannels(1)
        wave_write.setframerate(self.samples_per_second)
        wave_write.setsampwidth(1)
        wave_write.writeframes(final_data)
        wave_write.close()

