import h5py
from inspect import currentframe

def getFirstData(obj):
	def getOrder(name, obj):
		if isinstance(obj, h5py.Dataset):
			return obj
	return obj.visititems(getOrder)

def print_all(name, obj):
	if isinstance(obj, h5py.Dataset):
		print(obj.name, obj.shape, obj.dtype)
	else :
		print(obj.name)

def print_group(name, obj):
	if isinstance(obj, h5py.Dataset):
		pass
	else :
		print(obj.name)

def _line():
    cf = currentframe()
    return cf.f_back.f_lineno