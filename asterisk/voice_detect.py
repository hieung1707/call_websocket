#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from scipy.io import wavfile
from background_processing import detect_speech
from asterisk.agi import *
import sys
import websocket_api
import re


# path-related variables
PATH = "/home/hieung1707"
PREVOICE_DIR = 'python_code/voice_detection/prerecorded_voices'
FILE_NAME = 'sample.mp3'
# FILE_PATH = '{}/{}/{}'.format(PATH, PREVOICE_DIR, 'tongdai')

# audio-related constant
SAMPLE_RATE = 8000.0
CHUNK_TIME = 0.05
BYTES_PER_SAMPLE = 2
CHUNK = int(BYTES_PER_SAMPLE * SAMPLE_RATE * CHUNK_TIME)

# time-related variables
MIN_SPOKEN_TIME = 0.2
SILENT_TIME = 1.0
TIMEOUT = 7.0

FD = 3
windows = 0
loops = 0
data = np.array([])
has_spoken = False
hypothesis = ''


def rms(samples):  # Root-mean-square
    int64_samples = np.array(samples).astype(np.int64)
    return np.sqrt(np.mean(np.square(int64_samples)))


def record():
    global data, has_spoken
    # patience = 20
    # n_silence = 0
    # start_recording = True
    # --- new variables --- #
    cons_sil_time = 0.0
    cons_speech_time = 0.0
    total_time = 0.0
    # --------------------- #

    # --- old logic --- #
    # while start_recording:
    #     raw_samples = file_descriptor.read(CHUNK)
    #     new_samples = np.fromstring(raw_samples, dtype=np.int16)
    #     data = np.append(data, new_samples)
    #     v.data = data
    # ---------------- #

    # --- new logic --- #
    while cons_sil_time < SILENT_TIME:
        raw_samples = file_descriptor.read(CHUNK)
        new_samples = np.fromstring(raw_samples, dtype=np.int16)
        # new_samples = np.fromstring(raw_samples, dtype=np.int16)
        total_time += CHUNK_TIME
        spoke = detect_speech(new_samples)
        if spoke:
            cons_sil_time = 0.0
            cons_speech_time += CHUNK_TIME
            if cons_speech_time >= MIN_SPOKEN_TIME and not has_spoken:
                sys.stdout.write('VERBOSE \"{}\"\n'.format("has spoken"))
                has_spoken = True
                data = np.append(data[data.size - int(0.5*SAMPLE_RATE):] if data.size - 0.5*SAMPLE_RATE > 0 else data, new_samples)
        else:
            cons_speech_time = 0.0
            if has_spoken:
                cons_sil_time += CHUNK_TIME
        data = np.append(data, new_samples)
        # sys.stdout.write('VERBOSE \"{} {}\"\n'.format(cons_sil_time, total_time))
        # sys.stdout.flush()
        # has_spoken = True
        if total_time >= TIMEOUT:
            break
    # ---------------- #
    n_samples = len(data)
    if has_spoken:
        hypothesis = websocket_api.get_websocket_result(data.tobytes())
    padding = np.zeros(int(0.3 * SAMPLE_RATE),np.int16)
    data = np.append(padding, data)
    data = np.append(data, padding)
    n_secs = n_samples / SAMPLE_RATE
    save_record(data)


def save_record(data):
    data = data / 65535
    wavfile.write('{}/{}'.format(PATH, FILE_NAME), 8000, data)


if __name__ == "__main__":
    # agi = AGI()
    # caller_id = agi.get_variable("CALLERID(num)")
    FILE_PATH = ''
    if len(sys.argv) >= 2:
        FILE_PATH = sys.argv[1]
    if len(sys.argv) >= 3:
        TIMEOUT = sys.argv[2]
    if len(sys.argv) >= 4:
        SILENT_TIME = sys.argv[3]
    file_descriptor = open('/dev/fd/3', 'rb')
    if FILE_PATH != '':
        command = 'STREAM FILE {} \"{}\" {}\n'.format(FILE_PATH, 3, 0)
        sys.stdout.write(command)
        sys.stdout.flush()
    while True:
        record()
        sys.stdout.write("SET VARIABLE \"{}\" \"{}\"\n".format("has_spoken", 1 if has_spoken else 0))
        sys.stdout.flush()
        break
    sys.stdout.write("SET VARIABLE \"{}\" \"{}\"\n".format("hypothesis", hypothesis))
    sys.stdout.flush()
    exit()
