import h5py
#import modules.util as util
from modules import util
import numpy as np

contextLeft = 12 # 현재 프레임 앞쪽으로 더 볼 Frame 개수
contextRigth = 12 # 현재 프레임 뒤쪽으로 더 볼 Frame 개수
contextLen = contextLeft + 1 + contextRigth
inputNodeLen = contextLen * 13 # mfcc를 기준으로 13차수



h5f = h5py.File('test.hdf5', 'r+')

if '/context' in h5f:
	del h5f['context']
if '/label' in h5f:
	del h5f['label']

classes    = list(h5f.keys())
firstData  = util.getFirstData(h5f)
inputNodeLen = contextLen * firstData.shape[1] # 
grpContext = h5f.create_group('context')

if '/data' in grpContext: del grpContext['data']
if '/lable' in grpContext: del grpContext['label']
nodeInput = grpContext.create_dataset('data',
			shape=(firstData.shape[0], inputNodeLen), # label을 넣어 주기 위하여+1
			maxshape=(None, inputNodeLen), compression="gzip",
			dtype='float32')
label     = grpContext.create_dataset('label',
			shape=(firstData.shape[0],), # label을 넣어 주기 위하여+1
			maxshape=(None,), compression="gzip",
			dtype='int32')
ctxRowId  = 0

for classid, key in enumerate(classes):
	grp = h5f[key]
	#tmplst = list(grp.keys())
	for dkey in grp.keys(): #tmplst[:1]:
		print(dkey, grp[dkey].shape, classid, ctxRowId)
		size = grp[dkey].shape[0]
		for idx in range(0, size-contextLen, contextLeft):
			arr = grp[dkey][idx:idx+contextLen]			
			nodeInput[ctxRowId] = arr.flatten()
			label[ctxRowId] = classid
			#print(nodeInput.shape[0], ctxRowId,
			#	classid, classes[classid], nodeInput[ctxRowId][-4:],
			#	util._line())
			ctxRowId += 1
			if nodeInput.shape[0] < ctxRowId+1: # append hdf memory
				nodeInput.resize(nodeInput.shape[0]*2, axis=0)
				label.resize(label.shape[0]*2, axis=0)

nodeInput.resize(ctxRowId-1, axis=0)
label.resize(ctxRowId-1, axis=0)

h5f.visititems(util.print_all)
print(h5f['context']['data'].shape)
print(h5f['context']['label'].shape)
h5f.close()