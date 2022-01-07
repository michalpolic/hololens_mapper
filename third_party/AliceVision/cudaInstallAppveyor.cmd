@echo off

set CUDA_VERSION_MAJOR=11
set CUDA_VERSION_MINOR=0
set CUDA_VERSION_MICRO=1
set DRIVER_VERSION=451.22
set OS_PLATFORM=win10

set CUDA_VERSION=%CUDA_VERSION_MAJOR%.%CUDA_VERSION_MINOR%
set CUDA_VERSION_FULL=%CUDA_VERSION%.%CUDA_VERSION_MICRO%
set CUDA_SDK_FILENAME=cuda_%CUDA_VERSION_FULL%_%DRIVER_VERSION%_%OS_PLATFORM%
set CUDA_SDK_URL=https://developer.download.nvidia.com/compute/cuda/%CUDA_VERSION_FULL%/local_installers/%CUDA_SDK_FILENAME%.exe

echo Downloading CUDA toolkit %CUDA_VERSION_FULL%
echo -- url: %CUDA_SDK_URL%

appveyor DownloadFile %CUDA_SDK_URL% -FileName %CUDA_SDK_FILENAME%.exe
dir

echo Installing CUDA toolkit %CUDA_VERSION_FULL%
%CUDA_SDK_FILENAME%.exe -s nvcc_%CUDA_VERSION% ^
                           cublas_%CUDA_VERSION% ^
                           cublas_dev_%CUDA_VERSION% ^
                           cudart_%CUDA_VERSION% ^
                           curand_%CUDA_VERSION% ^
                           curand_dev_%CUDA_VERSION%

echo CUDA toolkit installed

dir "%ProgramFiles%"

set CUDA_PATH=%ProgramFiles%\NVIDIA GPU Computing Toolkit\CUDA\v%CUDA_VERSION%
set CUDA_BIN_PATH=%CUDA_PATH%\bin

set PATH=%CUDA_BIN_PATH%;%CUDA_PATH%\libnvvp;%PATH%

nvcc -V
