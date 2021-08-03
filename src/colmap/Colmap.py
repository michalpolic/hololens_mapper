from src.utils.UtilsSingularity import UtilsSingularity

class Colmap():

    def __init__(self, colmap_sif):
        """Init colmap object to run predefined commands"""
        self._colmap_sif = colmap_sif

    def extract_features(self, database_path, image_path):
        self._colmap_sif.command_dict("colmap feature_extractor", 
            {"database_path": database_path, 
            "image_path": image_path,
            "ImageReader.camera_model": "RADIAL",
            "ImageReader.single_camera": 1
            })

    def exhaustive_matcher(self, database_path):
        self._colmap_sif.command_dict("colmap exhaustive_matcher", 
            {"database_path": database_path})

    def mapper(self, database_path, image_path, output_path):
        self._colmap_sif.command_dict("colmap mapper", 
            {"database_path": database_path, 
            "image_path": image_path,
            "output_path": output_path
            })