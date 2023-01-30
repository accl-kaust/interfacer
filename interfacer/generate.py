import sys
import os
import datetime
import json as j
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from .utils.tool import Tool, Log
from pathlib import Path
from jinja2 import Environment, PackageLoader, Template
import interfacer.module as m

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class XilinxPragmaInput(vast.Value):
    attr_names = ("name", "signed")

    def __init__(self, name, width=None, signed=False, dimensions=None, lineno=0):
        self.lineno = lineno
        self.name = name
        self.width = width
        self.signed = signed
        self.dimensions = dimensions


class XilinxPragmaOutput(vast.Value):
    attr_names = ("name", "signed")

    def __init__(self, name, width=None, signed=False, dimensions=None, lineno=0):
        self.lineno = lineno
        self.name = name
        self.width = width
        self.signed = signed
        self.dimensions = dimensions


class Generate(Tool):

    def __init__(
        self,
        modules: list,
        config_defaults={},
        static=None,
        prr={},
        part="xc7z020-clg400",
    ):

        self.log = Log(self.__class__.__name__, enable=True, testing=True)
        self.modules = modules
        self.module = {}
        [self.load(m) for m in modules]
        self.prr = prr
        self.port_list = {}
        self.checkpoints = []
        self.wrapper_file = None
        self.blackbox_file = None
        self.config_defaults = config_defaults
        self.static = static
        self.blackbox_insts = []
        self.blackbox_modules = []
        self.part = part
        # self.obj = None
        self.jinja_env = Environment(
            loader=PackageLoader(__package__, "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def __renderTemplate(self, template_file, target_file, template_vars={}):
        template = self.jinja_env.get_template(template_file)
        with open(target_file, "w") as f:
            f.write(template.render(template_vars))

    def load(self, obj):
        if isinstance(obj, m.Module):
            # self.obj = obj
            self.module[obj.name] = {}
            self.module[obj.name]["name"] = obj.name
            self.module[obj.name]["ports"] = obj.ports
            self.module[obj.name]["files"] = obj.files
            try:
                self.module[obj.name]["vhdl"] = obj.vhdl
            except:
                pass

            try:
                self.module[obj.name]["tcl"] = obj.tcl
                print(self.module[obj.name]["tcl"])
                exit()
            except:
                pass

            # print(f"{obj.name} - {self.module[obj.name]['files']}")
            if hasattr(obj, "ipcores"):
                self.module[obj.name]["ip"] = obj.ipcores
            self.log.logger.info(f"loaded {obj.name}")
            # print("ports: ",obj.ports)
        else:
            self.log.logger.error("Not a valid object")
            raise ValueError("Not a valid object")

    def synth(self, parameter_list) -> bool:
        """
        Run synthesise to generate checkpoints
        """
        pass

    def write(self, module, output_file, tcl=True):
        template_vars = {
            "module": module.name,
            "file": None,
            "date": datetime.datetime.now().strftime("%H:%M %d/%m/%Y"),
            "type": None,
            "content": {},
        }

        generated_files = []

        template_vars["file"] = output_file + "blackbox.v"
        template_vars["content"] = self.blackbox_file
        if self.blackbox_file != None:
            template_vars["type"] = "blackbox"
            self.log.logger.info("Generating {}".format(
                output_file + "blackbox.v"))
            self.__renderTemplate(
                "base.j2", output_file + "blackbox.v", template_vars)
            generated_files.append(output_file + "blackbox.v")
        else:
            self.log.logger.error("Missing module blackbox")
            raise ValueError("Missing module blackbox")

        template_vars["file"] = output_file + "wrapper.v"
        template_vars["content"] = self.wrapper_file
        if self.wrapper_file != None:
            template_vars["type"] = "wrapper"
            self.log.logger.info(
                "Generating {}".format(output_file + "wrapper.v"))
            self.__renderTemplate(
                "base.j2", output_file + "wrapper.v", template_vars)
            generated_files.append(output_file + "wrapper.v")

        if self.part != None:
            template_vars["file"] = output_file + "generate.tcl"
            template_vars["content"] = {
                "part": self.part,
                "file": self.obj.files,
                "top": module["name"],
                "modes": self.obj.modes,
            }
            self.log.logger.info("Generating {}".format(
                output_file + "generate.tcl"))
            self.__renderTemplate(
                "generate.tcl.j2", output_file + "generate.tcl", template_vars
            )
            generated_files.append(output_file + "generate.tcl")

        return generated_files

    def render(self, output_file, build_dir, prr={}, tcl=True):
        template_vars = {
            "module": "zycap",
            "file": None,
            "date": datetime.datetime.now().strftime("%H:%M %d/%m/%Y"),
            "type": "tcl",
            "content": {},
            "build_dir": build_dir,
        }

        generated_files = []

        # Remove any skippable modules
        for module, properties in self.module.items():
            print(properties)
            print(module)
            stop = 0
            for i in range(len(properties["files"])):
                if Path(properties["files"][i - stop]).stem in ["ignore"]:
                    print(self.module[module].keys())
                    print(f'Popped! {self.module[module]["files"][i]}')
                    self.module[module]["files"].pop(i)
                    stop += 1

        # Modules
        template_vars["file"] = "gen_modules.tcl"
        template_vars["content"] = {
            "part": self.part,
            "file": f"{output_file}gen_modules.tcl",
            "modules": self.module,
            "configs": self.config_defaults,
            "output": output_file,
        }
        self.log.logger.info("Generating {}".format(
            f"{output_file}gen_modules.tcl"))
        self.__renderTemplate(
            "gen_modules.tcl.j2", f"{output_file}gen_modules.tcl", template_vars
        )
        generated_files.append(output_file + "generate.tcl")
        # for each in self.module:
        #     self.checkpoints.append(f"{self.module[each]['name']}_{prr}.dcp")

        # Blackboxes
        for pr in range(0, len(self.prr)):
            template_vars["file"] = f"{output_file}blackbox_{pr}.v"
            template_vars["content"] = self.blackbox_modules[pr]
            if self.blackbox_modules != []:
                template_vars["type"] = "blackbox"
                self.log.logger.info(
                    "Generating {}".format(f"{output_file}blackbox_{pr}.v")
                )
                self.__renderTemplate(
                    "black_box.j2", f"{output_file}blackbox_{pr}.v", template_vars
                )
                generated_files.append(f"{output_file}blackbox_{pr}.v")
            else:
                self.log.logger.error("Missing module blackbox")
                raise ValueError("Missing module blackbox")

        # Wrapper
        template_vars["file"] = output_file + "wrapper.v"
        template_vars["content"] = self.wrapper_file
        if self.wrapper_file != None:
            template_vars["type"] = "wrapper"
            self.log.logger.info(
                "Generating {}".format(output_file + "wrapper.v"))
            self.__renderTemplate(
                "base.j2", output_file + "wrapper.v", template_vars)
            generated_files.append(output_file + "wrapper.v")

        # TCL Script
        # if self.part != None:
        # 	template_vars['file'] = output_file+"_generate.tcl"
        # 	template_vars['content'] = {
        # 		'part' : self.part,
        # 		'file' : self.obj.files,
        # 		'top'  : self.static,
        # 		'modes': self.obj.modes
        # 	}
        # 	self.log.logger.info('Generating {}'.format(output_file+"_generate.tcl"))
        # 	self.__renderTemplate("generate.tcl.j2",output_file+"_generate.tcl",template_vars)
        # 	generated_files.append(output_file+"_generate.tcl")
        # print(self.checkpoints)
        return generated_files

    def tclScript(self):
        pass

    def blackbox_inst(self, portlist, prr):
        """
        Generate blackbox instance
        """
        codegen = ASTCodeGenerator()

        for pr in range(0, len(prr)):
            port_list = []
            for each in portlist.keys():
                inst_internal = vast.Identifier(each)
                inst_port = vast.PortArg(each, inst_internal)
                port_list.append(inst_port)
            mod = vast.Instance(
                name=f"blackbox_{pr}",
                module=None,
                portlist=port_list,
                parameterlist=None,
            )
            moder = vast.InstanceList(
                module=f"inst_{pr}", instances=[mod], parameterlist=[]
            )

            self.blackbox_insts.append(codegen.visit(moder))
        # print(self.blackbox_insts)

    def blackbox_module(self, portlist, prr):
        """
        Generate blackbox module
        """
        port_list = []
        for each in portlist.keys():
            if portlist[each]["msb"] != 0 or portlist[each]["lsb"] != 0:
                width = vast.Width(
                    vast.IntConst(portlist[each]["msb"]),
                    vast.IntConst(portlist[each]["lsb"]),
                )
                if portlist[each]["direction"] == "input":
                    port = vast.Input(each, width=width)
                else:
                    port = vast.Output(each, width=width)
            else:
                if portlist[each]["direction"] == "input":
                    port = vast.Input(each)
                else:
                    port = vast.Output(each)
            port_list.append(vast.Ioport(port))
        params = vast.Paramlist([])
        ports = vast.Portlist(port_list)

        codegen = ASTCodeGenerator()

        for pr in range(0, len(prr)):
            ast = vast.ModuleDef(f"blackbox_{pr}", params, ports, [])
            self.blackbox_modules.append(codegen.visit(ast))

    def __replacePragma(self, replace_file, pragma_list):
        new_gen = ""
        index = 0
        for line in replace_file.splitlines():
            new_gen += Template(line).render(
                xilinx_pragma=pragma_list[index]) + "\n"
            if ("{{ xilinx_pragma }}" in line) and (index < (len(pragma_list) - 1)):
                index = index + 1
        print(pragma_list)
        print(new_gen)
        return new_gen

    def __lookup_pragma(self, port, protocol_file):
        self.log.logger.info(f"{port}, {protocol_file}")
        return protocol_file[port]

    def wrapper(self, module, protocol_file=None, xilinx_pragmas=None):
        import interfacer.interface as inter

        self.log.logger.info(
            "Generating wrapper (Xilinx Pragmas: {})".format(xilinx_pragmas)
        )
        port_list = []
        bb_black_list = []
        wire_list = []
        pragma_list = []
        # print(self.port_list)
        i = inter.Interface(self.port_list)
        for pr in range(0, len(self.prr)):
            black_list = []
            for each in self.port_list:
                name = f"{each}_{pr}"
                self.log.logger.info(f"Port: {each}_{pr}")
                port = None
                print(self.port_list[each]["msb"], self.port_list[each]["lsb"])
                if self.port_list[each]["msb"] - self.port_list[each]["lsb"] != 0:
                    width = vast.Width(
                        vast.IntConst(self.port_list[each]["msb"]),
                        vast.IntConst(self.port_list[each]["lsb"]),
                    )
                else:
                    width = None
                arg = vast.PortArg(each, vast.Identifier(name))
                wire = vast.Wire(f"{each}_{pr}_wire", width=width)
                wire_list.append(wire)
                # modifiy below here 'each' should be port family from protocol_file
                valid = i.pragma(
                    each, self.__lookup_pragma(each, protocol_file), modifier=f"_{pr}"
                )
                if valid:
                    pragma_list.append(valid)
                if self.port_list[each]["direction"] == "input":
                    if xilinx_pragmas and (valid):
                        port = XilinxPragmaInput(name, width=width)
                        port.__class__.__name__ = "{{ xilinx_pragma }}\ninput"
                    else:
                        port = vast.Input(name, width=width)
                else:
                    if xilinx_pragmas and (valid):
                        port = XilinxPragmaOutput(name, width=width)
                        port.__class__.__name__ = "{{ xilinx_pragma }}\noutput"
                    else:
                        port = vast.Output(name, width=width)

                port_list.append(vast.Ioport(port, vast.Wire(name)))
                black_list.append(arg)
                valid = None
            bb_black_list.append(black_list)

        params = vast.Paramlist([])
        ports = vast.Portlist(port_list)

        blackbox_list = []
        for pr in range(0, len(self.prr)):
            blackbox = vast.Instance(
                f"blackbox_{pr}", f"inst_{pr}", bb_black_list[pr], params, array=None
            )
            if xilinx_pragmas:
                blackbox_inst = vast.InstanceList(
                    f"blackbox_{pr}", [], [blackbox])
            else:
                blackbox_inst = vast.InstanceList(
                    f"blackbox_{pr}", [], [blackbox])
            blackbox_list.append(blackbox_inst)

        items = []
        # items.append(pragma_list)
        for bb in blackbox_list:
            items.append(bb)

        ast = vast.ModuleDef("pr_wrapper", params, ports, items)

        codegen = ASTCodeGenerator()
        if xilinx_pragmas and (len(pragma_list) > 0):
            self.log.logger.info(
                "Inserting {} Xilinx Pragmas".format(len(pragma_list)))
            self.wrapper_file = self.__replacePragma(
                codegen.visit(ast), pragma_list)
        else:
            self.wrapper_file = codegen.visit(ast)
        # print(f'code - {self.wrapper_file}')

    def __check_compatibility(self, modules: list) -> (bool, list):
        """
        Checks that modules have matching ports to generate PPRs
        """
        mod_list = []
        superset = [None, None]
        self.log.logger.info("Checking module ports align")
        for module in modules:
            mod_list.append(set(module.ports))
            if module.ports is None:
                self.log.logger.error(
                    f"Module {module.name} does not contain any ports"
                )
            if superset[0] is None:
                superset[0] = module.ports
                superset[1] = module.name
            elif len(mod_list) != 0:
                if set(module.ports).issubset(superset[0]):
                    pass
                elif set(module.ports).issuperset(superset[0]):
                    superset[0] = module.ports
                    superset[1] = module.name
                else:
                    self.log.logger.error(
                        f"Module {module.name} is neither a subset or superset of {superset[1]}"
                    )
                    return False, []
            else:
                superset = module
        return True, superset[0]

    def __report_iterator(self, template):
        with open(template, "r") as t:
            for line in t:
                if "endmodule" in line:
                    break
                yield line

    def __insert_blackbox_inst(self):
        with open(self.static.file, "rw") as f:
            for line in self.report_iterator(f):
                f.write("toot")

    def implement(self):
        """
        Implements new static region with blackboxes for PRRs
        """
        success, self.port_list = self.__check_compatibility(self.modules)
        if len(self.modules) < len(self.prr):
            self.log.logger.warning(
                f"{len(self.prr)} PRR exceeds number of modules ({len(self.modules)})"
            )
        if not success:
            self.log.logger.error("Modules are not compatible")
            exit()
        # print(f'Final ports - {port_list}')
        # print(port_list.keys())
        self.blackbox_inst(self.port_list, self.prr)
        self.blackbox_module(self.port_list, self.prr)
        # print(f'Port_List: {self.port_list}')

        if self.static:
            pass
        else:
            self.wrapper
