from pathlib import Path
from pprint import pformat
import sys

from hloc import extract_features, match_features, pairs_from_retrieval
from hloc import localize_sfm


folder = sys.argv[1]
query_file = sys.argv[2]
output = sys.argv[3]

dataset = Path(folder)  # change this if your dataset is somewhere else
images = dataset

sfm_pairs = dataset / 'pairs-db-covis20.txt'  # top 20 most covisible in SIFT model
loc_pairs = dataset / 'pairs-query-netvlad50.txt'  # top 50 retrieved by NetVLAD ?CHYBI?

outputs = Path(output)  # where everything will be saved
reference_sfm = dataset / 'sfm_superpoint+superglue'  # the SfM model we will build
results = outputs / 'hololens_hloc_superpoint+superglue_netvlad50.txt'  # the result file

# pick one of the configurations for extraction and matching
# you can also simply write your own here!
retrieval_conf = extract_features.confs['netvlad']
feature_conf = extract_features.confs['superpoint_aachen']
matcher_conf = match_features.confs['superglue']

feature_path = extract_features.main(feature_conf, images, outputs)


sfm_match_path = dataset / 'feats-superpoint-n4096-r1024_matches-superglue_pairs-db-covis20'
global_descriptors = extract_features.main(retrieval_conf, images, outputs)


pairs_from_retrieval.main(
    global_descriptors, loc_pairs, 50,
    query_prefix='query', db_model=reference_sfm)

loc_match_path = match_features.main(matcher_conf, loc_pairs, feature_conf['output'], outputs)


localize_sfm.main(
    reference_sfm,
    Path(query_file),
    loc_pairs,
    feature_path,
    loc_match_path,
    results,
    covisibility_clustering=False)  # not required with SuperPoint+SuperGlue