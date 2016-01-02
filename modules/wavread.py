import scipy.io.wavfile as wavfile
import numpy as np
from numpy.fft import rfft
class wavread(object):
	def __init__ (self, filename, chunkSize = 30, slidingSize = 10):
		self.fs, self.data = wavfile.read(filename)
		self.size = self.data.shape[0]
		self.channel = len(self.data.shape)
		self.offset = 0
		self.chunk = self.fs * chunkSize * 0.001
		self.sliding = self.fs * slidingSize * 0.001

	def getPSD(self):
		if (self.offset + self.chunk > self.data.size):
			print('end of file')
			return False
		spectrum = rfft(self.data[self.offset : self.offset + self.chunk], n = 512)
		self.offset += self.sliding
		return (np.abs(spectrum[:256])**2)/256

	def getBandEn(self, bankNum = 30):
		bankId = np.linspace(0, 256, bankNum + 1, dtype=np.int)
		bankEn = []		
		for idx in range(bankNum):
			psd = self.getPSD()
			if psd == False : return False
			en = np.sum(psd[bankId[idx] : bankId[idx+1]])/256
			bankEn.append(en)
		return bankEn





#rate, data = wavfile.read('b.wav')
#print(rate, len(data.shape))