# Copyright (C) 2018  William Morgan
import wave
import math
import random


def mtof(midi_note_number):
    """
    Turns midi note number into frequency
    """
    return 440.0 * pow(2, (midi_note_number - 69) / 12)


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


def center(sample_from_zero_to_one):
    """
    Take a sample in the range 0 to 1 and centers it to the range -1 to 1
    """
    return sample_from_zero_to_one * 2.0 - 1.0


def adsr_generator(attack, decay, sustain, release, samples_per_second):
    """
    Returns a generator object that produces a series of values
    ramping over time from 0 to 1 to the sustain level and back to 0.
    attack, decay, and release are measured in seconds and cannot be 0.
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
    """
    The Voice class produces samples to be consumed by the Writer.
    It can accept calls to change it's volume and pitch parameters, or stop.
    """

    def __init__(self, samples_per_second):
        self.samples_per_second = samples_per_second
        self.volume = 1.0
        self.set_pitch(69)
        self.stopped = False

    def set_volume(self, volume):
        self.volume = volume

    def change_volume(self, delta):
        self.volume += delta

    def set_pitch(self, midi_note_number):
        self.frequency = mtof(midi_note_number)
        self.pitch = midi_note_number

    def change_pitch(self, delta):
        self.set_pitch(self.pitch + delta)

    def stop(self):
        self.stopped = True

    def get_sample(self):
        """
        Derived classes should implement this function to produce sound.
        """
        raise NotImplementedError

    def __iter__(self):
        return self

    def __next__(self):
        if self.stopped:
            raise StopIteration
        sample = self.get_sample()
        sample *= self.volume
        return sample


class AdsrVoice(Voice):
    """
    Modifies the volume of a voice's samples using an ADSR Envelope.
    """
    def __init__(self, samples_per_second):
        super().__init__(samples_per_second)
        self.adsr = adsr_generator(0.01, 0.01, 0.75, 0.1, samples_per_second)
        self.released = None

    def release(self):
        self.released = True

    def __next__(self):
        sample = super().__next__()
        sample *= self.adsr.send(self.released)
        return sample


class TimedVoice(AdsrVoice):
    """
    Keeps track of the time since the voice started playing.
    """
    def __init__(self, samples_per_second):
        super().__init__(samples_per_second)
        self.time_between_calls = 1.0 / samples_per_second
        self.time_in_seconds = 0.0

    def __next__(self):
        sample = super().__next__()
        self.time_in_seconds += self.time_between_calls
        return sample


class TableVoice(AdsrVoice):
    """
    Uses a table to represent one period of the waveform and
    keeps the current phase offset, so that changes to the pitch
    can be made without causing discontinuities in the output.
    """
    # To be overwritten with a waveform shape in derived classes.
    table = [0]

    def __init__(self, samples_per_second):
        super().__init__(samples_per_second)
        self.current_phase = 0

    def get_sample(self):
        table_len = len(self.table)
        value = self.table[int(self.current_phase)]
        rate = table_len * self.frequency / self.samples_per_second
        self.current_phase = math.fmod(self.current_phase + rate, table_len)
        return value


class Sine(TableVoice):
    """
    A sinusoidal waveform that smoothly goes from 0 to 1 to -1 and back to 0.
    It is like the y coordinate of a unit circle unwrapped couterclockwise.
    """
    table = [
        math.sin(i / 44100 * 2 * math.pi)
        for i in range(0, 44100)
    ]


class Saw(TableVoice):
    """
    A waveform that ramps up to one value linearly but jumps back down.
    """
    table = [
        center(i / 44100)
        for i in range(0, 44100)
    ]


class Square(TableVoice):
    """
    A waveform that jumps back and forth between two values discontinuously.
    """
    table = [
        center(round(i / 44100))
        for i in range(0, 44100)
    ]


class Triangle(TableVoice):
    """
    A waveform that ramps linearly back and forth between two values.
    """
    table = [
        center(i / 22050 if i <= 22050 else 1 - (i - 22050) / 22050)
        for i in range(0, 44100)
    ]


class Noise(AdsrVoice):
    """
    White noise, jumping discontinuously to random values with equal chance.
    """
    def get_sample(self):
        return random.uniform(-1.0, 1.0)


class Writer:
    """
    The writer mixes together samples from voices and writes them to a file.
    While it goes through the voices, sample by sample, it will execute
    commands added to it for specific times.  These commands can add more
    voices, change their properties, etc.
    When a voice runs out of samples and raises StopIteration, it is no
    longer checked for samples.

    To use it, you load it up with commands and call write_output().
    """
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
        self.timed_commands.sort(key=lambda a: a[0])
        current_sample = 0
        while len(self.timed_commands) > 0 or len(self.voices) > 0:
            current_seconds = current_sample / 44100
            while len(self.timed_commands) > 0 and \
                    self.timed_commands[0][0] <= current_seconds:
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

            # The signal might have gone too big or small.
            # Clip it between -1 and 1.
            trimmed = min(max(sample, -1), 1.0)

            # 16-bit samples are stored as 2's-complement signed integers,
            # ranging from -32768 to 32767.
            as_int = int(trimmed * 32767.5 - 0.5)
            bytes = as_int.to_bytes(2, byteorder='little', signed=True)

            final_data.append(bytes[0])
            final_data.append(bytes[1])

            current_sample += 1

        wave_write = wave.open(filename, mode='wb')
        wave_write.setnchannels(1)
        wave_write.setframerate(self.samples_per_second)
        wave_write.setsampwidth(2)
        wave_write.writeframes(final_data)
        wave_write.close()
