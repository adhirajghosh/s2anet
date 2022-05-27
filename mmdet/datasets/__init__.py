from .builder import build_dataset
from .cityscapes import CityscapesDataset
from .coco import CocoDataset
from .custom import CustomDataset
from .dataset_wrappers import ConcatDataset, RepeatDataset
from .deepscoresv2 import DeepScoresV2Dataset
from .deepscoresv2_hybrid import DeepScoresV2Dataset_Hybrid
from .loader import DistributedGroupSampler, GroupSampler, build_dataloader
from .registry import DATASETS
from .voc import VOCDataset
from .wider_face import WIDERFaceDataset
from .xml_style import XMLDataset

from .hrsc2016 import HRSC2016Dataset
from .dota import DotaDataset

__all__ = [
    'CustomDataset', 'XMLDataset', 'CocoDataset', 'VOCDataset',
    'CityscapesDataset', 'GroupSampler', 'DistributedGroupSampler',
    'build_dataloader', 'ConcatDataset', 'RepeatDataset',
    'WIDERFaceDataset', 'DATASETS', 'build_dataset',
    'HRSC2016Dataset','DotaDataset','DeepScoresV2Dataset','DeepScoresV2Dataset_Hybrid',
]
