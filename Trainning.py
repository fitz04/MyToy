import numpy as np
import h5py
import modules.util as util
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.utils import np_utils

h5f = h5py.File('feat.hdf5', 'r')

h5f['context'].visititems(util.print_all)
classNum = len(h5f.keys())-1
X_train = np.asarray(h5f['context']['data']) #.astype('float32')
Y_train = np_utils.to_categorical(h5f['context']['label'])
#X_train = data.astype('float32')
#lbls = data[:,-1].astype('int32')
#Y_train = np_utils.to_categorical(lbls)
#print(X_train.shape)
#print(Y_train)

inputDim = X_train.shape[1]
print (inputDim, X_train.shape)

model = Sequential()
model.add(Dense(128, input_dim=inputDim, init='uniform'))
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
model.add(Dense(classNum, init='uniform'))
model.add(Activation('softmax'))

sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mean_squared_error', optimizer=sgd)
model.fit(X_train, Y_train, batch_size=50, nb_epoch=50)
score = model.evaluate(X_train, Y_train, batch_size=50, show_accuracy=True)
print(score)

json_string = model.to_json()
open('myfirst_model.json', 'w').write(json_string)
model.save_weights('myfirst_model.h5')
h5f.close()