from partial_pv import *
from overlap import *
import numpy as np

# Read in command line arguments
# ex: songstitcher.py songOne.wav songTwo.wav -b 100 -f 1 -t 1.5 -o outputSong.wav
if len(sys.argv) < 11:
    print "Error: not enough arguments.  Please enter the names of both songs, followed by "
    print "-b and the number of overlapping beats, -f and whether you want it crossfaded, "
    print "-t and what you want the overlap tempo to be, and -o and the output song name."
else:
    first_song = sys.argv[1]
    second_song = sys.argv[2]
    overlap_beats = int(sys.argv[4])
    fade = int(sys.argv[6])
    overlap_tempo = float(sys.argv[8])
    output_name = sys.argv[10]

print "Loading songs"
sr = 44100
songa, sr = librosa.load(first_song, sr)
songb, sr = librosa.load(second_song, sr)

win_s = 1024
hop_s = win_s // 8 # 87.5 % overlap

bpm_1, bpm_2 = tempo(songa, songb)

bps_1 = bpm_1 / 60
bps_2 = bpm_2 / 60

t1 = overlap_beats / bps_2
t2 = overlap_beats / bps_2

if overlap_tempo == 1:
    rate1 = 1.0
    rate2 = bpm_1/bpm_2
elif overlap_tempo == 1.5:
    bpm_final = (bpm_1+bpm_2)/2.0
    rate1 = bpm_final/bpm_1
    rate2 = bpm_final/bpm_2
elif overlap_tempo == 2:
    rate1 = bpm_2/bpm_1
    rate2 = 1.0

div = int(abs(rate1-rate2)/0.05)
change_rate = 0.05

source_in_1 = source(first_song, 0, hop_s)
source_in_2 = source(second_song, 0, hop_s)

samplerate = source_in_1.samplerate
p = pvoc(win_s, hop_s)

# allocate memory to store norms and phases
dur_1 = source_in_1.duration
dur_2 = source_in_2.duration
n_blocks_1 = dur_1 // hop_s + 1
n_blocks_2 = dur_2 // hop_s + 1

# adding an empty frame at end of spectrogram
norms_1  = np.zeros((n_blocks_1 + 1, win_s // 2 + 1), dtype = float_type)
phases_1 = np.zeros((n_blocks_1 + 1, win_s // 2 + 1), dtype = float_type)
norms_2  = np.zeros((n_blocks_2 + 1, win_s // 2 + 1), dtype = float_type)
phases_2 = np.zeros((n_blocks_2 + 1, win_s // 2 + 1), dtype = float_type)

block_read_1 = 0
while True:
    # read from source
    samples, read = source_in_1()
    # compute fftgrain
    spec = p(samples)
    # store current grain
    norms_1[block_read_1] = spec.norm
    phases_1[block_read_1] = spec.phas
    # until end of file
    if read < hop_s: break
    # increment block counter
    block_read_1 += 1

block_read_2 = 0
while True:
    # read from source
    samples, read = source_in_2()
    # compute fftgrain
    spec = p(samples)
    # store current grain
    norms_2[block_read_2] = spec.norm
    phases_2[block_read_2] = spec.phas
    # until end of file
    if read < hop_s: break
    # increment block counter
    block_read_2 += 1

sink_out_1 = sink('shift_a.wav', samplerate)
sink_out_2 = sink('shift_b.wav', samplerate)

print "Changing tempos"
# if only the first song changes tempo
if overlap_tempo == 2:
    timestretch(rate1, samplerate, dur_1, win_s, hop_s, n_blocks_1, norms_1, phases_1, p, block_read_1, sink_out_1)
    sink_out_1.close()
    pvsonga, sr = librosa.load('shift_a.wav', sr)
    pvsongb, sr = librosa.load(second_song, sr)

# if only the second song changes tempo
elif overlap_tempo == 1:
    timestretch(rate2, samplerate, dur_2, win_s, hop_s, n_blocks_2, norms_2, phases_2, p, block_read_2, sink_out_2)
    sink_out_2.close()
    pvsonga, sr = librosa.load(first_song, sr)
    pvsongb, sr = librosa.load('shift_b.wav', sr)

# if both songs change tempo
elif overlap_tempo == 1.5:
    timestretch(rate1, samplerate, dur_1, win_s, hop_s, n_blocks_1, norms_1, phases_1, p, block_read_1, sink_out_1)
    timestretch(rate2, samplerate, dur_2, win_s, hop_s, n_blocks_2, norms_2, phases_2, p, block_read_2, sink_out_2)
    sink_out_1.close()
    sink_out_2.close()
    pvsonga, sr = librosa.load('shift_a.wav', sr)
    pvsongb, sr = librosa.load('shift_b.wav', sr)

print "Mixing tracks"
mix = overlap(pvsonga, pvsongb, overlap_beats, sr, fade)
wavwrite(output_name, mix, sr)
