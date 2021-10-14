from pathlib import Path
from typing import List
from numpy.random import choice
import numpy as np
from PIL.Image import Image, open as img_open
from PIL import Image as Image_m, ImageEnhance, ImageFilter

from ..registry import PIPELINES

SEAMLESS = 'seamless'
SEAMED = 'seamed'

@PIPELINES.register_module
class ScoreAug(object):
    """
    Augment scores with real-world blank pages
    """
    _blank_pages_path: Path
    _seamless_imgs: List[Image]
    _seamed_imgs: List[Image]

    def __init__(self, blank_pages_path, padding_length = 200):
        self._blank_pages_path = Path(blank_pages_path)
        assert self._blank_pages_path.exists(), "Path to blank pages must exist"
        assert self._blank_pages_path.is_dir(), "Path to blank pages must be a directory"
        self._seamless_imgs = self._load_images(self._blank_pages_path / SEAMLESS)
        self._seamed_imgs = self._load_images(self._blank_pages_path / SEAMED)
        self.padding_length = padding_length



    @staticmethod
    def _load_images(path: Path) -> List[Image]:
        assert path.exists(), f"Path to {path.name} blank pages must exist"
        assert path.is_dir(), f"Path to {path.name} blank pages must be a directory"
        return list(map(img_open, path.glob('*.png')))


    def __call__(self, results: dict):
        take_seamless = choice([True, False], p=[0.5, 0.5])
        if not take_seamless:
            bg_imgs = self._seamed_imgs
        else:
            bg_imgs = self._seamless_imgs

        # Random blank page background image
        bg_img: Image = choice(bg_imgs)
        shape = results['img_shape'][1::-1]
        bg_img = bg_img.resize(shape)

        # Random flips
        horiz_flip = choice([True, False], p=[0.5, 0.5])
        if horiz_flip:
            bg_img = bg_img.transpose(Image_m.FLIP_LEFT_RIGHT)
        vert_flip = choice([True, False], p=[0.5, 0.5])
        if vert_flip:
            bg_img = bg_img.transpose(Image_m.FLIP_TOP_BOTTOM)

        # maybe crop and resize
        crop_resize = choice([True, False], p=[0.5, 0.5])
        if crop_resize:
            crop_factor = np.random.uniform(low=0.25, high=0.85)
            crop_size = (crop_factor * np.array(shape)).astype(np.int32)
            max_topleft = np.array(shape) - crop_size
            top_left = np.random.uniform(low=[0, 0], high=max_topleft, size=2).astype(np.int32)
            bottom_right = top_left + crop_size
            bg_img = bg_img.crop(np.concatenate([top_left, bottom_right]))
            bg_img = bg_img.resize(shape)

        # Increase size if seamed
        if not (take_seamless or crop_resize):
            # compute new shape, resize background
            shape = tuple([x + self.padding_length for x in shape])
            bg_img = bg_img.resize(shape)

            # extend foreground
            img_extended = np.ones(shape[::-1] + (3,),dtype=np.uint8)*255
            half_pad = self.padding_length//2
            img_extended[half_pad:-half_pad,half_pad:-half_pad] = results['img']

            # shift bounding boxes
            results['ann_info']['bboxes'] = results['ann_info']['bboxes'] + half_pad
            results['gt_bboxes'] = results['gt_bboxes'] + half_pad

            # correct meta infos
            results['img_info']['width'] = shape[0]
            results['img_info']['height'] = shape[1]
            results['img_shape'] = shape[::-1]+(3,)

        # randomize bg brightness
        random_bg_brightness = choice([True, False], p=[0.5, 0.5])
        if random_bg_brightness or True:
            enhancer = ImageEnhance.Brightness(bg_img)
            bg_img = enhancer.enhance(np.random.uniform(0.8, 1.1))

        fg_img = Image_m.fromarray(results['img'])
        # high contrast contrast fg
        fg_high_contrast = choice([True, False], p=[0.2, 0.8])
        if fg_high_contrast or True:
            enhancer = ImageEnhance.Contrast(fg_img)
            fg_img = enhancer.enhance(5)

        fg_brightness = choice([True, False], p=[0.4, 0.6])
        if fg_brightness or True:
            fg_img = np.array(fg_img, dtype=np.uint32)
            fg_img = fg_img + np.random.uniform(30, 150)
            fg_img[fg_img > 255] = 255
            fg_img = Image_m.fromarray(fg_img.astype(np.uint8))


        fg_blur = choice([True, False], p=[0.4, 0.6])
        if fg_blur or True:
            fg_img = fg_img.filter(ImageFilter.GaussianBlur(radius=np.random.randint(1, 4)))


        # Merge
        results['img'] = np.minimum(fg_img, bg_img)
        # from matplotlib import pyplot as plt
        # plt.figure(figsize=(20, 30))
        # plt.imshow(results['img'], interpolation='nearest')
        # plt.show()

    def __repr__(self):
        return f'{self.__class__.__name__}(blank_pages_path={self._blank_pages_path})'
