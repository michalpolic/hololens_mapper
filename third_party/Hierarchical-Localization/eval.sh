. /usr/local/etc/profile.d/conda.sh
conda activate hloc2
pip install pycolmap
python /app/run_hloc.py $1 $2 $3