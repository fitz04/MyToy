import matplotlib.pylab as plt
import numpy as np

def hamm(winlen):
	win = []
	for i in range(winlen):
		b = 0.54 - 0.46 * np.cos( (2*np.pi*i)/(winlen-1) ) # b = 24.7 * (1 + 4.37 * i/160)
		win.append(b)
	return win

def tribank(start, center, end):
	win = []
	leftbank = center - start
	RigthBank = end - center
	for i in range(leftbank):
		win.append(i/leftbank)

	for i in range(RigthBank):
		win.append(1 - i/RigthBank)
	return win


melscale = lambda f: 2595 * np.log10(1+ (f/700) )
melinv = lambda m: 700 * ( 10 ** (m/2595) - 1)

centerFreq = []
maxMel = melscale(16000)
step = (maxMel/15)
for m in range(0,int(maxMel),int(step)):
	f = melinv(m)
	centerFreq.append(int(f))
	print("mel = %8d, freq = %8d"%(m, int(f)))
idx = 0
for startq, centq, endq in zip(centerFreq[:-2], centerFreq[1:-1], centerFreq[2:]):
	idx += 1
	print (idx, startq, centq, endq)
	winlen = endq - startq
	print ( len(tribank(startq, centq, endq)), endq - startq )
	plt.plot([x for x in range(startq, endq)], tribank(startq, centq, endq))	
plt.show()
# 메세지 = "abcd"
# print(메세지)


# xidx = range(256)

# banknum = 0
# for fc in range(0, 256, 8):
# 	fl = fc-8
# 	fh = fc+8
# 	if  (fl > 0) and (fh < 256):
# 		banknum +=1
# 		plt.plot([x for x in range(fl, fh)], hamm(16))
# plt.show()
# print(banknum)