import os

class UtilsSingularity:
    """Class for simpler execution of Singularity commands"""
    _working_dir = ""

    def __init__(self, path_to_singularity_image, working_dir, lib_prefix = ""):
        """Init setup the Singularity image for calling the commands"""
        self._path_to_singularity_image = path_to_singularity_image
        self._working_dir = working_dir
        self._lib_prefix = lib_prefix

    def command(self, command):
        """Process single command"""
        command_line = f"singularity exec --nv -B {self._working_dir}:/host_pwd --pwd /host_pwd {self._path_to_singularity_image} {self._lib_prefix}{command}"
        print(command_line)
        os.system(command_line)

    def command_dict(self, command_name, dict_params):
        command_params = ""
        for name, value in dict_params.items():
            command_params += f"--{name}={value} "
        self.command(f"{command_name} {command_params}")
        