import argparse
import numpy as np
import os
import sys
import glob
from tqdm import tqdm
from pathlib import Path


def get_memory_usage(total_memory_ram = 60000):
    total_memory, used_memory, free_memory = map( \
        int, os.popen('free -t -m').readlines()[-1].split()[1:])
    return round((used_memory/total_memory_ram) * 100, 2)


def write_pointcloud_to_file(file_path, xyz, rgb):
    """Append dense points into file.
    Input: 
        file_path - path .obj file
        xyz - dense pointcloud
        rgb - colors
    """
    assert file_path, "file_path is empty"
    assert xyz.any(), "pointcloud to save is empty"

    b = bytearray()
    if not os.path.isfile(file_path):
        b.extend(map(ord, "o Object.1\n"))

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'ab') as objfile:
        list_of_rows = [f"v {xyz[0,i]} {xyz[1,i]} {xyz[2,i]} {rgb[0,i]} {rgb[1,i]} {rgb[2,i]}\n" for i in range(np.shape(xyz)[1])]
        b.extend(map(ord, ''.join(list_of_rows)))
        objfile.write(b)


def hash_vertices(xyz, rgb, hash_scale):
    hashed_xyz = np.round(xyz * hash_scale).astype(dtype=np.int32)
    unique_hashed_xyz, indices = np.unique(hashed_xyz, return_index=True, axis=0)
    unique_rgb = rgb[indices,:]
    return (unique_hashed_xyz.astype(dtype=np.float32) * (1/hash_scale), unique_rgb)

def process_points(input_folder, output_folder, hash_scale):
    dir_list = glob.glob(input_folder + '/*.npy')

    print("Concatenate and hash points ...")
    all_xyz = []
    all_rgb = []

    for vertices_file in tqdm(dir_list):
        data = np.load(vertices_file, allow_pickle=True)
        xyz, rgb = hash_vertices(data.item().get("vertices"), data.item().get("vertex_colors"), hash_scale)
        all_xyz.append(xyz)
        all_rgb.append(rgb)
        
        if get_memory_usage() > 80:
            xyz, rgb = hash_vertices(np.concatenate(all_xyz, axis=0), np.concatenate(all_rgb, axis=0), hash_scale)
            write_pointcloud_to_file(Path(output_folder) / "model.obj", xyz.T, rgb.T)
            all_xyz = []
            all_rgb = []

    xyz, rgb = hash_vertices(np.concatenate(all_xyz, axis=0), np.concatenate(all_rgb, axis=0), hash_scale)
    write_pointcloud_to_file(Path(output_folder) / "model.obj", xyz.T, rgb.T)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fuse computed point clouds")

    # High level input/output options
    parser.add_argument("--input_folder", type=str, help="input data path")
    parser.add_argument("--output_folder", type=str, default="", help="output path")
    parser.add_argument("--hash_scale", type=int, default=100, help="the scale of hashing, i.e., one point per 1 = m, 100 = cm, 1000 = mm")

    input_args = parser.parse_args()

    if input_args.input_folder is None or not os.path.isdir(input_args.input_folder):
        raise Exception("Invalid input folder: {}".format(input_args.input_folder))

    if not input_args.output_folder:
        input_args.output_folder = input_args.input_folder

    process_points(input_args.input_folder, input_args.output_folder, input_args.hash_scale)