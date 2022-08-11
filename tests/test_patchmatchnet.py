import pytest
from pathlib import Path

from src.utils.UtilsContainers import UtilsContainers


def test_docker_patchmatchnet_on_ETH3D():
    Path("d:/tmp/eth3d_door/output").mkdir(parents=True, exist_ok=True)
    patchmatchnet_container = UtilsContainers("docker", "patchmatchnet", "/host_mnt/d/tmp/eth3d_door")

    #python3  eval.py --input_folder=/data/door --output_folder=/data/output --checkpoint_path=/app/checkpoints/params_000007.ckpt --num_views 7 --image_max_dim 2048 --geo_mask_thres 5 --photo_thres 0.8
    patchmatchnet_container.command_dict("python3 eval.py", 
            {"input_folder": "/data/door", 
            "output_folder": "/data/output",
            "checkpoint_path": "/app/checkpoints/params_000007.ckpt",
            "num_views": 7,
            "image_max_dim": 2048,
            "geo_mask_thres": 5,
            "photo_thres": 0.8
            })
