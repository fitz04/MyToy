import numpy as np
import h5py
import modules.util as util
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
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
		for idx in range(0,self.dataNum-50, 50):
			x = np.asarray((h5f['context/data'][idx:idx+50][:]))
			y = np_utils.to_categorical(h5f['context/label'][idx:idx+50], nb_classes=self.classNum)
			yield x, y
		h5f.close()
dataGenerator = DataProc('feat.hdf5')
print(dataGenerator.dataNum, dataGenerator.lblNum, dataGenerator.classNum, dataGenerator.inputDim)

model = Sequential()
model.add(Dense(128, input_dim=dataGenerator.inputDim, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(128, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(64, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(64, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(dataGenerator.classNum, init='uniform'))
model.add(Activation('softmax'))

sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mean_squared_error', optimizer=sgd)
# model.fit(X_train, Y_train, batch_size=100, nb_epoch=5)
model.fit_generator(dataGenerator.data_iterator(), samples_per_epoch=dataGenerator.dataNum, nb_epoch=20)
# score = model.evaluate(X_train, Y_train, batch_size=50, show_accuracy=True)
# print(score)

json_string = model.to_json()
open('myfirst_model.json', 'w').write(json_string)
model.save_weights('myfirst_model.h5')
