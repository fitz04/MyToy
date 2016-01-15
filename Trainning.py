import numpy as np
import h5py
import modules.util as util
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.normalization import BatchNormalization
from keras.optimizers import SGD
from keras.utils import np_utils


class DataProc(object):
	def __init__(self, filename):
		self.filename = filename
		h5f = h5py.File(self.filename, 'r')
		self.classNum = len(h5f.keys())-1
		self.dataNum = h5f['context/data'].shape[0]
		self.inputDim = h5f['context/data'].shape[1]
		self.lblNum = h5f['context/label'].shape[0]
		print(self.dataNum, self.lblNum, self.classNum)
		h5f.close()


	def data_iterator(self):
		h5f = h5py.File(self.filename, 'r')
		suffledIdx = np.arange(self.dataNum)
		np.random.shuffle(suffledIdx)
		print(suffledIdx[:5])
		for idx in range(0,self.dataNum-50, 50):
			x = np.zeros((50, self.inputDim))
			y = np.zeros((50))
			for i, rowid in enumerate(suffledIdx[idx:idx+50]):
				x[i,:] = (h5f['context/data'][rowid][:])
				y[i] = h5f['context/label'][rowid]
			y = np_utils.to_categorical(y, nb_classes=self.classNum)
			# print(x.shape, y.shape)
			yield x, y
		h5f.close()
datIter = DataProc('feat.hdf5')
print(datIter.dataNum, datIter.lblNum, datIter.classNum, datIter.inputDim)

model = Sequential()
model.add(Dense(128, input_dim=datIter.inputDim, init='uniform'))
model.add(Activation('relu'))

model.add(Dense(128, init='uniform'))
model.add(BatchNormalization(128))
model.add(Activation('relu'))

model.add(Dense(128, init='uniform'))
model.add(BatchNormalization(128))
model.add(Activation('relu'))

model.add(Dense(64, init='uniform'))
model.add(BatchNormalization(64))
model.add(Activation('relu'))

model.add(Dense(64, init='uniform'))
model.add(BatchNormalization(64))
model.add(Activation('relu'))

model.add(Dense(64, init='uniform'))
model.add(BatchNormalization(64))
model.add(Activation('relu'))
# model.add(Dropout(0.8))

model.add(Dense(datIter.classNum, init='uniform'))
model.add(BatchNormalization(datIter.classNum))
model.add(Activation('softmax'))

sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mean_squared_error', optimizer=sgd)

model.fit_generator(datIter.data_iterator(), samples_per_epoch=datIter.dataNum, nb_epoch=20)
# score = model.evaluate(X_train, Y_train, batch_size=50, show_accuracy=True)
# print(score)

json_string = model.to_json()
open('dio14classModel.json', 'w').write(json_string)
model.save_weights('dio14classModel.h5')
