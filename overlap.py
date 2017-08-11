import numpy as np, scipy as sp, librosa, IPython
from IPython.display import Audio

import scipy.io.wavfile

def wavwrite(filepath, data, sr, norm=True, dtype='int16',):
    '''
    Write wave file using scipy.io.wavefile.write, converting from a float (-1.0 : 1.0) numpy array to an integer array

    Parameters
    ----------
    filepath : str
    The path of the output .wav file
    data : np.array
    The float-type audio array
    sr : int
    The sampling rate
    norm : bool
    If True, normalize the audio to -1.0 to 1.0 before converting integer
    dtype : str
    The output type. Typically leave this at the default of 'int16'.
    '''
    if norm:
        data /= np.max(np.abs(data))
    data = data * np.iinfo(dtype).max
    data = data.astype(dtype)
    scipy.io.wavfile.write(filepath, sr, data)

def tempo(siga, sigb):
    atempo, abeatframes = librosa.beat.beat_track(y=siga, sr=44100)#sr)
    btempo, bbeatframes = librosa.beat.beat_track(y=sigb, sr=44100)#sr)
    if (atempo < 80):
        atempo *=2
    if (btempo < 80):
        btempo *=2
    # print "Tempos: ",atempo, btempo
    return atempo, btempo

    # Beat overlap matching testing *************************
def overlap(siga, sigb, overlap_beats, sr, fade):
    # Trim leading and trailing silence
    siga = np.trim_zeros(siga)
    sigb = np.trim_zeros(sigb)

    # Get beat frames for each track and convert to track sample indices
    atempo, abeatframes = librosa.beat.beat_track(y=siga, sr=sr)
    abeats = librosa.frames_to_samples(abeatframes)
    btempo, bbeatframes = librosa.beat.beat_track(y=sigb, sr=sr)
    bbeats = librosa.frames_to_samples(bbeatframes)

    # print atempo
    # print btempo

    # print siga.shape
    # print sigb.shape

    # print abeats.shape
    # print bbeats.shape

    # If fade is specified, cross-fade both tracks into each other
    if (fade):
        print "Fading tracks"
        fadeindices = int(bbeats[overlap_beats])
        fade = np.linspace(0, 1, num=fadeindices+1)
        for i in range(0, fade.shape[0]):
            sigb[i] *= fade[i]
            siga[siga.shape[0]-1-i] *= fade[i]

    # print "Fade indicies: ",int(bbeats[overlap_beats])

    # Create the output signal
    mix = np.zeros(sigb.shape[0]+siga.shape[0])
    # Prep it with the first track
    mix[:siga.shape[0]] = siga
    # The time frame of the beat where the second track should start
    startframe = abeats[abeats.shape[0]-overlap_beats+4]
    # print "Start frames: ",startframe,startframe-bbeats[3],startframe-bbeats[3]+sigb.shape[0]
    # print "Time beyond end of a ",(startframe-bbeats[3]+sigb.shape[0]-siga.shape[0])/44100.
    # for i in range(overlap_beats):
    #     print abeats[abeats.shape[0]-overlap_beats+i]-abeats[abeats.shape[0]-overlap_beats+i-1], bbeats[i+1]-bbeats[i]
    mix[startframe-bbeats[3]:startframe-bbeats[3]+sigb.shape[0]] += sigb
    mix = np.trim_zeros(mix)
    # print "Shape of mix ",mix.shape
    return mix

# sr = 44100
# songa, sr = librosa.load('Bounce_150.wav', sr)
# songb, sr = librosa.load('Dead_150.wav', sr)
# mix = overlap(songb, songa, 100, fade=True)
# wavwrite('mix.wav', mix, sr)
