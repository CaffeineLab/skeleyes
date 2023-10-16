# Read the wav file and generate the eye flicker pattern.  Kind of kludgey but works
# well enough for a first pass at this.
from pathlib import Path
import argparse
import json
import wave
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')


def intervalize(time, signal, interval=0.1):

    points = len(time)
    base = 0

    time_new = [0]
    signal_new = [0]
    t = 1

    while t <= points:
        signals = []
        try:
            while time[t] < base + interval:
                signals.append(signal[t])
                t += 1

            base = base + interval
            if len(signals) > 0:
                signal_new.append(int(sum(signals)/len(signals)))
            else:
                signal_new.append(0)
            time_new.append(round(base, 1))
        except:
            print('done')
            t = points + 100
    time_new.append(round(base + interval, 0))
    signal_new.append(0)
    return time_new, signal_new


def dedupe(time, signal):
    points = len(time)

    time_new = []
    signal_new = []
    for t in range(1, points):
        if signal[t] > 25:
            time_new.append(time[t])
            signal_new.append(signal[t])

    return time_new, signal_new


def write_peaks(fn, show_chart=False):
    # reading the audio file
    raw = wave.open(fn)

    # reads all the frames
    # -1 indicates all or max frames
    signal = raw.readframes(-1)
    signal = np.frombuffer(signal, dtype="int16")
    signal = abs(signal)
    signal = signal / np.max(signal)
    signal = signal * 100
    signal = np.round(signal, 0)
    signal = 100 - signal

    # gets the frame rate
    f_rate = raw.getframerate()

    # to Plot the x-axis in seconds
    # you need get the frame rate
    # and divide by size of your signal
    # to create a Time Vector
    # spaced linearly with the size
    # of the audio file
    time = np.linspace(
        0,  # start
        raw.getnframes() / raw.getframerate(),
        num=len(signal)
    )

    time, signal = dedupe(time.tolist(), signal.tolist())
    time, signal = intervalize(time, signal)

    s = json.dumps(dict(zip(time, signal)))
    with open('out.json', 'w', encoding='utf-8') as f:
        f.write(s)

    # using matplotlib to plot
    # creates a new figure
    plt.figure(1)

    # title of the plot
    plt.title("Sound Wave")

    # label of x-axis
    plt.xlabel("Time")

    # actual plotting
    plt.plot(time, signal)
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", action="store", dest="filename", default=None)
    parser.add_argument("-o", "--outfile", action="store", dest="outfile", default=None)
    args = parser.parse_args()


    write_peaks(args.filename)
