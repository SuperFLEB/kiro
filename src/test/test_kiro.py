from . import pkg

__package__ = pkg()

import unittest
import bpy
from os import path
from ..lib import kiro
from ..lib import types

test_images_path = path.join(path.dirname(__file__), "testdata")
ti_filenames = ["image1.png", "image2.png"]
ti_paths = [path.join(test_images_path, fn) for fn in ti_filenames]
tj_paths = [path.join(test_images_path, fn[0:-4] + ".kiro.json") for fn in ti_filenames]
ti_ki_metas = [types.KiroImageMeta(name=fn, name_full=fn, image_path=path.join(test_images_path, fn),
                                   json_path=path.join(test_images_path, fn[:-4] + ".kiro.json"))
               for fn in ti_filenames]

KiroImageMeta = types.KiroImageMeta


class KiroImageTest(unittest.TestCase):
    def setUp(self) -> None:
        kiro._test_clear_caches()
        for img in bpy.data.images:
            if img.filepath_raw in ti_paths:
                bpy.data.images.remove(img)

    def test_infer_kirofile_from_embedded_image(self):
        bpy.data.images.load(ti_paths[0])
        bpy.data.images.load(ti_paths[1])
        kiro_images = kiro.kiro_images(True)
        kiro_json_paths = [kim.json_path for kim in kiro_images]
        self.assertListEqual(kiro_json_paths, tj_paths)

    def test_infer_packed_kirofile(self):
        self.skipTest("Not implemented yet")
