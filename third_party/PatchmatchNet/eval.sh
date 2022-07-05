. /usr/local/etc/profile.d/conda.sh
conda activate patchmatchnet2
python3 /app/eval.py --input_folder=$1 --output_folder=$2 --checkpoint_path=$3 --num_views=$4 --image_max_dim=$5 --geo_mask_thres=$6 --photo_thres=$7