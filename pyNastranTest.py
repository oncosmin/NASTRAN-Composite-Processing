import pyNastran
from pyNastran.bdf.bdf import BDF

bdf_filename = 'inOrbit.bdf'

model = BDF()
model.read_bdf(bdf_filename)

print(model.coords.items())
