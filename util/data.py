import os
import platform


wd = os.getcwd()

if 'Windows' in platform.platform():
    split = '\\'

else:
    split = '/'

data_dir = '/'.join(
    wd.split(split) + ['data']
)


def file_check(file_path):
    split_path = file_path.split('/')
    current_path = '/'.join(split_path[:-1])

    if not os.path.exists(current_path):
        os.makedirs(current_path)

    return os.path.isfile(file_path)
