"""hubmap_kaggle dataset."""

import os
import io
from glob import glob

import numpy as np

import tensorflow_datasets as tfds

_DESCRIPTION = """
# TFDS for HuBMAP dataset in `kaggle`.
This dataset is built of the data processed by `iafoss` and `joshi98kishan`.
Image shapes:
  Train: 256/512/1024
  Test: 256
"""

_CITATION = """
"""

_TRAIN_DATA_REF_PREFIX = 'iafoss/hubmap'
_TEST_DATA_REF = 'joshi98kishan/hubmap-256x256-test-data'


class HubmapKaggleConfig(tfds.core.BuilderConfig):
  """BuilderConfig for Hubmap Kaggle."""

  def __init__(self, size, **kwargs):
    super(HubmapKaggleConfig, self).__init__(
      version=tfds.core.Version('1.0.0'), **kwargs)
    self.size = size


def _make_builder_configs():
  """Return BuilderConfigs."""
  configs = []
  for size in [256, 512, 1024]:
    configs.append(
      HubmapKaggleConfig(
        name='%dx%d' % (size, size),
        size=size,
        description=f"Training images cropped to {size}x{size}"
      ),
    )
  return configs


class HubmapKaggle(tfds.core.GeneratorBasedBuilder):
  """DatasetBuilder for hubmap_kaggle dataset."""

  VERSION = tfds.core.Version('1.0.0')
  BUILDER_CONFIGS = _make_builder_configs()

  def _info(self) -> tfds.core.DatasetInfo:
    """Returns the dataset metadata."""
    size = self.builder_config.size
    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            'image': tfds.features.Image(
                      shape=(None, None, 3), encoding_format='png'),
            'mask': tfds.features.Image(
                      shape=(None, None, 1), encoding_format='png'), 
            'id': tfds.features.Text(),
        }),
        supervised_keys=('image', 'mask'),  # Set to `None` to disable
        homepage='https://kaggle/datasets/',
        citation=_CITATION,
    )

  def _split_generators(self, dl_manager: tfds.download.DownloadManager):
    """Returns SplitGenerators."""

    size = self.builder_config.size
    train_path = dl_manager.download_kaggle_data(
                    _TRAIN_DATA_REF_PREFIX + f'-{size}x{size}')
    test_path = dl_manager.download_kaggle_data(_TEST_DATA_REF)

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
              'path': train_path,
              'split': 'train',
            },
        ),
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={
              'path': test_path,
              'split': 'test',
            },
        ),
    ]


  def _generate_examples(self, path, split):
    """Yields examples."""
    def _get_fname(path):
      basename = os.path.basename(path)
      fname = basename.split(os.path.sep)[0]
      return fname

    if split == 'train':
      image_paths = os.path.join(path, 'train', '*.png')
      image_paths = glob(image_paths)
      mask_paths = [path.replace('train', 'masks') for path in image_paths]
    elif split == 'test':
      image_paths = os.path.join(path, '*.png')
      image_paths = glob(image_paths)
      mask_paths = None

    n = len(image_paths)
    for i in range(n):
      image = open(image_paths[i], 'rb') 
      mask = (open(mask_paths[i], 'rb') if mask_paths is not None
                else np.ones((256, 256, 1), dtype=np.uint8))

      fname = _get_fname(image_paths[i])
      record = {
        'id': fname,
        'image': image,
        'mask': mask,
      }
      yield fname, record

    

