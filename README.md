Welcome in repository focused on processing AR devices recordings. 

That main goal of this project is to implement all the research codes in single place that allow easy setup, easy buils, and remove the time that is required to reinstall all the repositories, writing the format conversion, and wrappers for deployment. The overview of the codes will be here (TODO), however, you can simply run the GUI and load the pipeline that are already done, e.g., localization, dense and sparse mapping, downloading of the AR device recordings, dense point clouds alignment, etc..

---------------------------------------------------------------------------------------------------
                                HOW TO INSTALL ME
---------------------------------------------------------------------------------------------------
1) Requirements (install in advance)
* Git
* Cmake 
* Anaconda
* Singularity (Linux) / Docker (Windows) (most of the codes are in containers to run on any machine)

2) Clone this repository and its submodules
* git clone --recurse-submodules --remote-submodules https://github.com/michalpolic/hololens_mapper.git

3) Create or copy the Docker/Singularity containers   (copy the containers if available, otherwise use code in init.sh)
4) Create the conda environment  (use code in init.sh)
5) Compile the C++ codes  (use code in init.sh)
6) Download pre-trained weights for NetVLAD  (use code in init.sh)
* Run the initialization (steps 3-6): `sh ./init.sh`  (building the containes may take few hours)

7) Activate conda enviroment
* In general: `conda activate meshroom`
* Using VS Code: `F1 -> Python:Select Interpreter -> meshroom`

8) If debuging in VS Code
* Specify what should be called and which parameters to use. Create `launch.json`, for example:
```
 {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Meshroom GUI",
            "type": "python",
            "request": "launch",
            "program": "<path to hololens_mapper>/third_party/meshroom/meshroom/ui",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "<path to hololens_mapper>/third_party/meshroom;<path to hololens_mapper>"
            }
        },
        {
            "name": "Meshroom batch",
            "type": "python",
            "request": "launch",
            "program": "<path to hololens_mapper>/third_party/meshroom/bin/meshroom_compute",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": 
                "<path to hololens_mapper>/third_party/meshroom/meshroom;<path to hololens_mapper>/third_party/meshroom;<path to hololens_mapper>"
            },
            "args": [
                "<path to hololens_mapper>/pipelines/<your pipeline name.mg>",
                "--cache",
                "<your output cache folder>/<evaluation folder>"
            ]
        }
    ]
}
```
* If not using VS Code, execute:
- a) `export PYTHONPATH="$PYTHONPATH;<path to hololens_mapper>/third_party/meshroom;<path to hololens_mapper>"`
- b) run `python <path to hololens_mapper>/third_party/meshroom/meshroom/ui`


---------------------------------------------------------------------------------------------------
                                    HOW TO RUN ME
---------------------------------------------------------------------------------------------------
If you finished previous section, you can create, build, modify, and test your pipelines in Meshroom GUI.
* The pipelines that will be uploaded in git are in `<path to hololens_mapper>/pipelines`
* If you want any "private" pipeline, start it with `tmp_<your private pipeline name>.mg` 


---------------------------------------------------------------------------------------------------
                                    HOW TO CONTRIBUTE
---------------------------------------------------------------------------------------------------
If you would like to add your nodes: 
* Find a simple node, e.g., `<path to hololens_mapper>/third_party/meshroom/meshroom/nodes/Alignment/DensePonitcloudsConcatenator.py`
* Make your own copy to proper folder in `<path to hololens_mapper>/third_party/meshroom/meshroom/nodes` (please follow reasonable naming)
* Modify the content as you wish

To add your own source codes:
* The source codes are located in `<path to hololens_mapper>/src` (please, follow reanable naming)
* Your own containers building add into `sh ./init.sh`