#!/usr/bin/env python3
''' Script to generate sample waveforms for use on an Elektron Digitakt!
'''

import argparse
import errno
import math
import os
import pathlib
import struct
import wave

TWOPI = 2.0 * math.pi

NUM_CHANNELS = 1
FRAME_WIDTH_BYTES = 2  # i.e. 16 bits
FRAME_RATE_HZ = 48000


def generate_additive(file_name, num_frames, harmonic_amplitudes=None):
    if harmonic_amplitudes is None:
        harmonic_amplitudes = [1.0]

    # pre-allocate
    frames = [0.0] * num_frames

    step = TWOPI / num_frames

    # generate waveform
    for i in range(0, len(frames)):
        for n, harmonic_amplitude in enumerate(harmonic_amplitudes):
            frames[i] += harmonic_amplitude * math.sin(
                    (float(n) + 1.0) * float(i) * step)

    frames = _normalize(frames)

    _export_file(file_name, frames)


def generate_fm(
        file_name, num_frames,
        carrier_ratio=1, modulator_ratio=1, mod_index=1):

    # pre-allocate
    modulator_frames = [0.0] * num_frames
    carrier_frames = [0.0] * num_frames

    # generate modulator waveform
    modulator_step = TWOPI * (modulator_ratio + 1.0) / num_frames
    modulator_phase = 0.0
    for i in range(0, len(modulator_frames)):
        modulator_phase += modulator_step
        modulator_frames[i] = math.sin(modulator_phase)

    # generate carrier waveform
    carrier_phase = 0.0
    for i in range(0, len(carrier_frames)):
        carrier_step = (TWOPI * (carrier_ratio + 1.0)
                        * (1.0 + (modulator_frames[i] * mod_index))
                        / num_frames)
        carrier_phase += carrier_step
        carrier_frames[i] = math.sin(carrier_phase)

    carrier_frames = _normalize(carrier_frames)

    _export_file(file_name, carrier_frames)



def _normalize(frames):
    ''' Returns a new list of frames normalized to have a peak value of 1.0.
    '''
    max_value = max([abs(x) for x in frames])

    if max_value < 0.01:
        raise ValueError('Normalization would amplify signal over 100x!')

    normalized_frames = [x / max_value for x in frames]
    return normalized_frames


def _export_file(file_name, frames):
    try:
        os.mkdir('generated')
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir('generated'):
            pass
        else:
            raise

    file_path = str(pathlib.Path('generated') / file_name)

    with wave.open(file_path, 'w') as f:
        f.setnchannels(NUM_CHANNELS)
        f.setsampwidth(FRAME_WIDTH_BYTES)  # 2 bytes, i.e. 16 bits
        f.setframerate(FRAME_RATE_HZ)

        packed_data = struct.pack(
                f'<{len(frames)}h',
                *[int(32767*frame) for frame in frames])

        f.writeframes(packed_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-frames', type=int, default=4096)

    data = generate_fm(file_name='3.wav', num_frames=1024, mod_index=3)
