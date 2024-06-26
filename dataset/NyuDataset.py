# coding=utf-8
import torch.utils.data as data
import sys
sys.path.append("..")
from imageio import imread
from path import Path
import numpy as np
import random
import time
from scipy.spatial.transform import Rotation as R
from skimage.transform import resize
import glob
import os
import natsort

def load_as_float(path):
    image = imread(path).astype(np.float32)[:, :, :3]
    return image

def load_as_npy(path):
    depth = np.load(path, dtype=np.float32)
    return depth


class DataSequence(data.Dataset):
    def __init__(self, root,
                 seed=None,
                 train=True,
                 shuffle=True,
                 transform=None,
                 scene=None,
                 image_width=640,
                 image_height=480):
        np.random.seed(seed)
        random.seed(seed)
        self.root = root
        self.transform = transform
        # self.train_path = './nyu_depth_raw/train/'
        # self.valid_path = './nyu_depth_raw/validation/'
        
        self.shuffle = shuffle
        self.crawl_folders(scene=scene)

    def crawl_folders(self, scene):
        samples = []

        path = os.path.join(self.root, scene)
        imgs = glob.glob(path+'/rgb/*')
        depth = glob.glob(f'{path}/depth/*.npy')

        imgs = natsort.natsorted(imgs, reverse=False)
        depth = natsort.natsorted(depth, reverse=False)
        
        for i in range(len(imgs)):
            samples.append([imgs[i], depth[i]])

        if self.shuffle:
            random.shuffle(samples)
        self.samples = samples

    def __getitem__(self, index):
        img_path, depth_path = self.samples[index]

        imgs = imread(img_path).astype(np.float32)
        depth = np.load(depth_path).astype(np.float32)
        depth = np.expand_dims(depth, axis=-1)

        if self.transform is not None:
            imgs, depth = self.transform(imgs, depth) # Imu (5, 11, 6) # intrinsic (3, 3)
        
        return imgs, depth

    def __len__(self):
        return len(self.samples)

if __name__ == "__main__":
    start_time = time.time()
    D = DataSequence(
        root='./nyu_depth_raw',
        shuffle=False,
        image_width=832,
        image_height=256,
        scene='validation'
    )
    img, depth = D[0]
    print('time used {}'.format(time.time()-start_time))
