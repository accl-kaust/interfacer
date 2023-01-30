
from jinja2 import Environment, PackageLoader, Template
import logging
from pathlib import Path
import glob
import subprocess
from colorlog import ColoredFormatter
import os


class Tool(object):
    """
    Parent class for tool utilities
    """

    def __init__(self):
        # print(__package__)
        # self.jinja_env = Environment(
        # 	loader = PackageLoader(__package__,'templates'),
        # 	trim_blocks = True,
        # 	lstrip_blocks = True,
        # 	keep_trailing_newline = True,
        # )
        pass

    def add_whitespace(self, verilog):
        with open(verilog, "a") as f:
            f.write("\n")

    def remove_artifacts(self, directory, ext: list):
        for artifact in ext:
            for each in glob.glob(f'{directory}/**/*{artifact}', recursive=True):
                Path(each).unlink()
            # Path.unlink(each)
            # stem = Path(each).ste
            # print(stem)

    def xilinx_tool(self, xilinx_dir, tool, version, tcl) -> (str, bool):
        output = open(f'.logs/{tool}_{tcl}.log', 'w')
        e = subprocess.run(
            f'{xilinx_dir}/{tool.title()}/{version}/bin/{tool} -mode batch -nojournal -nolog -notrace -source {tcl}'.split(), stdout=output, stderr=output)
        # e.wait()
        if e.returncode != 0:
            return (f'.logs/{tool}_{tcl}.log', False)
        else:
            return (f'.logs/{tool}_{tcl}.log', True)

    def renderTemplate(self, template_file, target_file, template_vars={}):
        template = self.jinja_env.get_template(template_file)
        with open(target_file, 'w') as f:
            f.write(template.render(template_vars))


class Log(object):
    def __init__(self, name, enable=False, testing=False):
        self.logger = self.init_logger(name, enable, testing=testing)

    def setup_logger(self):
        """Return a logger with a default ColoredFormatter."""
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',
            }
        )

        logger = logging.getLogger('example')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        return logger

    def init_logger(self, dunder_name, enable, testing) -> logging.Logger:

        stdout_formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'purple',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',
            }
        )

        logger = logging.getLogger(__package__+'.'+dunder_name)

        if not enable:
            logger.disabled = True
        if not os.path.exists('.logs'):
            os.makedirs('.logs')
        logger.setLevel(logging.DEBUG)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('.logs/interfacer.log')
        c_handler.setLevel(logging.ERROR)
        f_handler.setLevel(logging.INFO)

        f_format = logging.Formatter(
            '%(asctime)s - %(name)-20s - %(levelname)-20s - %(message)s')
        c_handler.setFormatter(stdout_formatter)
        f_handler.setFormatter(f_format)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        return logger
