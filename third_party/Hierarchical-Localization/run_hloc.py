import sys
import os
from pathlib import Path
from pprint import pformat
from hloc import extract_features, match_features, pairs_from_retrieval
from hloc import localize_sfm

# input
map_folder = sys.argv[1]
query_file = sys.argv[2]
output_folder = sys.argv[3]
image_descriptor = 'netvlad'
keypoint_detector = 'feats-r2d2-n5000-r1024'
matcher = 'superglue'
if len(sys.argv) >= 4:
    image_descriptor = sys.argv[4]
if len(sys.argv) >= 5:
    keypoint_detector = sys.argv[5]
if len(sys.argv) >= 6:
    matcher = sys.argv[6]

map_path = Path(map_folder) 
db_images_path = map_path
query_folder_path = Path(query_file).parent
query_images_path = query_folder_path

# setting 
retrieval_conf = extract_features.confs[image_descriptor]
feature_conf = extract_features.confs[keypoint_detector]
matcher_conf = match_features.confs[matcher]

# database features and descriptors
reference_sfm = map_path / 'sfm_superpoint+superglue'
db_feature_path = map_path / 'feats-superpoint-n4096-r1024.h5'
db_descriptors_path = map_path / 'global-feats-netvlad.h5'

# output paths
output_path = Path(output_folder)
query_pairs_path = output_path / 'pairs-query-netvlad50.txt' 
results_path = output_path / 'query_localization_results.txt' 


# ---------------------------------------------------
#              localization process 
# ---------------------------------------------------

# detect feature points on query images, extract NetVLAD descriptors for query images
query_feature_path = extract_features.main(feature_conf, query_images_path, output_path)
query_descriptors_path = extract_features.main(retrieval_conf, query_images_path, output_path)

# global descriptor matching
pairs_from_retrieval.main(query_descriptors_path, query_pairs_path, 50, query_prefix='query', \
    db_model=reference_sfm, db_descriptors = db_descriptors_path)

# feature points matching
loc_match_path = match_features.main(matcher_conf, query_pairs_path, feature_conf['output'],\
    output_path, None, db_feature_path)

# calculate the poses in global coordinate system
localize_sfm.main(
    reference_sfm,
    Path(query_file),
    query_pairs_path,
    query_feature_path,
    loc_match_path,
    results_path,
    covisibility_clustering=False)  # not required with SuperPoint+SuperGlue