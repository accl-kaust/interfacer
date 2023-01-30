import subprocess
import datetime
from .utils.tool import Tool, Log
import xml.etree.ElementTree as ET
from jinja2 import Environment, PackageLoader, Template
import glob
from pathlib import Path
import re


class Module(Tool):
    """
    Base class for managing Module extraction
    """

    def __init__(
        self,
        top,
        files,
        version,
        project,
        ipcores=None,
        directory="rtl",
        output_dir="build",
        xdc=None,
        xilinx_dir="/tools/Xilinx",
        skip=["skip"],
        vhdl=None,
        tcl=None,
        force=False,
    ):
        self.jinja_env = Environment(
            loader=PackageLoader(__package__, "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        self.log = Log(self.__class__.__name__, enable=True, testing=True)
        self.xilinx_dir = xilinx_dir
        self.directory = directory
        self.name = top
        self.project_name = project
        self.blackbox = None
        self.xdc = xdc
        self.protocols = None
        self.checkpoint = None
        self.files = []
        print(f"DIR: {directory}")
        for f in files:
            print(f"{Path.cwd()}/{directory}/{f}")
            my_file = Path(f"{Path.cwd()}/{directory}/{f}")
            if my_file.is_file():
                print(my_file.stem)
                print(Path(f"{directory}/{f}"))
                self.files.append(Path(f"{directory}/{f}"))
            # elif my_file.stem in skip:
            #     self.log.logger.info(f"Skipping file {f}")
            #     pass
            else:
                self.log.logger.error(f"Error could not find {f}")
                exit()
        if vhdl:
            self.vhdl = []
            for f in vhdl:
                print(f"{Path.cwd()}/{directory}/{f}")
                my_file = Path(f"{Path.cwd()}/{directory}/{f}")
                if my_file.is_file():
                    print(my_file.stem)
                    print(Path(f"{directory}/{f}"))
                    self.vhdl.append(Path(f"{directory}/{f}"))
                # elif my_file.stem in skip:
                #     self.log.logger.info(f"Skipping file {f}")
                #     pass
                else:
                    self.log.logger.error(f"Error could not find {f}")
                    exit()
        if tcl:
            self.tcl = []
            for f in tcl:
                print(f"{Path.cwd()}/{directory}/{f}")
                my_file = Path(f"{Path.cwd()}/{directory}/{f}")
                if my_file.is_file():
                    print(my_file.stem)
                    print(Path(f"{directory}/{f}"))
                    self.tcl.append(Path(f"{directory}/{f}"))
                # elif my_file.stem in skip:
                #     self.log.logger.info(f"Skipping file {f}")
                #     pass
                else:
                    self.log.logger.error(f"Error could not find {f}")
                    exit()
        if ipcores:
            self.ipcores = []
            for f in ipcores:
                print(f)
                my_file = Path(f)
                print("toot")
                if my_file.is_file():
                    print(my_file.stem)
                    self.ipcores.append(Path(f))
                # elif my_file.stem in skip:
                #     self.log.logger.info(f"Skipping file {f}")
                #     pass
                else:
                    self.log.logger.error(f"Error could not find {f}")
                    exit()
            # for path in Path('.').rglob(f'{directory}/**/*.v'):
            #     if path.name == f:
            #         self.files.append(path)
            #         break
        self.log.logger.info(f"found files {self.files}")
        # for path in Path('.').rglob(f'{directory}/**/*.v'):
        #     print(f'path - {path.name}')
        #     for each in files:
        #         print(f'files - {each.name}')
        #         if path.name in each.name:
        #             self.files.append(path)
        for each in self.files:
            self.add_whitespace(each)
        self.interface = None
        # if ipcores:
        #     self.ipcores = True
        #     self.log.logger.info("Unpacking .xci files")
        #     ip, success = self.__read_ip(ipcores, version, None)
        #     if not success:
        #         self.log.logger.error(f"Error got {ip}, expecting {version}")
        #         exit()
        #     self.ip = ip
        #     for each in ip:
        #         self.log.logger.info(f'{directory}/{each.split(".")[0]}.veo')
        #         if (
        #             not glob.glob(
        #                 f'{output_dir}/{self.project_name}.inst/{each.split(".")[0]}.veo',
        #                 recursive=True,
        #             )
        #             or (force == True)
        #         ):
        #             self.__generate_ip_template(
        #                 ip[each], version, directory, output_dir, skip=False
        #             )
        #         else:
        #             self.__generate_ip_template(
        #                 ip[each], version, directory, output_dir, skip=True
        #             )
        self.modes = {}

    # def __generate_ip_template(self, ip, version, directory, output_dir, skip=False):
    #     template_vars = {
    #         "module": ip["name"],
    #         "file": f"{output_dir}/{self.project_name}.inst/{ip['name']}.tcl",
    #         "date": datetime.datetime.now().strftime("%H:%M %d/%m/%Y"),
    #         "type": "tcl",
    #         "content": ip,
    #     }
    #     template_name = f"{ip['name']}_ip_core.tcl"
    #     self.log.logger.debug(f"Generating {template_name}")
    #     self.renderTemplate("xci.j2", template_name, template_vars)
    #     if not skip:
    #         with click_spinner.spinner():
    #             log, success = self.xilinx_tool(
    #                 self.xilinx_dir, "vivado", version, template_name
    #             )
    #             self.remove_artifacts(
    #                 ".", [".log", ".jou", ".vho", ".xml", ".out"])
    #             # Path(f"{directory}/.inst").mkdir(parents=True, exist_ok=True)
    #             # Path(f"{directory}/{ip['name']}.veo").replace(
    #             #     f"{output_dir}/{self.project_name}.inst/{ip['name']}.veo"
    #             # )
    #             if not success:
    #                 self.log.logger.error(f"ERROR - See {log}")
    #                 exit()
        # ip["ports"] = self.__extract_module(
        #     ip, f"{output_dir}/{self.project_name}.inst/{ip['name']}.veo"
        # )
        # template_vars["type"] = "verilog"
        # template_vars["file"] = f"{output_dir}/{self.project_name}.inst/{ip['name']}.v"
        # template_name = (
        #     f"{output_dir}/{self.project_name}.inst/{ip['name']}_ip_blackbox.v"
        # )
        # self.renderTemplate("ip_template.j2", template_name, template_vars)
        # if (
        #     Path(f"{output_dir}/{self.project_name}.inst/{ip['name']}_ip_blackbox.v")
        #     not in self.files
        # ):
        #     self.log.logger.info(f"inserting blackbox {ip['name']}_ip_blackbox.v")
        #     self.files.append(
        #         Path(
        #             f"{output_dir}/{self.project_name}.inst/{ip['name']}_ip_blackbox.v"
        #         )
        #     )

    def report_iterator(self, template):
        with open(template, "r") as t:
            for line in t:
                if "your_instance_name (" in line:
                    break
            for line in t:
                if ");\n" in line:
                    break
                yield line

    def __extract_module(self, ip, template) -> list:
        ports = []
        for line in self.report_iterator(template):
            port = line.split("// ")[1].split()
            del port[1]
            port = " ".join(port)
            ports.append(port)
        return ports

    def update(self, module) -> bool:
        if "ports" in module:
            self.ports = module["ports"]
        if "checkpoint" in module:
            print("adding checkpoint")
            self.checkpoint = module["checkpoint"]
        return True

    def __read_ip(self, ipcores: list, version, directory) -> tuple[str, bool]:
        ip = {}
        for xci in ipcores:
            # print(f'file - {directory}/{xci}')
            if directory:
                tree = ET.parse(f"{directory}/{xci}")
            else:
                tree = ET.parse(f"{xci}")
            root = tree.getroot()
            data = {}
            data["dir"] = directory
            data["file"] = xci
            data["name"] = root.find(
                ".//{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}instanceName"
            ).text
            meta = root.find(
                ".//{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}componentRef"
            ).attrib
            data["vendor"] = meta[
                "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}vendor"
            ]
            data["product"] = {}
            data["product"]["name"] = meta[
                "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}name"
            ]
            data["product"]["version"] = meta[
                "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}version"
            ]
            for attribs in root.findall(
                ".//{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}configurableElementValue"
            ):
                if (
                    attribs.attrib[
                        "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}referenceId"
                    ]
                    == "RUNTIME_PARAM.SWVERSION"
                ):
                    data["version"] = attribs.text
                if (
                    attribs.attrib[
                        "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}referenceId"
                    ]
                    == "PROJECT_PARAM.DEVICE"
                ):
                    data["device"] = attribs.text
                if (
                    attribs.attrib[
                        "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}referenceId"
                    ]
                    == "PROJECT_PARAM.PACKAGE"
                ):
                    data["package"] = attribs.text
                if (
                    attribs.attrib[
                        "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}referenceId"
                    ]
                    == "PROJECT_PARAM.SPEEDGRADE"
                ):
                    data["speed"] = attribs.text
                if (
                    attribs.attrib[
                        "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}referenceId"
                    ]
                    == "PROJECT_PARAM.TEMPERATURE_GRADE"
                ):
                    data["temp"] = attribs.text.lower()
            if version != data["version"]:
                return data["version"], False
            ip[xci] = data
        return ip, True


class Static(Module):
    """
    Class for managing Static Module extraction.
    """

    def __init__(
        self,
        top: str,
        files: list,
        version: str,
        project: str,
        ipcores: list = None,
        directory: str = "rtl",
        xdc: str = None,
        xilinx_dir: str = "/tools/Xilinx",
        force: bool = False,
        base: bool = False,
    ) -> None:
        """Initialize the Static Module object.

        Arguments:
            top: The Verilog top file
            files: A list of RTL files for the base design
            version: Version of Xilinx Vivado/Vitis
            project: Project name
        """
        super().__init__(
            top, files, version, project, ipcores, directory, xilinx_dir, force
        )
        self.top_file = self.__find_top()
        self.xdc = f"{directory}/{xdc}"

    def __find_top(self):
        return None

    def __check_compatibility(self, modules: list) -> tuple[bool, list]:
        """
        Checks that modules have matching ports to generate PPRs
        TODO: Allow for multiple combinations
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

    def implement(self, modules: list):
        """
        Implements new static region with blackboxes for PRRs
        """
        success, port_list = self.__check_compatibility(modules)
        if not success:
            self.log.logger.error("Modules are not compatible")
            exit()
        print(f"Final ports - {port_list}")
