from __future__ import division
import threading

import pyaudio
import numpy
from numpy.fft import rfft
from numpy import argmax, mean, diff, log, polyfit, arange
from matplotlib.mlab import find
from scipy.signal import fftconvolve
from time import time
from array import array
from sys import byteorder
import numpy as np
import peakutils
from math import log2, pow

import Constants

FORMAT = pyaudio.paInt16

#Mic
class mic(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.r = array('h')
        self.freq = 0.0
        self.record = False
        self.data = array('h')


    def run(self):
        
        p=pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels = 1, rate = Constants.RATE, input=True, output=True, frames_per_buffer = Constants.CHUNK_SIZE)


        while self.running:
            snd_data = array('h', stream.read(Constants.CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
                self.r.extend(snd_data)
            if voicing(snd_data):
                self.freq = 1/freq_from_autocorr(snd_data, snd_data)
            else:
                self.freq = 0.0

            #FOR TESTING ONLY
            ###############################################
            # if voicing(snd_data):
            #     print(self.freq)
            # else:
            #     self.freq = 0.0
            #     print(self.freq)
            # ###############################################
            #FOR TESTING ONLY


        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        #self.r = normalize(self.r)

    def record(self):
    #Record a single chunk from an audio stream for later processing
    
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=1, rate=Constants.RATE,
            input=True, output=True,
            frames_per_buffer=Constants.CHUNK_SIZE)

        snd_started = False

        while self.record:
            # little endian, signed short
            snd_data = array('h', stream.read(CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
            self.data.extend(snd_data)


        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def Off():
        self.b = False

    def get(time):
        return

#Voicing
def voicing(r):
	if np.mean(np.abs(r)) > 400 :
		return True
	else:
		return False

def maxFrequency(X, F_sample, Low_cutoff, High_cutoff):
        """ Searching presence of frequencies on a real signal using FFT
        Inputs
        =======
        X: 1-D numpy array, the real time domain audio signal (single channel time series)
        Low_cutoff: float, frequency components below this frequency will not pass the filter (physical frequency in unit of Hz)
        High_cutoff: float, frequency components above this frequency will not pass the filter (physical frequency in unit of Hz)
        F_sample: float, the sampling frequency of the signal (physical frequency in unit of Hz)
        """        

        M = len(X) # let M be the length of the time series
        Spectrum = rfft(X, n=M) 
        [Low_cutoff, High_cutoff, F_sample] = map(float, [Low_cutoff, High_cutoff, F_sample])

        #Convert cutoff frequencies into points on spectrum
        [Low_point, High_point] = map(lambda F: F/F_sample * M, [Low_cutoff, High_cutoff])

        maximumFrequency = np.where(Spectrum == np.max(Spectrum[Low_point : High_point])) # Calculating which frequency has max power.

        return maximumFrequency


#Pitch
def freqHz(data):

	w = np.fft.fft(data)
	freqs = np.fft.fftfreq(len(w))
	#print(freqs.min(), freqs.max())
	# (-0.5, 0.499975)

	# Find the peak in the coefficients
	idx = np.argmax(np.abs(w))
	freq = freqs[idx]
	freq_in_hertz = abs(freq * Constants.RATE)
	return freq_in_hertz
	# 439.8975

#Autocorrelate Pitch
def freq_from_autocorr(sig, fs):
    """
    Estimate frequency using autocorrelation
    """
    # Calculate autocorrelation (same thing as convolution, but with
    # one input reversed in time), and throw away the negative lags
    corr = fftconvolve(sig, sig[::-1], mode='full')
    corr = corr[len(corr)//2:]

    # Find the first low point
    d = diff(corr)
    start = find(d > 0)[0]

    # Find the next peak after the low point (other than 0 lag).  This bit is
    # not reliable for long signals, due to the desired peak occurring between
    # samples, and other peaks appearing higher.
    # Should use a weighting function to de-emphasize the peaks at longer lags.
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)

    return px / Constants.RATE

def freq_from_auto(signal, fs):
    # Calculate autocorrelation (same thing as convolution, but with one input
    # reversed in time), and throw away the negative lags
    signal -= np.mean(signal)  # Remove DC offset
    corr = fftconvolve(signal, signal[::-1], mode='full')
    corr = corr[len(corr)//2:]

    # Find the first peak on the left
    i_peak = peakutils.indexes(corr, thres=0.8, min_dist=5)#[0]
    i_interp = parabolic(corr, i_peak)#[0]

    return fs / i_interp #, corr, i_interp

def parabolic(f, x):
    """
    Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    f is a vector and x is an index for that vector.

    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.

    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.

    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]

    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)
    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)

def freq_from_fft(sig, fs):
    """
    Estimate frequency from peak of FFT
    """
    # Compute Fourier transform of windowed signal
    windowed = sig * blackmanharris(len(sig))
    f = rfft(windowed)

    # Find the peak and interpolate to get a more accurate peak
    i = argmax(abs(f))  # Just use this for less-accurate, naive version
    true_i = parabolic(log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return Constants.RATE * true_i / len(windowed)

def freq_from_crossings(sig, fs):
    """
    Estimate frequency by counting zero crossings
    """
    # Find all indices right before a rising-edge zero crossing
    indices = find((sig[1:] >= 0) & (sig[:-1] < 0))

    # Naive (Measures 1000.185 Hz for 1000 Hz, for instance)
    # crossings = indices

    # More accurate, using linear interpolation to find intersample
    # zero-crossings (Measures 1000.000129 Hz for 1000 Hz, for instance)
    crossings = [i - sig[i] / (sig[i+1] - sig[i]) for i in indices]

    # Some other interpolation based on neighboring points might be better.
    # Spline, cubic, whatever

    return Constants.RATE / mean(diff(crossings))

A4 = 440
C0 = A4*pow(2, -4.75)
name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
def note(freq):
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)


def notedev(f0, note):
    no = note[0]
    octave = note[1]
    #f0no

#y value for pitch point every 40ms
def pitchpoints(data, recf0):
    i = 0.0
    j = 0.04
    freqs = []
    while j < data.duration:
        seg = data.segment(i, j)
        
       
        if numpy.mean(abs(seg.ys)) > 0.004:
            fre = 1/freq_from_autocorr(seg.ys, seg.ys)
            if recf0*4 > fre > recf0/2:
                freqs.append(fre)
                print(fre)
            else:
                freqs.append(0)
                print(0)
        else:
            freqs.append(0)


        i += 0.04
        j += 0.04

    print(freqs)
    return freqs

#f0 value for all of recording voiced segments
def f0value(data):
    i = 0.0
    j = 0.05
    freqs = 1
    count = 1
    while j < data.duration:
        seg = data.segment(i, j)
       
        if numpy.mean(abs(seg.ys)) > 0.13 :
            fre = 1/freq_from_autocorr(seg.ys, seg.ys)
            freqs += fre
            count += 1
      
        i += 0.05
        j += 0.05
    r = freqs/count
    print(r)
    return r

#Musical Note 2
def note_no_oct(freq):
    A4 = 440
    C0 = A4*pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] #+ str(octave)

#Musical Semitone with octave
def semitone(freq):
    A4 = 440
    C0 = A4*pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    h = round(24*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)
    
#Weighted F0 Deviation No Array
def f0dev(freq, f0):
    n = freq - f0
    n = n/(f0/100)
    return n

def f0v(data):
    freqs = 1
    count = 1
    for x in data:

        freqs += x
        count += 1

    r = freqs/count
    return r

#Weighted F0 Deviation Array
def f0devA(freq, f0, r):
    n = freq - f0
    r.append(n/(f0/100))

def notepos(note):
    n = Constants.WIN_HEIGHT/20
    x = Constants.HALF_HEIGHT

    if note == "C":
        x = x - n*1
    elif note == "C#":
        x = x - n*1.5
    elif note == "D":
        x = x - n*2
    elif note == "D#":
        x = x - n*2.5
    elif note == "E":
        x = x - n*3
    elif note == "F":
        x = x - n*3.5
    elif note == "F#":
        x = x + n*2.5
    elif note == "G":
        x = x + n*2
    elif note == "G#":
        x = x + n*1.5
    elif note == "A":
        x = x + n*1
    elif note == "A#":
        x = x + n*0.5
    elif note == "B":
        x = Constants.HALF_HEIGHT

    return x