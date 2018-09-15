import bloopamadoo as bpmd

#notes = [0, 4, 7, 0 + 12, 4 + 12, 7 + 12, 24, 7 + 12, 4 + 12, 12, 7, 4]
major_scale_notes = [0, 2, 4, 5, 7, 9, 11]
major_triad = [0, 4, 7]
#notes = [0, 2, 3, 5, 7]
root_note = 69

arpeggio_notes = major_triad * 24
melody_notes = major_scale_notes + [12, 14, 12] + major_scale_notes[::-1]
#make note numbers absoulute from the root, instead of relative.
arpeggio_notes = [x + root_note for x in arpeggio_notes]
melody_notes = [x + root_note for x in melody_notes]

bass = bpmd.BassDrum
snare = bpmd.Noise
beat_pattern = [bass,  None,  None,  None,
                snare, None,  bass,  bass,
                bass,  None,  bass,  None,
                snare, None,  None,  None]
beat = beat_pattern * 2

samples_per_second = 44100
writer = bpmd.Writer(samples_per_second)

for i in range(len(beat)):
    if beat[i] is None:
        continue;
    voice = bpmd.Voice(beat[i](), samples_per_second)
    def note_on_command(voice = voice):
        voice.set_volume(0.1)
        writer.add_voice(voice)
    writer.add_command(i / 8.0, note_on_command)
    def note_off_command(voice = voice):
        voice.release()
    writer.add_command((i / 8.0) + (1.0 / 16.0), note_off_command)

for i in range(len(arpeggio_notes)):
    voice = bpmd.Voice(bpmd.Saw(), samples_per_second)
    def note_on_command(voice = voice, i = i):
        voice.set_pitch(arpeggio_notes[i])
        voice.set_volume(.025)
        voice.adsr = bpmd.adsr_generator(0.0001, 0.0001, 1.0, 0.0001, samples_per_second)
        writer.add_voice(voice)
    writer.add_command(i / 24.0, note_on_command)
    def note_off_command(voice = voice):
        voice.release()
    writer.add_command((i / 24.0) + (1.0 / 24.0), note_off_command)

for i in range(len(melody_notes)):
    voice = bpmd.Voice(bpmd.Saw(), samples_per_second)
    def note_on_command(voice = voice, i = i):
        voice.set_pitch(melody_notes[i])
        voice.set_volume(.05)
        writer.add_voice(voice)
    writer.add_command(i / 4.0, note_on_command)
    def note_off_command(voice = voice):
        voice.release()
    writer.add_command((i / 4.0) + (1.0 / 8.0), note_off_command)

writer.write_output('demo_song.wav')
