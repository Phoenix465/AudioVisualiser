import numpy as np


def gkernRightSide(filter_length=5, sigma=1.75):
    mid = filter_length / 2
    inverseSigmaSqrt2Pi = (1 / (sigma * np.sqrt(2 * np.pi)))
    doubleSigmaSquared = (2 * sigma ** 2)

    result = np.array([inverseSigmaSqrt2Pi * (1 / (np.exp((i ** 2) / doubleSigmaSquared))) for i in range(filter_length)], dtype=np.float32)
    result /= sum(result)

    return result


class BlurKernel:
    def __init__(self, pixelRange: int):
        self.pixelRange = pixelRange
        self.maxPixels = 26
        self.kernel = self.generateKernel()

    def updateKernel(self, newRange):
        self.pixelRange = max(min(newRange, self.maxPixels), 0)
        self.kernel = self.generateKernel()
        print(self.kernel)

    def generateKernel(self) -> np.ndarray:
        kernel = gkernRightSide(filter_length=self.pixelRange)
        return np.pad(kernel, (0, self.maxPixels-len(kernel))).astype(dtype=np.float32)


if __name__ == "__main__":
    import timeit

    print(timeit.timeit(gkernRightSide, number=100000)/100000)

    print(gkernRightSide())