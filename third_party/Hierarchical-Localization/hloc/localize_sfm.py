import argparse
import logging
import numpy as np
from pathlib import Path
from collections import defaultdict
import h5py
from tqdm import tqdm
import pickle
import pycolmap

from .utils.read_write_model import Point3D, read_model, write_model
from .utils.parsers import parse_image_lists, parse_retrieval, names_to_pair


def do_covisibility_clustering(frame_ids, all_images, points3D):
    clusters = []
    visited = set()

    for frame_id in frame_ids:
        # Check if already labeled
        if frame_id in visited:
            continue

        # New component
        clusters.append([])
        queue = {frame_id}
        while len(queue):
            exploration_frame = queue.pop()

            # Already part of the component
            if exploration_frame in visited:
                continue
            visited.add(exploration_frame)
            clusters[-1].append(exploration_frame)

            observed = all_images[exploration_frame].point3D_ids
            connected_frames = set(
                j for i in observed if i != -1 for j in points3D[i].image_ids)
            connected_frames &= set(frame_ids)
            connected_frames -= visited
            queue |= connected_frames

    clusters = sorted(clusters, key=len, reverse=True)
    return clusters


def pose_from_cluster(qname, qinfo, db_ids, db_images, points3D,
                      feature_file, match_file, thresh):
    kpq = feature_file[qname]['keypoints'].__array__()
    kp_idx_to_3D = defaultdict(list)
    kp_idx_to_3D_to_db = defaultdict(lambda: defaultdict(list))
    num_matches = 0

    for i, db_id in enumerate(db_ids):
        db_name = db_images[db_id].name
        points3D_ids = db_images[db_id].point3D_ids
        if len(points3D_ids) == 0:
            logging.debug(f'No 3D points found for {db_name}.')
            continue

        pair = names_to_pair(qname, db_name)
        matches = match_file[pair]['matches0'].__array__()
        valid = np.where(matches > -1)[0]
        valid = valid[points3D_ids[matches[valid]] != -1]
        num_matches += len(valid)

        for idx in valid:
            id_3D = points3D_ids[matches[idx]]
            kp_idx_to_3D_to_db[idx][id_3D].append(i)
            # avoid duplicate observations
            if id_3D not in kp_idx_to_3D[idx]:
                kp_idx_to_3D[idx].append(id_3D)

    idxs = list(kp_idx_to_3D.keys())
    mkp_idxs = [i for i in idxs for _ in kp_idx_to_3D[i]]
    mkpq = kpq[mkp_idxs]
    mkpq += 0.5  # COLMAP coordinates

    mp3d_ids = [j for i in idxs for j in kp_idx_to_3D[i]]
    mp3d = [points3D[j].xyz for j in mp3d_ids]
    mp3d = np.array(mp3d).reshape(-1, 3)

    # mostly for logging and post-processing
    mkp_to_3D_to_db = [(j, kp_idx_to_3D_to_db[i][j])
                       for i in idxs for j in kp_idx_to_3D[i]]

    camera_model, width, height, params = qinfo
    cfg = {
        'model': camera_model,
        'width': width,
        'height': height,
        'params': params,
    }
    ret = pycolmap.absolute_pose_estimation(mkpq, mp3d, cfg, thresh)
    ret['cfg'] = cfg
    return ret, mkpq, mp3d, mp3d_ids, num_matches, (mkp_idxs, mkp_to_3D_to_db)

# import collections
# Point3D = collections.namedtuple(
#     "Point3D", ["id", "xyz", "rgb", "error", "image_ids", "point2D_idxs"])

def compose_simple_subreconstruction(cameras, images, points3D, images_list):
    # do not check observations and points in 3D 
    ncameras = {}
    nimages = {}
    npoints3D = {}
    for img in images.values():
        if img.name in images_list:
            nimages[img.id] = img
            ncameras[img.camera_id] = cameras[img.camera_id]
    
    new_img_ids = list(nimages.keys())
    for pt_id in points3D:
        pt = points3D[pt_id]
        filter_images = [False for i in range(len(pt.image_ids))]
        for i in range(len(pt.image_ids)):
            if pt.image_ids[i] in new_img_ids:
                filter_images[i] = True
        npoints3D[pt.id] = Point3D(id=pt.id, xyz=pt.xyz, rgb=pt.rgb,
            error=pt.error, image_ids=pt.image_ids[filter_images],
            point2D_idxs=pt.point2D_idxs[filter_images])
        
    return (ncameras, nimages, npoints3D)


def main(reference_sfm, queries, retrieval, features, matches, results,
         ransac_thresh=12, covisibility_clustering=False,
         prepend_camera_name=False, min_common_p3d=50):

    assert reference_sfm.exists(), reference_sfm
    assert retrieval.exists(), retrieval
    assert features.exists(), features
    assert matches.exists(), matches

    queries = parse_image_lists(queries, with_intrinsics=True)
    retrieval_dict = parse_retrieval(retrieval)

    logging.info('Reading 3D model...')
    cameras, db_images, points3D = read_model(str(reference_sfm))
    db_name_to_id = {image.name: i for i, image in db_images.items()}

    feature_file = h5py.File(features, 'r')
    match_file = h5py.File(matches, 'r')

    poses = {}
    neighbours = {}
    logs = {
        'features': features,
        'matches': matches,
        'retrieval': retrieval,
        'loc': {},
    }
    logging.info('Starting localization...')
    q_2d3d_cp = {}
    for qname, qinfo in tqdm(queries):
        if qname not in retrieval_dict:
            logging.warning(f'No images retrieved for query image {qname}. Skipping...')
            continue
        db_names = retrieval_dict[qname]
        db_ids = []
        for n in db_names:
            if n not in db_name_to_id:
                logging.warning(f'Image {n} was retrieved but not in database')
                continue
            db_ids.append(db_name_to_id[n])

        if covisibility_clustering:
            clusters = do_covisibility_clustering(db_ids, db_images, points3D)
            best_inliers = 0
            best_cluster = None
            logs_clusters = []
            for i, cluster_ids in enumerate(clusters):
                ret, mkpq, mp3d, mp3d_ids, num_matches, map_ = (
                        pose_from_cluster(
                            qname, qinfo, cluster_ids, db_images, points3D,
                            feature_file, match_file, thresh=ransac_thresh))
                if ret['success'] and ret['num_inliers'] > best_inliers:
                    best_cluster = i
                    best_inliers = ret['num_inliers']
                logs_clusters.append({
                    'db': cluster_ids,
                    'PnP_ret': ret,
                    'keypoints_query': mkpq,
                    'points3D_xyz': mp3d,
                    'points3D_ids': mp3d_ids,
                    'num_matches': num_matches,
                    'keypoint_index_to_db': map_,
                })
            if best_cluster is not None:
                ret = logs_clusters[best_cluster]['PnP_ret']
                poses[qname] = (ret['qvec'], ret['tvec'])
            logs['loc'][qname] = {
                'db': db_ids,
                'best_cluster': best_cluster,
                'log_clusters': logs_clusters,
                'covisibility_clustering': covisibility_clustering,
            }
        else:
            ret, mkpq, mp3d, mp3d_ids, num_matches, map_ = pose_from_cluster(
                qname, qinfo, db_ids, db_images, points3D,
                feature_file, match_file, thresh=ransac_thresh)
            q_2d3d_cp[qname] = {'mkpq': mkpq, 'mp3d': mp3d, 'result': ret, 'thresh': ransac_thresh}

            if ret['success']:
                poses[qname] = (ret['qvec'], ret['tvec'])
                mp3d_inliers = [pt_id for (i,pt_id) in enumerate(mp3d_ids) if ret['inliers'][i]]
                list_img_ids = [np.ndarray.tolist(points3D[pt_id].image_ids) \
                    for pt_id in mp3d_inliers]
                unique_img_ids, counts_img_ids = np.unique(np.array([item for sublist \
                    in list_img_ids for item in sublist]), return_counts=True)
                neighbours[qname] = [db_images[unique_img_ids[l]].name for l in \
                    range(len(unique_img_ids)) if counts_img_ids[l] > min_common_p3d]
            else:
                closest = db_images[db_ids[0]]
                poses[qname] = (closest.qvec, closest.tvec)
            logs['loc'][qname] = {
                'db': db_ids,
                'PnP_ret': ret,
                'keypoints_query': mkpq,
                'points3D_xyz': mp3d,
                'points3D_ids': mp3d_ids,
                'num_matches': num_matches,
                'keypoint_index_to_db': map_,
                'covisibility_clustering': covisibility_clustering,
            }


    logging.info(f'Localized {len(poses)} / {len(queries)} images.')
    logging.info(f'Writing poses to {results}...')
    with open(results, 'w') as f:
        for q in poses:
            qvec, tvec = poses[q]
            qvec = ' '.join(map(str, qvec))
            tvec = ' '.join(map(str, tvec))
            #name = q.split('/')[-1]
            name = q.replace('query/','')
            if prepend_camera_name:
                name = q.split('/')[-2] + '/' + name
            f.write(f'{name} {qvec} {tvec}\n')
    
    pairs_path = results.parent / 'image_pairs.txt'
    logging.info(f'Writing found image pairs to {pairs_path}...')
    with open(pairs_path, 'w') as f:
        for q in neighbours:
            for d in neighbours[q]:
                orig_query_rel_path = q.replace('query/','')
                f.write(f'{orig_query_rel_path} {d}\n')

    logging.info(f'Writing subreconstruction of global map {results.parent}...')
    used_db_images = {}
    for q in neighbours:
        for d in neighbours[q]:
            used_db_images[d] = True
    n_cameras, n_images, n_points3D = compose_simple_subreconstruction(\
        cameras, db_images, points3D, used_db_images.keys())
    write_model(n_cameras, n_images, n_points3D, results.parent, ext = '.txt')

    corresp_path = results.parent / 'corresp_2d-3d.npy'
    logging.info(f'Writing 2D-3D correspondences {corresp_path}...')
    np.save(corresp_path, q_2d3d_cp)

    logs_path = f'{results}_logs.pkl'
    logging.info(f'Writing logs to {logs_path}...')
    with open(logs_path, 'wb') as f:
        pickle.dump(logs, f)
    logging.info('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference_sfm', type=Path, required=True)
    parser.add_argument('--queries', type=Path, required=True)
    parser.add_argument('--features', type=Path, required=True)
    parser.add_argument('--matches', type=Path, required=True)
    parser.add_argument('--retrieval', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--ransac_thresh', type=float, default=12.0)
    parser.add_argument('--covisibility_clustering', action='store_true')
    parser.add_argument('--prepend_camera_name', action='store_true')
    args = parser.parse_args()
    main(**args.__dict__)
