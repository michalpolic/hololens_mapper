#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <string.h> 
#include <sstream> 
#include <vector>
#include <map>
#include <cmath>
#include <iostream>

namespace py = pybind11;


class Observation{
    public:
        int observationId;
        int featureId;
        double x[2];

        Observation(int id, int fid, double u, double v){
            observationId = id;
            featureId = fid;
            x[0] = u;
            x[1] = v;
        };
};

class Landmark{
    public:
        int landmarkId;
        int color[3];
        double X[3];
        std::vector<Observation> observations;

        Landmark(int id, double* c, double* pt){
            landmarkId = id;
            for (int i = 0; i < 3; ++i){
                color[i] = int(c[i]);
                X[i] = pt[i];
            }
        };
};

std::ostream& operator<<(std::ostream& os, const Observation& o)
{
    os << "{\"observationId\":\"" << std::to_string(o.observationId) << "\",";
    os << "\"featureId\":\"" << std::to_string(o.featureId) << "\",";
    os << "\"x\":[\"" <<  std::to_string(o.x[0]) << "\"," 
        << "\"" <<  std::to_string(o.x[1]) << "\"],";
    os << "\"scale\":\"0\"}";    
    return os;
}


std::ostream& operator<<(std::ostream& os, const Landmark& lm)
{
    os << "{\"landmarkId\":\"" << std::to_string(lm.landmarkId) << "\",";
    os << "\"descType\":\"sift\"," ;
    os << "\"color\":[\"" <<  std::to_string(lm.color[0]) << "\"," 
        << "\"" <<  std::to_string(lm.color[1]) << "\"," 
        << "\"" <<  std::to_string(lm.color[2]) << "\"],";
    os << "\"X\":[\"" <<  std::to_string(lm.X[0]) << "\"," 
        << "\"" <<  std::to_string(lm.X[1]) << "\"," 
        << "\"" <<  std::to_string(lm.X[2]) << "\"],";
    os << "\"observations\":[";
    for(int i = 0; i < lm.observations.size(); ++i){
        os << lm.observations[i];
        if (i < lm.observations.size()-1){
            os << ",";
        }
    }
    os << "]}";
    return os;
}




inline std::string get_obs_hash(int u, int v){
    return std::string("obs_" + std::to_string(u) + "_" + std::to_string(v));
}

std::string encode_structure(int num_xyz, int num_visibility_map_records, 
    py::array_t<double> xyz, py::array_t<double> rgb, py::array_t<double> visibility_map){

    // input
    auto xyzbuf = xyz.request();
    double *xyz_ptr = (double *) xyzbuf.ptr;
    auto rgbbuf = rgb.request();
    double *rgb_ptr = (double *) rgbbuf.ptr;
    auto vmapbuf = visibility_map.request();
    double *vmap_ptr = (double *) vmapbuf.ptr;

    int max_img_id = 0;
    std::vector<std::vector<int>> obs_for_feature;
    obs_for_feature.reserve(num_xyz);
    py::print(std::string("Num. of pts: " + std::to_string(num_xyz)).c_str());
    py::print(std::string("Num. vis. map records: " + std::to_string(num_visibility_map_records)).c_str());

    int proc = 0;
    for (int i = 0; i < num_visibility_map_records; ++i){
        if (proc < int((double(i) / double(num_visibility_map_records))*100)){
            proc = int((double(i) / double(num_visibility_map_records))*100);
            py::print(std::string("Composing obs. for points in 3D ... " + std::to_string(proc) + " proc").c_str());
        }
        int k = int(vmap_ptr[4*i]);
        // py::print(std::string("k=" + std::to_string(k) + ", img_id=" + std::to_string(int(vmap_ptr[4*i + 1])) 
        //     + ", u=" + std::to_string(int(vmap_ptr[4*i + 2])) + ", v=" + std::to_string(int(vmap_ptr[4*i + 3]))).c_str());
        obs_for_feature[k].push_back(int(vmap_ptr[4*i + 1]));
        obs_for_feature[k].push_back(int(vmap_ptr[4*i + 2]));
        obs_for_feature[k].push_back(int(vmap_ptr[4*i + 3]));
        if (vmap_ptr[4*i + 1] > max_img_id){
            max_img_id = int(vmap_ptr[4*i + 1]);
        }
    }
    py::print(std::string("Composing obs. for points in 3D ... 100 proc").c_str());

    py::print(std::string("Num. of images: " + std::to_string(max_img_id)).c_str());
    std::map<std::string, int> images_obs[max_img_id+1];
    int images_obs_max[max_img_id+1] = { 0 };
    proc = 0;
    for (int i = 0; i < num_visibility_map_records; ++i){
        if (proc < int((double(i) / double(num_visibility_map_records))*100)){
            proc = int((double(i) / double(num_visibility_map_records))*100);
            py::print(std::string("Composing unique obs. ids ... " + std::to_string(proc) + " proc").c_str());
        }
        int img_id = int(vmap_ptr[4*i + 1]);
        images_obs[img_id][get_obs_hash(int(vmap_ptr[4*i+2]),int(vmap_ptr[4*i+3]))] = images_obs_max[img_id];
        images_obs_max[img_id] = images_obs_max[img_id] + 1;
    }
    py::print(std::string("Composing unique obs. ids ... 100 proc").c_str());
    

    py::print(std::string("Print the landmarks and observations to string.").c_str());
    std::stringstream ss;
    ss << "[";
    for (int i = 0; i < num_xyz; ++i){
        Landmark pt3D(i, rgb_ptr + 3*i, xyz_ptr + 3*i);
        std::vector<int> obs_array = obs_for_feature[i];
        if (int(obs_array.size()/3) > 1){
            for (int j = 0; j < int(obs_array.size()/3); ++j){
                int img_id = obs_array[j*3];
                int u = obs_array[j*3 + 1];
                int v =  obs_array[j*3 + 2];
                int fid = images_obs[img_id][get_obs_hash(u,v)];
                Observation obs(img_id, fid, u, v);
                pt3D.observations.push_back(obs);
            }
            ss << pt3D;
            if (i < (num_xyz - 1)){
                ss << ",";
            }
        }
    }
    ss << "]";
    py::print(std::string("Print the landmarks and observations to string. [done]").c_str());

    // output
    return ss.str();
}


PYBIND11_MODULE(MeshroomCpp, m) {
    m.doc() = "pybind11 MeshroomCpp plugin"; // optional module docstring
    m.def("encode_structure", &encode_structure, py::return_value_policy::move);
}