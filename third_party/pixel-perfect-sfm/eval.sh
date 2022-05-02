. /usr/local/etc/profile.d/conda.sh
conda activate pixel-perfect-sfm
pip install pycolmap
python /app/examples/refine_colmap.py --dataset=$1 --outputs=$2 --tag=$3