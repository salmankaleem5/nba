import os
import platform

if "Windows" in platform.platform():
    pass
elif "Darwin" in platform.platform():
    data_dir = '/Users/patrick/data/nba/'
else:
    data_dir = '/home/patrick/data/nba/'


def file_check(file_path):
    split_path = file_path.split('/')
    current_path = ''
    for p in range(0, len(split_path) - 1):
        current_path += split_path[p] + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
    return os.path.isfile(file_path)