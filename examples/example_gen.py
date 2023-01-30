
from interfacer.generate import Generate
from interfacer.identify import Identify
from interfacer.module import Module
from interfacer.interface import Interface
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))






obj = Module(top="blinky_zybo_z7",files=["rtl/top.v","rtl/blink.v"], blackboxes=['blinky_zybo_z7'])

obj.add_mode('mode_a',["rtl/top_0.v","rtl/blink.v"],"rtl/zybo.xdc")
obj.add_mode('mode_b',["rtl/top_1.v","rtl/blink.v"],"rtl/zybo.xdc")

iden = Identify()
iden.load(obj)

print(obj.ports)

i = Interface()
i.verifyInterface(obj.ports)
for each in i.matched_interfaces:
    print(each)
# print(i.protocol_classification)

gen = Generate()
# print(obj.ports)
gen.load(obj)
gen.wrapper(xilinx_pragmas=True)
gen.blackbox()
outfile = gen.write("out")
print(outfile)