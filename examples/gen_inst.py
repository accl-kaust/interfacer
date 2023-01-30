from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

def main():
    datawid = vast.Parameter( 'DATAWID', vast.Rvalue(vast.IntConst('32')) )
    params = vast.Paramlist( [datawid] )
    hmm = vast.Identifier('CLK')
    
    eh = vast.PortArg('clk',hmm)
    eh1 = vast.PortArg('rst',hmm)

    mod = vast.Instance(name="module_name",module=None, portlist=[eh,eh1], parameterlist=None)
    moder = vast.InstanceList(module='module',instances=[mod],parameterlist=[])
    
    codegen = ASTCodeGenerator()
    rslt = codegen.visit(moder)
    print(rslt)

if __name__ == '__main__':
    main()