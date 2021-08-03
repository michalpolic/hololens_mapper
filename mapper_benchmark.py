from Mapper import Mapper

# example dataset
data_dir = "/local/artwin/mapping/data/"
recoring_dir = "benchmark/desk"
uvdata_path = "uvdata.txt"
out_dir = "benchmark_results/desk"

mapper = Mapper(data_dir)
mapper.run(recoring_dir, uvdata_path, out_dir)