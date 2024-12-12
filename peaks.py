# Read the wav file and generate the eye flicker pattern.
# Kind of kludgey but works well enough to generate required files.
from pathlib import Path
import argparse
import json
import sys
import wave
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
SIGNAL_THRESHOLD = 25
APP_PATH = Path(__file__).parent.resolve()


def intervalize(time, signal, interval=0.1):
    """Generate the two series, one for the interval start time,
     and another for the signal strength for that interval."""

    t = 1
    base = 0
    points = len(time)
    time_new = [0]
    signal_new = [0]

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
            break

    time_new.append(round(base + interval, 0))
    signal_new.append(0)
    return time_new, signal_new


def dedupe(time, signal):
    """Don't bother changing intensity of LEDs if we don't have to,
    just leave the lights on at the specified brightness for the period."""
    time_new = []
    signal_new = []
    for t in range(1, len(time)):
        if signal[t] > SIGNAL_THRESHOLD:
            time_new.append(time[t])
            signal_new.append(signal[t])
    return time_new, signal_new


def write_peaks(args):
    """Open a .wav audio file, determine the waveform, and write a file
    that supplies time and brightness level for the LEDs of the display."""

    fn = Path(args.filename)
    raw = wave.open(str(fn.absolute()))

    # -1 indicates all or max frames
    signal = raw.readframes(-1)
    signal = np.frombuffer(signal, dtype="int16")
    signal = abs(signal)
    signal = signal / np.max(signal)
    signal = signal * 100
    signal = np.round(signal, 0)
    signal = 100 - signal

    # gets the frame rate
    # f_rate = raw.getframerate()

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

    # Get rid of timestamps that don't change intensity of lights
    # Also sets the minium intensity.
    time, signal = dedupe(time.tolist(), signal.tolist())

    # Convert timeseries to intervals
    time, signal = intervalize(time, signal)

    s = json.dumps(dict(zip(time, signal)))

    with open(args.filename.parent / fn.name.replace('.wav', '.json'), 'w', encoding='utf-8') as f:
        f.write(s)

    if args.show_chart:

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

    parser.add_argument("filename",
                        help="relative path to .WAV file")

    parser.add_argument("-v",
                        "--visualize",
                        action="count",
                        dest="show_chart",
                        default=0)

    pargs = parser.parse_args()
    pargs.filename = APP_PATH / pargs.filename
    if pargs.filename.exists() is False:
        sys.exit('Input file not found')
    write_peaks(pargs)
