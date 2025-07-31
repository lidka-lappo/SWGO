import configparser
import numpy as np

def load_general_config(filepath: str) -> dict:
    config = configparser.ConfigParser()
    config.read(filepath)

    def parse_range(raw: str):
        parts = list(map(float, raw.strip().split()))
        min_val, max_val, step = parts
        return np.arange(min_val, max_val, step)

    return {
        'general': {
            'n_of_rpcs': config.getint('general', 'n_of_rpcs'),
            'streamer_threshold': config.getint('general', 'streamer_threshold'),
            'strips': config.getint('general', 'strips'),
            'vprop': config.getfloat('general', 'vprop'),
            'pitch': config.getfloat('general', 'pitch'),
        },
        'ranges': {
            'QRange': parse_range(config['ranges']['QRange']),
            'XRange': parse_range(config['ranges']['XRange']),
            'YRange': parse_range(config['ranges']['YRange']),
        }
    }

def load_detector_mapping(filepath: str) -> dict:
    lookup = {}

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 5:
                raise ValueError(f"Expected 5 columns per line, got {len(parts)}: {line}")

            group, *channels = parts
            Q_F, Q_B, T_F, T_B = [
                list(map(int, ch.split())) if ch else [] for ch in channels
            ]

            lookup[group] = {
                'Q_F': Q_F,
                'Q_B': Q_B,
                'T_F': T_F,
                'T_B': T_B,
            }

    return lookup

def load_rpc_parameters(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()

    sections = {}
    current_section = None
    data = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') and line.endswith(']'):
            if current_section:
                sections[current_section] = data
            current_section = line.strip('[]')
            data = []
        else:
            values = list(map(float, line.split()))
            data.append(values)

    if current_section:
        sections[current_section] = data

    processed = {}
    for key, entries in sections.items():
        if key.endswith('offsets'):
            processed[key] = entries  # list of [x, y]
        elif key.endswith('ycenters'):
            processed[key] = entries[0]  # single list

    return processed
