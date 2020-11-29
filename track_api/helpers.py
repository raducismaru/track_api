import yaml


class ConfigParser:
    def __init__(self, yml_file):
        with open(yml_file, 'r') as cfg_file:
            cfg = yaml.load(cfg_file, yaml.SafeLoader)
        for key in cfg:
            setattr(self, key, cfg[key])
