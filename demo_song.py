import bloopamadoo as bpmd
import math
import random

# These are examples of custom voices made in the song file
class BassDrum(bpmd.TimedVoice):
    def get_sample(self):
        frequency = 1.0 / (self.time_in_seconds / 100 + 0.0001)
        #return math.sin(math.pi * 2 * self.time_in_seconds * frequency)
        from_zero_to_one = math.fmod(self.time_in_seconds * frequency, 1.0)
        return from_zero_to_one * 2.0 - 1.0

class FilteredNoise(bpmd.Noise):
    def __init__(self, samples_per_second):
        super().__init__(samples_per_second)
        self.history_size = 100
        self.past_samples = [0] * self.history_size
    def __next__(self):
        sample = super().__next__()
        self.past_samples.append(sample)
        self.past_samples.pop(0)
        num_samples = self.pitch
        if num_samples:
            return sum(self.past_samples[-num_samples:]) / num_samples
        else:
            return 0.0

# This is an example of a helper to load commands into the writer object.
# This might get moved into bloopamadoo if it proves reusable.
def simple_sequence(notes, note_length, note_release, offset, volume, voice_maker, writer):
    for i in range(len(notes)):
        voice = voice_maker(i)
        if not voice or notes[i] is None:
            continue
        def note_on_command(voice = voice, i = i):
            voice.set_pitch(notes[i])
            voice.set_volume(volume)
            writer.add_voice(voice)
        note_start_time = offset + i * note_length
        writer.add_command(note_start_time, note_on_command)
        def note_off_command(voice = voice):
            voice.release()
        writer.add_command(note_start_time + note_length * note_release, note_off_command)

# These are the notes used by the scale section
major_scale_notes = [0, 2, 4, 5, 7, 9, 11]
major_triad = [0, 4, 7]
root_note = 69

arpeggio_notes = major_triad * 6
#arpeggio_notes = [0, 4, 7, 0 + 12, 4 + 12, 7 + 12, 24, 7 + 12, 4 + 12, 12, 7, 4] * 4
#random.shuffle(major_scale_notes)
melody_notes = major_scale_notes + [12, 14, 12] + major_scale_notes[::-1]
bassline_notes = [0, None, None, None, 12, None, None, 0, 0, None, 0, None, 12, None, 0, None]
bassline_notes = bassline_notes + [x + 7 if not x is None else None for x in bassline_notes] + [0]

#make note numbers absoulute from the root, instead of relative.
arpeggio_notes = [x + root_note for x in arpeggio_notes]
melody_notes = [x + root_note for x in melody_notes]
bassline_notes = [x + root_note - 36 if not x is None else None for x in bassline_notes]


beat_bass = [1,    None,  None,  None,
             None, None,  1,     1,
             1,    None,  1,     None,
             None, None,  None,  None]
beat_snare = [None, None,  None,  None,
              1,    None,  None,  None,
              None, None,  None,  None,
              1,    None,  None,  None]
beat_bass = beat_bass * 2
beat_snare = beat_snare * 2

samples_per_second = 44100
writer = bpmd.Writer(samples_per_second)

def simple_voice_maker_maker(voice_class):
    def voice_maker(i):
        return voice_class(writer.samples_per_second)
    return voice_maker

def flat_adsr_saw_voice_maker(i):
    voice = bpmd.Saw(writer.samples_per_second)
    voice.adsr = bpmd.adsr_generator(0.0001, 0.0001, 1.0, 0.0001, samples_per_second)
    return voice

# scale section
start_scale_section = 0.0
simple_sequence(melody_notes, 0.25, 0.5, start_scale_section, 0.25, simple_voice_maker_maker(bpmd.Saw), writer)
simple_sequence(arpeggio_notes, 1.0/24.0, 1.0, start_scale_section, 0.0625, flat_adsr_saw_voice_maker, writer)
simple_sequence([x + 7 for x in arpeggio_notes], 1.0/24.0, 1.0, start_scale_section + 2.0, 0.0625, flat_adsr_saw_voice_maker, writer)
simple_sequence(arpeggio_notes, 1.0/24.0, 1.0, start_scale_section + 4.0, 0.0625, flat_adsr_saw_voice_maker, writer)
simple_sequence(bassline_notes, 0.125, 0.5, start_scale_section, 0.25, simple_voice_maker_maker(bpmd.Square), writer)
simple_sequence(beat_bass, 1/8.0, 1/16.0, start_scale_section, 0.25, simple_voice_maker_maker(BassDrum), writer)
simple_sequence(beat_snare, 1/8.0, 1/16.0, start_scale_section, 0.25, simple_voice_maker_maker(bpmd.Noise), writer)
scale_section_over = start_scale_section + 4.0

# noise_beat_section
start_noise_beat = scale_section_over
simple_sequence(range(1, 17), .25, 0.75, start_noise_beat, 1.0, lambda i: FilteredNoise(writer.samples_per_second), writer)
beat_noise = [20, 99, 99, 99, 1, 0, 20, 99, 20, 99, 99, 99, 1, 99, 99, 99]*3
simple_sequence(beat_noise, .25, 0.75, start_noise_beat + 4.0, 1.0, lambda i: FilteredNoise(writer.samples_per_second), writer)
beat_noise_bass = [1, None, None, None, None, None, 1, None, 1, None, None, None, None, None, None, None]*2
simple_sequence(beat_noise_bass, .25, 0.75, start_noise_beat + 8.0, 1.0, simple_voice_maker_maker(BassDrum), writer)
noise_beat_over = start_noise_beat + 12.0

def slide_note(start_pitch, end_pitch, duration, start_time, writer):
    voice = bpmd.Triangle(writer.samples_per_second);
    def note_on_command():
        voice.set_pitch(start_pitch)
        writer.add_voice(voice)
    writer.add_command(start_time-duration, note_on_command)

    num_changes = 101
    for i in range(num_changes):
        def pitch_command(i = i):
            voice.set_pitch(bpmd.lerp(start_pitch, end_pitch, i / float(num_changes - 1)))
        writer.add_command(start_time + duration * (i / float(num_changes - 1)), pitch_command)

    def finish_up():
        voice.release()
    writer.add_command(start_time + duration + duration, finish_up)

slide_note(root_note - 12 * 4, root_note, 3 * 0.25, noise_beat_over - 3 * 0.25, writer)

writer.write_output('demo_song.wav')

