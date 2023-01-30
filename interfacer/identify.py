import sys
import os
from pathlib import Path
from optparse import OptionParser
import json
import pyverilog.dataflow.dataflow_analyzer as da
from pyverilog.vparser.parser import VerilogCodeParser
from pyverilog.dataflow.modulevisitor import ModuleVisitor
from pyverilog.dataflow.signalvisitor import SignalVisitor
from pyverilog.dataflow.bindvisitor import BindVisitor
import pyverilog.utils.op2mark as op2mark
from .utils.tool import Tool, Log


class preprocess(da.VerilogDataflowAnalyzer, VerilogCodeParser):
    def __init__(self, filelist, topmodule='TOP', noreorder=False, nobind=False, preprocess_include=None, preprocess_define=None, preprocess_ignoremodules=True):
        self.topmodule = topmodule
        self.terms = {}
        self.binddict = {}
        self.frametable = None
        files = filelist if isinstance(filelist, tuple) or isinstance(
            filelist, list) else [filelist]
        VerilogCodeParser.__init__(self, files,
                                   preprocess_include=preprocess_include,
                                   preprocess_define=preprocess_define)
        self.noreorder = noreorder
        self.nobind = nobind

    def generate(self):
        ast = self.parse()

        module_visitor = ModuleVisitor()
        module_visitor.visit(ast)
        modulenames = module_visitor.get_modulenames()
        moduleinfotable = module_visitor.get_moduleinfotable()

        signal_visitor = SignalVisitor(moduleinfotable, self.topmodule)
        signal_visitor.start_visit()
        frametable = signal_visitor.getFrameTable()

        if self.nobind:
            self.frametable = frametable
            return

        bind_visitor = BindVisitor(moduleinfotable, self.topmodule, frametable,
                                   noreorder=self.noreorder)

        bind_visitor.start_visit()
        dataflow = bind_visitor.getDataflows()

        self.frametable = bind_visitor.getFrameTable()
        self.terms = dataflow.getTerms()
        self.binddict = dataflow.getBinddict()

    def getFrameTable(self):
        return self.frametable

    def getInstances(self):
        if self.frametable is None:
            return ()
        return self.frametable.getAllInstances()

    def getSignals(self):
        if self.frametable is None:
            return ()
        return self.frametable.getAllSignals()

    def getConsts(self):
        if self.frametable is None:
            return ()
        return self.frametable.getAllConsts()

    def getTerms(self):
        return self.terms

    def getBinddict(self):
        return self.binddict


class Identify(Tool):
    def __init__(self):
        self.log = Log(self.__class__.__name__, enable=True, testing=True)
        self.version = "0.0.1"
        self.top = None
        self.filelist = []

    def __inSet(self, direction):
        if 'Input' in direction:
            return('input')
        if 'Output' in direction:
            return('output')

    def __convert(self, s):
        new = "("
        for x in s:
            new += str(x)
        new += ")"
        return new

    def __dive(self, node, path, params):
        if hasattr(node, 'nextnodes'):
            temp = []
            for i, each in enumerate(node.nextnodes):
                if hasattr(node, 'operator') & i == 1:
                    temp.append(op2mark.op2mark(node.operator))
                self.__dive(each, temp, params)
            path.append(self.__convert(temp))
        else:
            if hasattr(node, 'name'):
                # print(node.name)
                if node.name in params:
                    path.append(params[node.name])
            if hasattr(node, 'value'):
                path.append(int(node.value))

    def __evaluate(self, value, params):
        try:
            return int(eval(value))
        except:
            try:
                return int(value.value)
            except:
                try:
                    return int(value)
                except:
                    self.log.logger.error(
                        f'Invalid value: {value} - {params}.')

    def load(self, obj):
        from interfacer.module import Module as mod
        if isinstance(obj, mod):
            self.top = obj.name
            self.filelist = obj.files
            self.directory = obj.directory
            # self.blackboxes = obj.blackboxes
        else:
            raise ValueError('Not a valid object')

        for f in self.filelist:
            # print(f'file - {Path(f)}')
            if not Path(f"{f}").exists():
                raise IOError("file not found: " + f)
        self.log.logger.info(f'top module - {self.top}')
        self.log.logger.info(f'File List - {[str(i) for i in self.filelist]}')
        analyzer = preprocess([str(i) for i in self.filelist], self.top,
                              noreorder=False,
                              nobind=False,
                              preprocess_include=[],
                              preprocess_define=[],
                              preprocess_ignoremodules=True)
        analyzer.generate()
        module_dict = {}
        module_dict['name'] = self.top
        module_dict['ports'] = {}

        instances = analyzer.getInstances()
        terms = analyzer.getTerms()
        params = {}
        for tk, tv in terms.items():
            scope = tv.getScope(tv.name)
            # Reject non-topmodule params
            if ('Parameter' in tv.termtype) & tv.isTopmodule(scope):
                params[tv.name] = None
        binddict = analyzer.getBinddict()
        for bk, bv in binddict.items():
            for bvi in bv:
                if bvi.dest in params:
                    params[bvi.dest] = bvi.tree
        for tk, tv in terms.items():
            scope = tv.getScope(tv.name)
            # print('blackbox: ',self.blackboxes, ' scope: ',scope)
            if ('Input' in tv.termtype or 'Output' in tv.termtype) & (str(scope) in self.top):
                path = []
                self.__dive(tv.msb, path, params)
                msb = self.__evaluate(path[0], params)
                path = []
                self.__dive(tv.lsb, path, params)
                lsb = self.__evaluate(path[0], params)
                name = str(tv.name).split('.')[-1]
                direction = self.__inSet(tv.termtype)
                port = {
                    'msb': msb,
                    'lsb': lsb,
                    'direction': direction
                }
                # print('port',port)
                module_dict['ports'][name] = port
        return (module_dict)


# if __name__ == '__main__':
#     obj = mod.Module(top="blinky_zybo_z7", files=[
#         "../examples/rtl/top.v", "../examples/rtl/blink.v"], blackboxes=['blinky_zybo_z7'])

#     obj.add_mode('mode_a', ["../examples/rtl/top_0.v",
#                             "../examples/rtl/blink.v"], "../examples/rtl/zybo.xdc")
#     obj.add_mode('mode_b', ["../examples/rtl/top_1.v",
#                             "../examples/rtl/blink.v"], "../examples/rtl/zybo.xdc")

#     obj.list_modes()

#     # print(dir(obj))

#     iden = Identify()
#     iden.load(obj)

#     gen = gen.Generate()
#     gen.load(obj)
#     # gen.wrapper(xilinx_pragmas=False)
#     gen.blackbox()
#     gen.write("../examples/out")
