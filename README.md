Requirements (install in advance)
* git
* cmake 
* conda
* go
* singularity (Linux) / docker (Windows)

Init the containers and conda enviroment:
* Run the initialization: "sh ./init.sh"

How to run: 
* conda activate meshroom

```
mkdir ./src/meshroom/MeshroomCpp/build
cd ./src/meshroom/MeshroomCpp/build
cmake -D Python_EXECUTABLE=$(which python) -D pybind11_DIR="$(conda info --json | jq -r '.active_prefix')/share/cmake/pybind11" ..
cmake --build . --config Release --target install
```

