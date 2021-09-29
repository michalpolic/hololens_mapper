from Mapper import Mapper

# example dataset
data_dir = "/local/artwin/data/"
recoring_dir = "Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1"
uvdata_path = "uvdata.txt"
out_dir = "Munich/HoloLensRecording__2021_08_02__11_23_59_MUCLab_1_results"

mapper = Mapper(data_dir)
mapper.run(recoring_dir, uvdata_path, out_dir)
