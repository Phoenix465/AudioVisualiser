from math import exp, pow, pi, sqrt


def generateKernel2D(size, sigma):
    kernel = [[0]*size]*size

    mean = size/2
    sum = 0

    for x in range(size):
        for y in range(size):
            kernel[x][y] = (
                    exp(-0.5 * (
                            pow(
                                (x-mean) / sigma, 2
                            ) + pow(
                                (y-mean) / sigma, 2
                            ))) / (2 * pi * sigma * sigma))
            sum += kernel[x][y]

    for x in range(size):
        for y in range(size):
            kernel[x][y] /= sum

    print(kernel)
    return kernel


def getTwoPassKernel(size, sigma):
    kernel = [0] * size
    fkernel = generateKernel2D(size, sigma)

    for i in range(size):
        kernel[i] = sqrt(fkernel[i][i])

    return kernel


if __name__ == "__main__":
    print("Kernel:", getTwoPassKernel(10, 1.75))