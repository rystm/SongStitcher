# SongStitcher
## What It Is

SongStitcher makes seamless transitions between songs a reality. 
It takes in two songs, shifts the tempo of one or both songs, 
and overlaps the songs by a specified number of beats, on the beat. 
It also gives the option to cross-fade the songs. 
The goal is to have no interruption in tempo, so that dancers can stay in their groove. 
The way to do that is to line up beats in the first song with beats in the second song, 
after they have been shifted to have matching tempos at the end of the first song and beginning of the next.


## How It Works

SongStitcher is based on several pre-existing features in audio manipulation, 
namely beat tracking and phase vocoding, or changing the tempo of a song without changing pitch. 
The program takes in two songs, then beat tracks both to find the tempos. 
Based on the user's selection, one tempo is picked as the unifying tempo (or the two are averaged), 
and the song(s) that need(s) to be sped up or slowed down are run through the phase vocoder.

Now there are two audio files at the same tempo. 
They are both run through a beat tracker again to find the sample indices of each beat. 
Then the second song is added to the first song, 
with the fourth beat of song two matched up with the fourth beat in the overlap window for the first song. 
The fourth beat is used so that any fuzziness at the beginning of the beat tracking is ignored, 
and the rest of the transition is on beat.

This project uses Librosa, a Python library for music and audio processing, 
for its beat tracker and tempo detector. 
The Python/C library Aubio was also used for its phase vocoder, 
and the body of the code is based on their timestretch demo found at 
https://dev.aubio.org/browser/python/demos/demo_timestretch.py?rev=dd18484ebbd743e05cd1ddf0f3d71c722fff0109. 
It uses numpy for storing audio, and either Librosa or Aubio to read and write the songs that are being edited.

## Sample Usage

After downloading the files and opening a terminal in the correct folder,
run this (you will need numpy, librosa, and aubio installed):

python songstitcher.py Boundless_170.wav Bounce_150 -b 75 -f 1 -t 1 -o BoundlessBounceMix_170.wav

This command takes the two songs, overlaps them by 75 beats, cross-fades the volume,
and makes the overall tempo match that of the first song.
The output file, BoundlessBounceMix_170.wav, is saved in the working directory.

This command run as-is will put the transition somewhere around 2:35

## Testing/Results

Originally, we had decided to partially time-shift songs as they progressed, 
so that they slowly and smoothly sped up or slowed down until they reached the target transition tempo. 
During testing, we found that this caused a number of rather difficult issues. 
The original beat-track data did not work for the time-shifted audio, 
and beat-tracking a partially time-shifted audio file is very difficult. 
Given more time and experience, and the ability to write our own specialized beat-tracker, 
we feel that we would be able to eventually solve these issues 
and successfully beat-track a partially time-shifted audio file, 
at least enough that we could reliably overlap two tracks that were partially time-shifted to the same tempo. 
Instead, we lowered our expectations, and time-shifted entire tracks. 
Instead of a song's tempo changing as it progressed, now the song plays at its adjusted tempo the whole time.

We tested SongStitcher with songs from two general genres: EDM and pop. 
We looked for songs that generally had a relatively driving beat, though not necessarily the whole time. 
Our songs were all in the general range of 120bpm to 150bpm. This specific range is not important, 
but we found that songs with a tempo difference of greater than 30bpm did not overlap well. 
Additionally, the more something was time-shifted, the worse the beat-tracker did. 
Somehow, the process of running audio through a phase vocoder does something to the audio 
that makes beat-tracking more difficult. SongStitcher works well for songs that Librosa can beat-track well. 
If that works, then the overlap works. However, if something in an audio file throws off the beat-tracker, 
then the overlap will be imperfect. This means SongStitcher is effective on a narrow range of music. 
However, it is this narrow range (EDM, House, etc) that SongStitcher would be marketed towards. 
When used on music from those genres, many transitions sounded qualitatively very successful. 
The ideal songs have: a continuous, driving beat; few breaks in the beat for verses; 
tempos within ~30bpm of each other.

Devs: Ryan Miller and Kaitlyn MacIntyre

See more at songstitcher.weebly.com