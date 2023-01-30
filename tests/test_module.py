import os
import sys
from interfacer.module import Module
import pytest

codedir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))) + '/verilogcode/'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


expected = {'mode_a': {'files': ['rtl/led_mode_a.v', 'rtl/blink.v'], 'xdc': ['rtl/zybo.xdc'], 'ipcores': [
    None]}, 'mode_b': {'files': ['rtl/led_mode_b.v', 'rtl/blink.v'], 'xdc': ['rtl/zybo.xdc'], 'ipcores': [None]}}


@pytest.mark.skip(reason="Needs fixing...")
def test():
    obj = Module(top="blinky_zybo_z7", files=[
                 "rtl/top.v", "rtl/blink.v"], version='2018.3')

    obj.add_mode('mode_a', ["rtl/led_mode_a.v", "rtl/blink.v"], "rtl/zybo.xdc")
    obj.add_mode('mode_b', ["rtl/led_mode_b.v", "rtl/blink.v"], "rtl/zybo.xdc")

    obj.list_modes()
    rslt = obj.list_modes()

    print(rslt)
    assert(expected == rslt)


if __name__ == '__main__':
    test()
