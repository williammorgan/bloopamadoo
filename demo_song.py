import bloopamadoo as bpmd
import math
import random

# This is an example of a custom waveform made in the song file
class BassDrum(bpmd.Waveform):
    def render(self, time_in_seconds, frequency):
        frequency = 1.0 / (time_in_seconds / 100 + 0.0001)
        #from_zero_to_one = math.sin(math.pi * 2 * time_in_seconds * frequency)
        from_zero_to_one = math.fmod(time_in_seconds * frequency, 1.0)
        return from_zero_to_one * 2.0 - 1.0

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

def simple_voice_maker_maker(waveform):
    def voice_maker(i):
        return bpmd.Voice(waveform(), writer.samples_per_second)
    return voice_maker

def flat_adsr_saw_voice_maker(i):
    voice = bpmd.Voice(bpmd.Saw(), writer.samples_per_second)
    voice.adsr = bpmd.adsr_generator(0.0001, 0.0001, 1.0, 0.0001, samples_per_second)
    return voice

simple_sequence(melody_notes, 0.25, 0.5, 0.0, 0.25, simple_voice_maker_maker(bpmd.Saw), writer)
simple_sequence(arpeggio_notes, 1.0/24.0, 1.0, 0.0, 0.0625, flat_adsr_saw_voice_maker, writer)
simple_sequence([x + 7 for x in arpeggio_notes], 1.0/24.0, 1.0, 2.0, 0.0625, flat_adsr_saw_voice_maker, writer)
simple_sequence(arpeggio_notes, 1.0/24.0, 1.0, 4.0, 0.0625, flat_adsr_saw_voice_maker, writer)
simple_sequence(bassline_notes, 0.125, 0.5, 0.0, 0.25, simple_voice_maker_maker(bpmd.Square), writer)
simple_sequence(beat_bass, 1/8.0, 1/16.0, 0.0, 0.25, simple_voice_maker_maker(BassDrum), writer)
simple_sequence(beat_snare, 1/8.0, 1/16.0, 0.0, 0.25, simple_voice_maker_maker(bpmd.Noise), writer)

writer.write_output('demo_song.wav')

