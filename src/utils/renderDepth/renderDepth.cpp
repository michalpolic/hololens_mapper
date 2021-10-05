#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <string.h> 
#include <sstream> 
#include <vector>
#include <cmath>

namespace py = pybind11;

inline void applyKernel(double* img, int w, int h, int uv0, int uv1, int r, double val) {
    for (int i = -r; i <= +r; i++){
        for (int j = -r; j <= +r; j++){
            if (i + uv0 < 0 || j + uv1 < 0 || i + uv0 >= w || j + uv1 >= h || i*i + j*j > r*r)
                continue; 
            img[w * (j + uv1) + (i + uv0)] = val;
        }
    }
}

py::array_t<double> render(int img_height, int img_width, int uv_length, int t_length, 
    py::array_t<double> uv, py::array_t<double> d, py::array_t<double> t){

    // input
    auto uvbuf = uv.request();
    double *uvptr = (double *) uvbuf.ptr;
    auto dbuf = d.request();
    double *dptr = (double *) dbuf.ptr;
    auto tbuf = t.request();
    double *tptr = (double *) tbuf.ptr;
    
    // output
    py::array_t<double> img(img_height * img_width);
    auto imgbuf = img.request();
    double *imgptr = (double *) imgbuf.ptr;

    // // print
    // std::stringstream ss;
    // ss << "img[" << img_width << "][" << img_height << "]";
    // py::print(ss.str().c_str());
    
    // ss.str(std::string());
    // ss << "uv[" << uv_length << "]:" << uvptr[0] << " " << uvptr[uv_length] << " " << uvptr[1] << " " << uvptr[uv_length+1] << "... ";
    // py::print(ss.str().c_str());

    // ss.str(std::string());
    // ss << "d[" << uv_length << "]:" << dptr[0] << " " << dptr[1];
    // py::print(ss.str().c_str());

    // ss.str(std::string());
    // ss << "t[" << t_length << "]:" << tptr[0] << " " << tptr[t_length] << " " << tptr[1] << " " << tptr[t_length+1] << " " << tptr[2] << " " << tptr[t_length+2] << " ... ";
    // py::print(ss.str().c_str());


    // set zeros to img
    for (int i = 0; i < img_height * img_width; ++i){
        imgptr[i] = 0;
    }


    // for each point render its projection with radius 
    // defined according its distance to camera center
    int m = 0;
    int r = (tptr[m + t_length] - 1) / 2;
    for (int i = 0; i < uv_length; i++) {
        while (dptr[i] < tptr[m]){
            m = m + 1;
            r = (tptr[m + t_length] - 1) / 2;
        }
        applyKernel(imgptr, img_width, img_height, int(uvptr[i]), int(uvptr[i + uv_length]), r, dptr[i]);
    }

    // save the output
    return img;
}


py::array_t<double> is_visible(int img_height, int img_width, int uv_length, py::array_t<double> uv){

    // input
    auto uvbuf = uv.request();
    double *uvptr = (double *) uvbuf.ptr;

    // output
    py::array_t<double> visible(uv_length);
    auto visiblebuf = visible.request();
    double *visibleptr = (double *) visiblebuf.ptr;

    // set zeros to img
    for (int i = 0; i < uv_length; ++i){
        if (uvptr[i] > 0 & uvptr[i + uv_length] > 0 & uvptr[i] < img_width & uvptr[i + uv_length] < img_height){
            visibleptr[i] = 1;
        }else{
            visibleptr[i] = 0;
        }
    }

    // save the output
    return visible;
}

py::array_t<double> get_ids(int n){

    // output
    py::array_t<double> ids(n);
    auto idsbuf = ids.request();
    double *idsptr = (double *) idsbuf.ptr;

    // set zeros to img
    for (int i = 0; i < n; ++i){
        idsptr[i] = i;
    }

    // save the output
    return ids;
}

py::array_t<double> compose_visibility(int img_id, int width, int uv_length, py::array_t<double> uv, 
    py::array_t<double> gtd, py::array_t<double> md, py::array_t<double> ptsids, double threshold){

    // input
    auto uvbuf = uv.request();
    double *uvptr = (double *) uvbuf.ptr;
    auto gtdbuf = gtd.request();
    double *gtdptr = (double *) gtdbuf.ptr;
    auto mdbuf = md.request();
    double *mdptr = (double *) mdbuf.ptr;
    auto ptsidsbuf = ptsids.request();
    double *ptsidsptr = (double *) ptsidsbuf.ptr;
    
    // compose the visibility information
    std::vector<double> visibility_xyz;
    for (int i = 0; i < uv_length; ++i){  
        const int u = int(uvptr[i]);
        const int v = int(uvptr[i + uv_length]);
        double diff = mdptr[width*v + u] - gtdptr[i];
        if ( std::sqrt(diff*diff) < threshold ){
            visibility_xyz.push_back(ptsidsptr[i]);
            visibility_xyz.push_back(img_id);
            visibility_xyz.push_back(u);
            visibility_xyz.push_back(v);
        }
    }

    // output
    const int N = visibility_xyz.size();
    py::array_t<double> out(N);
    auto outbuf = out.request();
    double *outptr = (double *) outbuf.ptr;
    
    for (int i = 0; i < N; ++i){
        outptr[i] = visibility_xyz[i];
    }
    return out;
}

PYBIND11_MODULE(renderDepth, m) {
    m.doc() = "pybind11 renderDepth plugin"; // optional module docstring
    m.def("render", &render, py::return_value_policy::move);
    m.def("is_visible", &is_visible, py::return_value_policy::move);
    m.def("get_ids", &get_ids, py::return_value_policy::move);
    m.def("compose_visibility", &compose_visibility, py::return_value_policy::move);
}