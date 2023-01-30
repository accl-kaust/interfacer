
from interfacer.generate import Generate
from interfacer.identify import Identify
from interfacer.module import Module, Static
from interfacer.interface import Interface
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
iden = Identify()


# Static layer for interfacing with external peripherals
static = Static(top="static",directory='rtl',files=["static.v"], xdc="zybo.xdc", version='2018.3', base=False)

# Module of a mode; can be swapped in/out of a mode
obj_1 = Module(top="fft",directory='rtl',files=["top.v","blink.v"],ipcores=['test.xci'], version='2018.3', force=False)
json_1 = iden.load(obj_1)
obj_1.update(json_1)
obj_2 = Module(top="top_v1",directory='rtl',files=["top_1.v","blink.v"],ipcores=['test.xci'], version='2018.3', force=False)
json_2 = iden.load(obj_2)
obj_2.update(json_2)


i = Interface()
i.verifyInterface(obj_1.ports)
for each in i.matched_interfaces:
    print(each)

# Should accept all of the modules including static top
gen = Generate(static=static,modules=[obj_1,obj_2],prr=2,part='xc7z020-clg400')
gen.implement()
# gen.load(obj_1)
# print(obj_1.ports)
gen.wrapper(obj_1, xilinx_pragmas=True)
# gen.blackbox_inst(obj_1,0)
gen.render("rtl/.inst/")
# outfile = gen.write(obj_1,"rtl/.inst/test")
# print(outfile)


# obj.add_mode('mode_a',["rtl/top_0.v","rtl/blink.v"],"rtl/zybo.xdc")
# obj.add_mode('mode_b',["rtl/top_1.v","rtl/blink.v"],"rtl/zybo.xdc")