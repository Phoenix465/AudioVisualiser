import wave
from dataclasses import dataclass
from math import floor
from os import listdir, rename
from os.path import basename, isfile, join, abspath
from random import choice

import glm
import numpy as np
import pyaudio
from pydub import AudioSegment

import quadHandler


def InitializeMusicDirectory(musicPath, oldMusicPath, converterPath, ffmpegPath, ffprobePath):
    #AudioSegment.convert = overallFfmpegPath
    AudioSegment.converter = converterPath
    AudioSegment.ffmpeg = ffmpegPath
    AudioSegment.ffprobePath = ffprobePath

    audioFiles = []

    for file in [f for f in listdir(musicPath) if isfile(join(musicPath, f))]:
        if file.endswith(".mp3"):
            origFile = abspath(join(musicPath, file))

            newFile = file.replace('.mp3', '.wav')
            newFileFull = join(musicPath, newFile)

            print(f"Converting '{file}' => '{newFile}' ... ", end="")

            newSound = AudioSegment.from_mp3(fr"{origFile}")
            newSound.export(newFileFull, format="wav")
            rename(origFile, abspath(join(oldMusicPath, file)))

            print("FINISHED")

            audioFiles.append(newFile)

        elif file.endswith(".wav"):
            print(f"Loaded '{file}'")
            audioFiles.append(file)
        else:
            print(f"'{file}' Is UNSUPPORTED")

    print()

    return audioFiles


def audioDataToArray(soundData, sampleWidth, channels):
    sampleNumber, remainder = divmod(len(soundData), sampleWidth * channels)

    if remainder > 0:
        raise ValueError('The length of data is not a multiple of '
                         'sampleWidth * channels.')
    if sampleWidth > 4:
        raise ValueError("sampleWidth must not be greater than 4.")

    if sampleWidth == 3:
        a = np.empty((sampleNumber, channels, 4), dtype=np.uint8)
        raw_bytes = np.frombuffer(soundData, dtype=np.uint8)
        a[:, :, :sampleWidth] = raw_bytes.reshape(-1, channels, sampleWidth)
        a[:, :, sampleWidth:] = (a[:, :, sampleWidth - 1:sampleWidth] >> 7) * 255
        result = a.view('<i4').reshape(a.shape[:-1])
    else:
        dt_char = 'u' if sampleWidth == 1 else 'i'
        a = np.frombuffer(soundData, dtype='<%s%d' % (dt_char, sampleWidth))
        result = a.reshape(-1, channels)

    return result


@dataclass
class SoundData:
    data: bytes
    read: bool
    waveFile: wave.Wave_read
    rewind: bool
    pause: bool


class SoundHandler:
    def __init__(self, songPath):
        self.chunkSize = 1024
        self.songPath = songPath

        soundFile = wave.open(songPath, "rb")
        self.sampleWidth = soundFile.getsampwidth()
        self.frameRate = soundFile.getframerate()
        self.channels = soundFile.getnchannels()
        self.frames = soundFile.getnframes()

        self.pyAudioObj = pyaudio.PyAudio()

        self.soundDataHolder = SoundData(
            data=b'',
            read=False,
            waveFile=soundFile,
            rewind=False,
            pause=False,
        )

        def callback(in_data, frame_count, time_info, status):
            if not self.soundDataHolder.pause:
                data = soundFile.readframes(frame_count)

                self.soundDataHolder.data = data
                self.soundDataHolder.read = len(data) < frame_count * self.sampleWidth * self.channels

                if self.soundDataHolder.read:
                    print("Finished")
                    self.soundDataHolder.rewind = True
            else:
                data = np.zeros(frame_count * self.sampleWidth * self.channels)

            return data, pyaudio.paContinue

        self.soundStream = self.pyAudioObj.open(
            format=pyaudio.get_format_from_width(soundFile.getsampwidth()),
            channels=soundFile.getnchannels(),
            rate=soundFile.getframerate(),
            output=True,
            stream_callback=callback
        )

        self.soundStream.start_stream()

    def changeMusic(self, musicPath):
        self.soundStream.stop_stream()
        self.soundDataHolder.waveFile.close()

        self.__init__(musicPath)


class SoundUIHandler:
    def __init__(self, shader, musicPath, soundHandler, songFont, displayV, audioFiles):
        self.musicPath = musicPath
        self.soundHandler = soundHandler

        self.audioFiles = audioFiles

        self.oldSongPath = soundHandler.songPath
        self.songTitle = quadHandler.TextQuad(shader, basename(self.soundHandler.songPath), songFont, glm.vec2(0.01, 0.01), 0.05, displayV, (255, 255, 255, 255))
        self.songLength = quadHandler.TextQuad(shader, "0:00 / 0:00", songFont, glm.vec2(0.01, 0.0605), 0.05, displayV, (255, 255, 255, 255))

        self.shuffle = False
        self.songShuffle = quadHandler.TextQuad(shader, "Shuffle: OFF", songFont, glm.vec2(0.01, 0.111), 0.05, displayV, (255, 255, 255, 255))

        self.pause = False

    def update(self, frames):
        if self.oldSongPath != self.soundHandler.songPath:
            self.songTitle.changeText(basename(self.soundHandler.songPath))

        self.oldSongPath = self.soundHandler.songPath

        if frames % 15 == 0:
            duration = self.soundHandler.frames / self.soundHandler.frameRate
            currentTime = self.soundHandler.soundDataHolder.waveFile.tell() / self.soundHandler.frameRate

            self.songLength.changeText(f"{floor(currentTime//60)}:{floor(currentTime%60):0>2} / {floor(duration//60)}:{floor(duration%60):0>2}")

        #print(self.soundHandler.soundDataHolder.waveFile.)

    def shuffleToggle(self):
        self.shuffle = not self.shuffle
        self.songShuffle.changeText(f"Shuffle: {'ON' if self.shuffle else 'OFF'}")

    def nextSong(self):
        if self.shuffle:
            self.soundHandler.changeMusic(join(self.musicPath, choice(self.audioFiles)))

        else:
            self.audioFiles = self.audioFiles[1:] + [self.audioFiles[0]]
            self.soundHandler.changeMusic(join(self.musicPath, self.audioFiles[0]))

    def backSong(self):
        if self.shuffle:
            self.soundHandler.changeMusic(join(self.musicPath, choice(self.audioFiles)))

        else:
            self.audioFiles = [self.audioFiles[-1]] + self.audioFiles[:-1]
            self.soundHandler.changeMusic(join(self.musicPath, self.audioFiles[0]))

    def togglePause(self):
        self.soundHandler.soundDataHolder.pause = not self.soundHandler.soundDataHolder.pause

    def draw(self):
        self.songTitle.draw()
        self.songLength.draw()
        self.songShuffle.draw()
