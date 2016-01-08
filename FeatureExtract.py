from modules.base import mfcc
from modules.base import logfbank
import scipy.io.wavfile as wav
import numpy as np
import h5py, os, glob

h5f = h5py.File('feat.hdf5', 'w')

wavroot = 'F:/ken/Data/SpekerIdDB/NoiseMixedData/class14/Class_14_clean_wav'
subdirs = [x for x in os.listdir(wavroot) if os.path.isdir(os.path.join(wavroot, x))]

for spkid in subdirs:
    wavlist = glob.glob(os.path.join(wavroot, spkid) + '/*.wav')
    print (len(wavlist))
    if spkid not in h5f:
        grp = h5f.create_group(spkid)
        for fn in wavlist:
            print('Extract [%s:%s]'%(spkid, os.path.split(fn)[1]))
            (rate,sig) = wav.read(fn)
            mfcc_feat = mfcc(sig,rate)
            grp.create_dataset(os.path.basename(fn), data=mfcc_feat)

h5f.close()



#(rate,sig) = wav.read("a.wav")
#mfcc_feat = mfcc(sig,rate)
#fbank_feat = logfbank(sig,rate)

#h5f.create_dataset('mfcc', data=mfcc_feat)
#h5f.create_dataset('fbank', data=fbank_feat)

#h5f.close()

#h5fr = h5py.File('feat.hdf5', 'r')
#print (h5fr['mfcc'])
#print (h5fr['fbank'])
#h5fr.close()
