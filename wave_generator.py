#!/usr/bin/env python3
''' Script to generate sample waveforms for use on an Elektron Digitakt!
'''

import argparse
import math
import struct
import wave

TWOPI = 2.0 * math.pi


def generate_wave(sample_length, harmonic_amplitudes=None):
    if harmonic_amplitudes is None:
        harmonic_amplitudes = [1.0]

    step = TWOPI / sample_length

    # pre-allocate
    result = [0.0] * sample_length

    # generate waveform
    for i in range(0, len(result)):
        for n, harmonic_amplitude in enumerate(harmonic_amplitudes):
            result[i] += harmonic_amplitude * math.sin((n + 1) * i * step)

    # normalize
    max_value = max([abs(x) for x in result])
    for i in range(0, len(result)):
        result[i] /= max_value

    return result


def export_file(file_name, sample_data):
    with wave.open(file_name, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)  # 2 bytes, i.e. 16 bits
        f.setframerate(48000)

        packed_data = struct.pack(
                f'<{len(sample_data)}h',
                *[int(32767*sample) for sample in sample_data])

        f.writeframes(packed_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sample_length', type=int, default=4096)

    data = generate_wave(1024)
    export_file('1.wav', data)

    data = generate_wave(1024, [1.0, 0.5, 0.25, 0.125])
    export_file('2.wav', data)
