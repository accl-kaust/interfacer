import pytest

def test_vivado():
    import os
    import shutil
    # from edalize_common import compare_files, setup_backend, tests_dir

    # ref_dir      = os.path.join(tests_dir, __name__)
    # paramtypes   = ['generic', 'vlogdefine', 'vlogparam']
    # name         = 'test_vivado_0'
    # tool         = 'vivado'
    # tool_options = {
    #     'part' : 'xc7a35tcsg324-1',
    # }

    # (backend, work_root) = setup_backend(paramtypes, name, tool, tool_options)
    # backend.configure()

    # compare_files(ref_dir, work_root, [
    #     'Makefile',
    #     name+'.tcl',
    #     name+'_synth.tcl',
    #     name+'_run.tcl',
    #     name+'_pgm.tcl',
    # ])

    # backend.build()
    # compare_files(ref_dir, work_root, [
    #     'vivado.cmd',
    # ])
