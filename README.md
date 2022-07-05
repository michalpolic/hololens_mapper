
Init the enviroments required:
* Install Singularity from https://sylabs.io/guides/3.0/user-guide/installation.html 
* Run the initialization: "bash ./singularity/init.sh"

How to run: 
* TODO ..

```
mkdir ./src/meshroom/MeshroomCpp/build
cd ./src/meshroom/MeshroomCpp/build
cmake -D Python_EXECUTABLE=$(which python) -D pybind11_DIR="$(conda info --json | jq -r '.active_prefix')/share/cmake/pybind11" ..
cmake --build . --config Release --target install
```

