import sys
# sys.path.append('..')
from SeaM_main.src.global_config import GlobalConfig


def load_config():
    config = Config()
    return config


class Config(GlobalConfig):
    def __init__(self):
        super().__init__()
        self.project_data_save_dir = f'{self.data_dir}/multi_class_classification'
