import numpy as np


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
