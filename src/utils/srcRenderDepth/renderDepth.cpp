#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <string.h> 
#include <sstream> 
#include <vector>
#include <cmath>
#include <cstdint>

namespace py = pybind11;
template<typename T>
using c_arr = py::array_t<T, py::array::c_style>;

inline void applyKernel(double* img, int w, int h, int uv0, int uv1, int r, double val) {
    for (int i = -r; i <= +r; i++) {
        for (int j = -r; j <= +r; j++) {
            if (i + uv0 < 0 || j + uv1 < 0 || i + uv0 >= w || j + uv1 >= h || i*i + j*j > r*r)
                continue;
            img[w * (j + uv1) + (i + uv0)] = val;
        }
    }
}

inline void applyKernelRGB(
    uint8_t* img, int w, int h, int uv0, int uv1, int radius, uint8_t r, uint8_t g, uint8_t b) {
    for (int i = -radius; i <= +radius; ++i) {
        for (int j = -radius; j <= +radius; ++j) {
            if (i + uv0 < 0 || j + uv1 < 0 || i + uv0 >= w || j + uv1 >= h || i*i + j*j > radius*radius)
                continue;
            const auto base_index = 3 * (w * (j + uv1) + (i + uv0));
            img[base_index] = r;
            img[base_index + 1] = g;
            img[base_index + 2] = b;
        }
    }
}

inline py::array_t<double> render(int img_height, int img_width, int uv_length, int t_length,
    py::array_t<double> uv, py::array_t<double> d, py::array_t<double> t) {

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
    return img.reshape({img_height, img_width});
}

inline py::array_t<uint8_t> render_image(
    int img_height,
    int img_width,
    const c_arr<double> &uv,
    const c_arr<uint16_t> &radii,
    const c_arr<uint8_t> &rgb) {

    // input
    auto uvbuf = uv.request();
    int uv_length = uvbuf.shape[1];
    const auto uv_ptr = (const double *) uvbuf.ptr;
    const auto radii_ptr = (const uint16_t *) radii.request().ptr;
    const auto color_ptr = (const uint8_t *) rgb.request().ptr;

    // rgb output
    py::array_t<uint8_t> img(3 * img_height * img_width);
    auto imgptr = (uint8_t *)img.request().ptr;

    // zero img out
    for (int i = 0; i < 3 * img_height * img_width; ++i){
        imgptr[i] = 0;
    }

    // for each point render its projection with radius
    // defined according its distance to camera center
    for (int i = 0; i < uv_length; i++) {
        applyKernelRGB(
            imgptr,
            img_width, img_height,
            int(uv_ptr[i]), int(uv_ptr[i + uv_length]),
            radii_ptr[i],
            color_ptr[i], color_ptr[i + uv_length], color_ptr[i + 2 * uv_length]
        );
    }

    // save the output
    return img.reshape({img_height, img_width, 3});
}


inline py::array_t<bool> is_visible(int img_height, int img_width, py::array_t<double, py::array::c_style> uv){

    // input
    auto uvbuf = uv.request();
    auto uvptr = (double *) uvbuf.ptr;
    auto uv_length = uvbuf.shape[1];

    // output
    py::array_t<bool> visible(uv_length);
    auto visiblebuf = visible.request();
    auto visibleptr = (bool *) visiblebuf.ptr;

    // set zeros to img
    for (int i = 0; i < uv_length; ++i){
        if (uvptr[i] > 0 & uvptr[i + uv_length] > 0 & uvptr[i] < img_width & uvptr[i + uv_length] < img_height){
            visibleptr[i] = 1;
        } else{
            visibleptr[i] = 0;
        }
    }

    // save the output
    return visible;
}

inline py::array_t<double> compose_visibility(int img_id, int width, int uv_length, py::array_t<double> uv,
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
    m.def("render_image", &render_image, py::return_value_policy::move);
    m.def("is_visible", &is_visible, py::return_value_policy::move);
    m.def("compose_visibility", &compose_visibility, py::return_value_policy::move);
}