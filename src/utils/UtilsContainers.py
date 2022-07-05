import os

class UtilsContainers:
    """Class for simpler execution of Singularity/Docker commands"""
    _working_dir = ""

    def __init__(self, container_type, image, working_dir, lib_prefix = "", logger = None):
        """Init setup the Singularity/Docker image for calling the commands
        Input: 
            container_type (str) - {docker, singularity}
            image - the image name to run it
            working_dir - mounted directory to /data in container (add /data prefix when access the data in comands)
            lib_prefix - path to library in the container if executable is not in the path
            logger - object for Meshroom loging
        """
        assert (container_type == "docker" or container_type == "singularity"), f"The container type {container_type} is unknown."
        
        self._container_type = container_type
        self._image = image
        self._working_dir = working_dir
        self._lib_prefix = lib_prefix
        self._logger = logger


    def command(self, command):
        """Process single command.
        Input: 
            command (str) - the command which will be executed in the container
        Node:
            Working directory is mounted to /data dir. You have to use path to data in format /data/<rel_path>.
        """
        if self._container_type == "docker":
            command_line = f"docker run --rm --gpus all -v {self._working_dir}:/data {self._image} {self._lib_prefix}{command}"    # 
        if self._container_type == "singularity":
            command_line = f"singularity exec --nv -B {self._working_dir}:/data {self._image} {self._lib_prefix}{command}"

        if self._logger:
            self._logger.info("Run: " + command_line)
        else:
            print("Run: " + command_line)

        os.system(command_line)


    def command_dict(self, command_name, dict_params):
        """Process single command composed of dictionary with parameters
        Input: 
            command_name (str) - the executable name
            dict_params (dict) - the dictionary with parameters
        """
        command_params = ""
        for name, value in dict_params.items():
            command_params += f"--{name}={value} "
        self.command(f"{command_name} {command_params}")
        