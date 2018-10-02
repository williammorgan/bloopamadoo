import bloopamadoo as bpmd
import math
import random


# These are examples of custom voices made in the song file
class BassDrum(bpmd.TimedVoice):

    def get_sample(self):
        frequency = 1.0 / (self.time_in_seconds / 100 + 0.0001)
        # return math.sin(math.pi * 2 * self.time_in_seconds * frequency)
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


class SimpleEcho(bpmd.Voice):

    def __init__(self, samples_per_second, echo_delay):
        super().__init__(samples_per_second)
        self.history_size = int(samples_per_second * echo_delay)
        self.past_samples = [0] * self.history_size

    def __next__(self):
        try:
            sample = super().__next__()
        except StopIteration:
            sample = None
        self.past_samples.append(sample)
        old_sample = self.past_samples.pop(0)
        if old_sample is None:
            raise StopIteration
        else:
            if sample is None:
                sample = 0
            return sample + old_sample * 0.5


class EchoSine(SimpleEcho, bpmd.Sine):

    def __init__(self, samples_per_second):
        super().__init__(samples_per_second, 0.125)


# This is an example of a helper to load commands into the writer object.
# This might get moved into bloopamadoo if it proves reusable.
def simple_sequence(
        pitches,
        note_length,
        note_release,
        offset,
        volume,
        voice_maker,
        writer):
    for i in range(len(pitches)):
        voice = voice_maker(i)
        if not voice or pitches[i] is None:
            continue

        def note_on_command(voice=voice, i=i):
            voice.set_pitch(pitches[i])
            voice.set_volume(volume)
            writer.add_voice(voice)
        note_start_time = offset + i * note_length
        writer.add_command(note_start_time, note_on_command)

        def note_off_command(voice=voice):
            voice.release()
        note_off_time = note_start_time + note_length * note_release
        writer.add_command(note_off_time, note_off_command)


def simple_sequence_slide(
        pitches,
        note_length,
        slide_begin,
        offset,
        volume,
        voice_maker,
        writer):
    # the number of times a pitch will change durring a slide:
    num_changes = 100
    bend_length = note_length * (1 - slide_begin)

    voice = voice_maker(0)

    def note_on_command():
        voice.set_pitch(pitches[0])
        voice.set_volume(volume)
        writer.add_voice(voice)
    writer.add_command(offset, note_on_command)

    for i in range(1, len(pitches)):
        note_start = offset + note_length * (i - 1)
        bend_start = note_start + note_length * slide_begin
        for j in range(1, num_changes + 1):
            def pitch_command(i=i, j=j):
                pitch = bpmd.lerp(pitches[i - 1], pitches[i], j / num_changes)
                voice.set_pitch(pitch)
            pitch_change_time = bend_start + bend_length * (j / num_changes)
            writer.add_command(pitch_change_time, pitch_command)

    def note_off_command():
        voice.release()
    release_time = offset + note_length * len(pitches) - bend_length
    writer.add_command(release_time, note_off_command)


samples_per_second = 44100
writer = bpmd.Writer(samples_per_second)


def simple_voice_maker_maker(voice_class):
    def voice_maker(i):
        return voice_class(writer.samples_per_second)
    return voice_maker


def flat_adsr_saw_voice_maker(i):
    voice = bpmd.Saw(writer.samples_per_second)
    voice.adsr = bpmd.adsr_generator(
        0.0001, 0.0001, 1.0, 0.0001,
        samples_per_second
    )
    return voice


###
# Portamento and vibrato sinewave section
###
start_section_slides = 0.0

slide_pitches = [0, 4, 7, 12, 16, 19, 24, 19, 16, 12, 7, 4] * 1
slide_pitches = [x + 69 for x in slide_pitches]
simple_sequence_slide(
    pitches=slide_pitches, note_length=0.25, slide_begin=0.95,
    offset=start_section_slides, volume=0.25,
    voice_maker=simple_voice_maker_maker(EchoSine), writer=writer
)
slide_pitches_2 = [
    2, 5, 9,
    2 + 12, 5 + 12, 9 + 12,
    26,
    9 + 12, 5 + 12, 2 + 12,
    9, 5
] * 1
slide_pitches_2 = [x + 69 for x in slide_pitches_2]
start_section_slides_2 = start_section_slides + len(slide_pitches) * 0.25
simple_sequence_slide(
    pitches=slide_pitches_2, note_length=0.25, slide_begin=0.95,
    offset=start_section_slides_2, volume=0.25,
    voice_maker=simple_voice_maker_maker(EchoSine), writer=writer
)
start_section_slides_3 = start_section_slides_2 + len(slide_pitches_2) * 0.25
simple_sequence_slide(
    pitches=slide_pitches, note_length=0.25, slide_begin=0.95,
    offset=start_section_slides_3, volume=0.25,
    voice_maker=simple_voice_maker_maker(EchoSine), writer=writer
)
vibrato_pitches = [69.5, 68.5] * 3
start_section_slides_4 = start_section_slides_3 + len(slide_pitches) * 0.25
simple_sequence_slide(
    pitches=vibrato_pitches, note_length=0.5/len(vibrato_pitches), slide_begin=0.95,
    offset=start_section_slides_4, volume=0.25,
    voice_maker=simple_voice_maker_maker(EchoSine), writer=writer
)
end_section_slides = start_section_slides_4 + 0.5 + 0.5

###
# scale section
###
major_scale_pitches = [0, 2, 4, 5, 7, 9, 11]
major_triad = [0, 4, 7]
root_pitch = 69

arpeggio_pitches = major_triad * 6
random.shuffle(major_scale_pitches)
melody_pitches = major_scale_pitches + [12, 14, 12] + major_scale_pitches[::-1]
bassline_pitches = [
    0, None, None, None, 12, None, None, 0,
    0, None, 0, None, 12, None, 0, None
]
bassline_pitches += [
    x + 7 if x is not None else None
    for x in bassline_pitches
]
bassline_pitches += [0]

# Make pitch numbers absoulute from the root, instead of relative.
arpeggio_pitches = [x + root_pitch for x in arpeggio_pitches]
melody_pitches = [x + root_pitch for x in melody_pitches]
bassline_pitches = [
    x + root_pitch - 36 if x is not None else None
    for x in bassline_pitches
]

beat_bass = [
       1, None,  None,  None,
    None, None,     1,     1,
       1, None,     1,  None,
    None, None,  None,  None
]
beat_snare = [
    None, None,  None,  None,
       1, None,  None,  None,
    None, None,  None,  None,
       1, None,  None,  None
]
beat_bass = beat_bass * 2
beat_snare = beat_snare * 2

start_section_scale = end_section_slides
simple_sequence(
    pitches=melody_pitches, note_length=0.25, note_release=0.5,
    offset=start_section_scale, volume=0.25,
    voice_maker=simple_voice_maker_maker(bpmd.Saw), writer=writer
)
simple_sequence(
    pitches=arpeggio_pitches, note_length=1.0/24.0, note_release=1.0,
    offset=start_section_scale, volume=0.0625,
    voice_maker=flat_adsr_saw_voice_maker, writer=writer
)
simple_sequence(
    [x + 7 for x in arpeggio_pitches], 1.0/24.0, 1.0,
    start_section_scale + 2.0, 0.0625,
    flat_adsr_saw_voice_maker, writer
)
simple_sequence(
    arpeggio_pitches, 1.0/24.0, 1.0,
    start_section_scale + 4.0, 0.0625,
    flat_adsr_saw_voice_maker, writer
)
simple_sequence(
    bassline_pitches, 0.125, 0.5,
    start_section_scale, 0.25,
    simple_voice_maker_maker(bpmd.Square), writer
)
simple_sequence(
    beat_bass, 1/8.0, 1/16.0,
    start_section_scale, 0.25,
    simple_voice_maker_maker(BassDrum), writer
)
simple_sequence(
    beat_snare, 1/8.0, 1/16.0,
    start_section_scale, 0.25,
    simple_voice_maker_maker(bpmd.Noise), writer
)
end_section_scale = start_section_scale + 4.0

###
# noise_beat_section
###

start_section_noise = end_section_scale
simple_sequence(
    range(1, 17), .25, 0.75,
    start_section_noise, 1.0,
    lambda i: FilteredNoise(writer.samples_per_second), writer
)
beat_noise = [
    20, 99, 99, 99,  1,  0, 20, 99,
    20, 99, 99, 99,  1, 99, 99, 99
] * 3
simple_sequence(
    beat_noise, .25, 0.75,
    start_section_noise + 4.0, 1.0,
    lambda i: FilteredNoise(writer.samples_per_second), writer
)
beat_noise_bass = [
    1, None, None, None, None, None,    1, None,
    1, None, None, None, None, None, None, None
] * 2
simple_sequence(
    beat_noise_bass, .25, 0.75,
    start_section_noise + 8.0, 1.0,
    simple_voice_maker_maker(BassDrum), writer
)
end_section_noise = start_section_noise + 12.0

writer.write_output('demo_song.wav')
