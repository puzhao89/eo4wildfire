
from easydict import EasyDict as edict
import tifffile as tiff
from pathlib import Path
import os, glob
from imageio import imread, imsave
import numpy as np
from tqdm import tqdm
from prettyprinter import pprint
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.image import extract_patches_2d
from astropy.visualization import PercentileInterval
interval_95 = PercentileInterval(95.0)

class DataSampler:
    def __init__(self, cfg):
        self.cfg = cfg

        self.data_folder = Path(cfg.data_folder)
        self.trainPath = self.data_folder #/ "Historical_Wildfire_Dataset" 
        self.dataPath = self.trainPath / cfg.input_folder
        # self.patchPath = self.data_folder / f"patch_samples_{cfg.num_patch_per_image}_perImg_Nov15"

        self.sampleFolder = Path(self.cfg.project_dir) / "outputs" / "Sampled_Patches"
        if not os.path.exists(self.sampleFolder): 
            os.mkdir(self.sampleFolder)
        self.firename = os.path.split(self.cfg.data_folder)[-1].split("_")[0]
        self.patchPath = self.sampleFolder / f"Off_{self.firename}_patchSamples_{cfg.num_patch_per_image}_perImg"

        self.train = edict()
        self.train.patchDir = self.patchPath / f'trainPatches_{self.cfg.patchsize}'
        self.train.maskDir_SAR = self.patchPath / f'trainMasks_SARREF_{self.cfg.patchsize}'
        self.train.maskDir_optSAR = self.patchPath / f'trainMasks_OptSAR_{self.cfg.patchsize}'
        self.train.maskDir_Opt = self.patchPath / f'trainMasks_OptREF_{self.cfg.patchsize}'

        self.val = edict()
        self.val.patchDir = self.patchPath / f'valPatches_{self.cfg.patchsize}'
        self.val.maskDir_SAR = self.patchPath / f'valMasks_SARREF_{self.cfg.patchsize}'
        self.val.maskDir_optSAR = self.patchPath / f'valMasks_OptSAR_{self.cfg.patchsize}'
        self.val.maskDir_Opt = self.patchPath / f'valMasks_OptREF_{self.cfg.patchsize}'

    
    def __call__(self):
        self.generate_training_samples()

    def sklearn_uniformSampling_trainValSplit_multiRef(self, filename):
        tifName = filename[:-4]
        if '.png' == filename[-4:]:
            img = imread(self.dataPath / f"{filename}")
        elif '.tif' == filename[-4:]:
            img = tiff.imread(self.dataPath / f"{filename}")
        else:
            pass

        SARREF = imread(glob.glob(str(self.trainPath / f"A1_SARREF" / f"{tifName}*.png"))[0]) / 255.0
        OptSAR = imread(glob.glob(str(self.trainPath / f"A2_OptSAR" / f"{tifName}*.png"))[0]) / 255.0

        opt_ref_url = glob.glob(str(self.trainPath / f"A4_OptGTM" / f"{tifName}*.png"))[0]
        print("opt_ref_url", opt_ref_url)
        OptREF = imread(opt_ref_url) / 255.0
        
        # print(f' ref: [{SARREF.min(), SARREF.max()}], ref shape: {SARREF.shape}, input shape: {img.shape}, optSAR shape: {OptSAR.shape}')


        if len(OptREF.shape) > 2: # add on Nov-24-2020, for handle with 3-channel ref
            SARREF = SARREF[:,:,0]
            OptSAR = OptSAR[:,:,0]
            OptREF = OptREF[:,:,0]

        kmap = np.nan_to_num(img, 0)
        stacked = np.concatenate((kmap, SARREF[..., np.newaxis], OptSAR[..., np.newaxis], OptREF[..., np.newaxis]), axis=2)
        stacked = np.nan_to_num(stacked, 0)
        
        patchsize = self.cfg.patchsize
        split = self.cfg.train_val_split_rate
        numPatch = self.cfg.num_patch_per_image
        random_state = self.cfg.random_state

        train_max_height = int(split*stacked.shape[0])
        # print("train_max_height", train_max_height, stacked.shape[0], patchsize)

        train = extract_patches_2d(stacked[:train_max_height, ], (patchsize, patchsize), int(split*numPatch), random_state)
        val = extract_patches_2d(stacked[train_max_height:, ], (patchsize, patchsize), int((1-split)*numPatch), random_state)
        
        if not os.path.exists(self.patchPath): os.mkdir(self.patchPath)

        """ SAVE training samples """
        if not os.path.exists(self.train.maskDir_optSAR/ f"{tifName}_{int(split*numPatch-1)}.png"): 
            if not os.path.exists(self.train.patchDir): os.mkdir(self.train.patchDir)
            if not os.path.exists(self.train.maskDir_SAR): os.mkdir(self.train.maskDir_SAR)
            if not os.path.exists(self.train.maskDir_optSAR): os.mkdir(self.train.maskDir_optSAR)
            if not os.path.exists(self.train.maskDir_Opt): os.mkdir(self.train.maskDir_Opt)

            if not os.path.exists(self.val.patchDir): os.mkdir(self.val.patchDir)
            if not os.path.exists(self.val.maskDir_SAR): os.mkdir(self.val.maskDir_SAR)
            if not os.path.exists(self.val.maskDir_optSAR): os.mkdir(self.val.maskDir_optSAR)
            if not os.path.exists(self.val.maskDir_Opt): os.mkdir(self.val.maskDir_Opt)

            for i in tqdm(range(0, train.shape[0])):
                imsave(self.train.patchDir / f"{tifName}_{i}.png", (interval_95(train[i,...,:3])*255).astype(np.uint8))
                imsave(self.train.maskDir_SAR / f"{tifName}_{i}.png", (train[i,...,-3:-2]*255).astype(np.uint8))
                imsave(self.train.maskDir_optSAR / f"{tifName}_{i}.png", (train[i,...,-2:-1]*255).astype(np.uint8))
                imsave(self.train.maskDir_Opt / f"{tifName}_{i}.png", (train[i,...,-1:]*255).astype(np.uint8))

            for i in tqdm(range(0, val.shape[0])):
                imsave(self.val.patchDir / f"{tifName}_{i}.png", (interval_95(val[i,...,:3])*255).astype(np.uint8))
                imsave(self.val.maskDir_SAR / f"{tifName}_{i}.png", (val[i,..., -3:-2]*255).astype(np.uint8))
                imsave(self.val.maskDir_optSAR / f"{tifName}_{i}.png", (val[i,..., -2:-1]*255).astype(np.uint8))
                imsave(self.val.maskDir_Opt / f"{tifName}_{i}.png", (val[i,..., -1:]*255).astype(np.uint8))


    def sklearn_uniformSampling_trainValSplit(self, filename):
        tifName = filename[:-4]
        if '.png' == filename[-4:]:
            img = imread(self.dataPath / f"{filename}")
        elif '.tif' == filename[-4:]:
            img = tiff.imread(self.dataPath / f"{filename}")
        else:
            pass

        SARREF = imread(glob.glob(str(self.trainPath / f"A1_SARREF" / f"{tifName}*.png"))[0]) / 255.0
        # print(f"SARREF: ", np.unique(SARREF))

        if len(SARREF.shape) > 2: # add on Nov-24-2020, for handle with 3-channel ref
            SARREF = SARREF[:,:,0]

        kmap = np.nan_to_num(img, 0)
        stacked = np.concatenate((kmap, SARREF[..., np.newaxis]), axis=2)
        stacked = np.nan_to_num(stacked, 0)
        
        patchsize = self.cfg.patchsize
        split = self.cfg.train_val_split_rate
        numPatch = self.cfg.num_patch_per_image
        random_state = self.cfg.random_state

        train_max_height = int(split*stacked.shape[0])
        # print("train_max_height", train_max_height, stacked.shape[0], patchsize)

        train = extract_patches_2d(stacked[:train_max_height, ], (patchsize, patchsize), int(split*numPatch), random_state)
        val = extract_patches_2d(stacked[train_max_height:, ], (patchsize, patchsize), int((1-split)*numPatch), random_state)
        
        if not os.path.exists(self.patchPath): os.mkdir(self.patchPath)

        """ SAVE training samples """
        if not os.path.exists(self.train.maskDir_SAR/ f"{tifName}_{int(split*numPatch-1)}.png"): 
            if not os.path.exists(self.train.patchDir): os.mkdir(self.train.patchDir)
            if not os.path.exists(self.train.maskDir_SAR): os.mkdir(self.train.maskDir_SAR)

            if not os.path.exists(self.val.patchDir): os.mkdir(self.val.patchDir)
            if not os.path.exists(self.val.maskDir_SAR): os.mkdir(self.val.maskDir_SAR)

            for i in tqdm(range(0, train.shape[0])):
                imsave(self.train.patchDir / f"{tifName}_{i}.png", (interval_95(train[i,...,:3])*255).astype(np.uint8))
                imsave(self.train.maskDir_SAR / f"{tifName}_{i}.png", (train[i,...,-1]*255).astype(np.uint8))
               
            for i in tqdm(range(0, val.shape[0])):
                imsave(self.val.patchDir / f"{tifName}_{i}.png", (interval_95(val[i,...,:3])*255).astype(np.uint8))
                imsave(self.val.maskDir_SAR / f"{tifName}_{i}.png", (val[i,..., -1]*255).astype(np.uint8))

    def generate_training_samples(self):
        for filename in os.listdir(self.dataPath):
            if ('.tif' in filename) or ('.png' in filename):
                print(f"\n ==> Sampling over {filename}")
                self.sklearn_uniformSampling_trainValSplit_multiRef(filename)
                # self.sklearn_uniformSampling_trainValSplit(filename)

""" Near Real-Time Data Sampling """
class NRT_DataSampler:
    def __init__(self, cfg):
        self.cfg = cfg

        self.data_folder = Path(cfg.nrt_data_folder)
        self.trainPath = self.data_folder #/ "A0_Progression_PNG" 
        self.dataPath = self.trainPath / cfg.input_folder

        self.sampleFolder = Path(self.cfg.project_dir) / "outputs" / "Sampled_Patches"
        if not os.path.exists(self.sampleFolder): 
            os.mkdir(self.sampleFolder)

        # self.patchPath = self.data_folder / f"patch_samples_{cfg.num_patch_per_image}_perImg_Nov15"
        self.firename = os.path.split(self.cfg.nrt_data_folder)[-1].split("_")[0]
        self.patchPath = self.sampleFolder / f"Fly_{self.firename}_patchSamples_{cfg.num_patch_per_image}_perImg"

        self.train = edict()
        self.train.patchDir = self.patchPath / f'trainPatches_{self.cfg.patchsize}'
        self.train.maskDir_SAR = self.patchPath / f'trainMasks_SARREF_{self.cfg.patchsize}'
        self.train.maskDir_optSAR = self.patchPath / f'trainMasks_OptSAR_{self.cfg.patchsize}'
        self.train.maskDir_Opt = self.patchPath / f'trainMasks_OptREF_{self.cfg.patchsize}'

        self.val = edict()
        self.val.patchDir = self.patchPath / f'valPatches_{self.cfg.patchsize}'
        self.val.maskDir_SAR = self.patchPath / f'valMasks_SARREF_{self.cfg.patchsize}'
        self.val.maskDir_optSAR = self.patchPath / f'valMasks_OptSAR_{self.cfg.patchsize}'
        self.val.maskDir_Opt = self.patchPath / f'valMasks_OptREF_{self.cfg.patchsize}'

    
    def __call__(self):
        self.generate_training_samples()

    def sklearn_uniformSampling_trainValSplit_multiRef(self, filename):
        tifName = filename[:-4]
        if '.png' == filename[-4:]:
            img = imread(self.dataPath / f"{filename}")
        elif '.tif' == filename[-4:]:
            img = tiff.imread(self.dataPath / f"{filename}")
        else:
            pass

        SARREF = imread(glob.glob(str(self.trainPath / f"A1_SARREF" / f"{tifName}*.png"))[0]) / 255.0
        OptSAR = imread(glob.glob(str(self.trainPath / f"A2_OptSAR" / f"{tifName}*.png"))[0]) / 255.0

        # opt_ref_url = glob.glob(str(self.trainPath / f"A4_OptGTM" / f"{tifName}*.png"))[0]
        # # print("opt_ref_url", opt_ref_url)
        # OptREF = imread(opt_ref_url) / 255.0
        # # print(f' ref: [{SARREF.min(), SARREF.max()}], ref shape: {SARREF.shape}, input shape: {img.shape}, optSAR shape: {OptSAR.shape}')

        if len(OptSAR.shape) > 2: # add on Nov-24-2020, for handle with 3-channel ref
            SARREF = SARREF[:,:,0]
            OptSAR = OptSAR[:,:,0]
            # OptREF = OptREF[:,:,0]

        kmap = np.nan_to_num(img, 0)
        stacked = np.concatenate((kmap, SARREF[..., np.newaxis], OptSAR[..., np.newaxis]), axis=2)
        stacked = np.nan_to_num(stacked, 0)
        
        patchsize = self.cfg.patchsize
        split = self.cfg.train_val_split_rate
        numPatch = self.cfg.num_patch_per_image
        random_state = self.cfg.random_state

        train_max_height = int(split*stacked.shape[0])
        # print("train_max_height", train_max_height, stacked.shape[0], patchsize)

        train = extract_patches_2d(stacked[:train_max_height, ], (patchsize, patchsize), int(split*numPatch), random_state)
        val = extract_patches_2d(stacked[train_max_height:, ], (patchsize, patchsize), int((1-split)*numPatch), random_state)
        
        if not os.path.exists(self.patchPath): os.mkdir(self.patchPath)

        """ SAVE training samples """
        if not os.path.exists(self.train.maskDir_optSAR/ f"{tifName}_{int(split*numPatch-1)}.png"): 
            if not os.path.exists(self.train.patchDir): os.mkdir(self.train.patchDir)
            if not os.path.exists(self.train.maskDir_SAR): os.mkdir(self.train.maskDir_SAR)
            if not os.path.exists(self.train.maskDir_optSAR): os.mkdir(self.train.maskDir_optSAR)
            # if not os.path.exists(self.train.maskDir_Opt): os.mkdir(self.train.maskDir_Opt)

            if not os.path.exists(self.val.patchDir): os.mkdir(self.val.patchDir)
            if not os.path.exists(self.val.maskDir_SAR): os.mkdir(self.val.maskDir_SAR)
            if not os.path.exists(self.val.maskDir_optSAR): os.mkdir(self.val.maskDir_optSAR)
            # if not os.path.exists(self.val.maskDir_Opt): os.mkdir(self.val.maskDir_Opt)

            for i in tqdm(range(0, train.shape[0])):
                imsave(self.train.patchDir / f"{tifName}_{i}.png", (interval_95(train[i,...,:3])*255).astype(np.uint8))
                imsave(self.train.maskDir_SAR / f"{tifName}_{i}.png", (train[i,...,3:4]*255).astype(np.uint8))
                imsave(self.train.maskDir_optSAR / f"{tifName}_{i}.png", (train[i,..., 4:5]*255).astype(np.uint8))
                # imsave(self.train.maskDir_Opt / f"{tifName}_{i}.png", (train[i,...,-1:]*255).astype(np.uint8))

            for i in tqdm(range(0, val.shape[0])):
                imsave(self.val.patchDir / f"{tifName}_{i}.png", (interval_95(val[i,...,:3])*255).astype(np.uint8))
                imsave(self.val.maskDir_SAR / f"{tifName}_{i}.png", (val[i,..., 3:4]*255).astype(np.uint8))
                imsave(self.val.maskDir_optSAR / f"{tifName}_{i}.png", (val[i,..., 4:5]*255).astype(np.uint8))
                # imsave(self.val.maskDir_Opt / f"{tifName}_{i}.png", (val[i,..., -1:]*255).astype(np.uint8))

    def sklearn_uniformSampling_trainValSplit(self, filename):
        tifName = filename[:-4]
        if '.png' == filename[-4:]:
            img = imread(self.dataPath / f"{filename}")
        elif '.tif' == filename[-4:]:
            img = tiff.imread(self.dataPath / f"{filename}")
        else:
            pass

        SARREF = imread(glob.glob(str(self.trainPath / f"A1_SARREF" / f"{tifName}*.png"))[0]) / 255.0
        # print(f"SARREF: ", np.unique(SARREF))

        if len(SARREF.shape) > 2: # add on Nov-24-2020, for handle with 3-channel ref
            SARREF = SARREF[:,:,0]

        kmap = np.nan_to_num(img, 0)
        stacked = np.concatenate((kmap, SARREF[..., np.newaxis]), axis=2)
        stacked = np.nan_to_num(stacked, 0)
        
        patchsize = self.cfg.patchsize
        split = self.cfg.train_val_split_rate
        numPatch = self.cfg.num_patch_per_image
        random_state = self.cfg.random_state

        train_max_height = int(split*stacked.shape[0])
        # print("train_max_height", train_max_height, stacked.shape[0], patchsize)

        train = extract_patches_2d(stacked[:train_max_height, ], (patchsize, patchsize), int(split*numPatch), random_state)
        val = extract_patches_2d(stacked[train_max_height:, ], (patchsize, patchsize), int((1-split)*numPatch), random_state)
        
        if not os.path.exists(self.patchPath): os.mkdir(self.patchPath)

        """ SAVE training samples """
        if not os.path.exists(self.train.maskDir_SAR/ f"{tifName}_{int(split*numPatch-1)}.png"): 
            if not os.path.exists(self.train.patchDir): os.mkdir(self.train.patchDir)
            if not os.path.exists(self.train.maskDir_SAR): os.mkdir(self.train.maskDir_SAR)

            if not os.path.exists(self.val.patchDir): os.mkdir(self.val.patchDir)
            if not os.path.exists(self.val.maskDir_SAR): os.mkdir(self.val.maskDir_SAR)

            for i in tqdm(range(0, train.shape[0])):
                imsave(self.train.patchDir / f"{tifName}_{i}.png", (interval_95(train[i,...,:3])*255).astype(np.uint8))
                imsave(self.train.maskDir_SAR / f"{tifName}_{i}.png", (train[i,...,-1]*255).astype(np.uint8))
               
            for i in tqdm(range(0, val.shape[0])):
                imsave(self.val.patchDir / f"{tifName}_{i}.png", (interval_95(val[i,...,:3])*255).astype(np.uint8))
                imsave(self.val.maskDir_SAR / f"{tifName}_{i}.png", (val[i,..., -1]*255).astype(np.uint8))

    def generate_training_samples(self):
        for filename in sorted(os.listdir(self.dataPath)):
            if ('.tif' in filename) or ('.png' in filename):
                print(f"\n ==> Sampling over {filename}")
                self.sklearn_uniformSampling_trainValSplit_multiRef(filename)
                # self.sklearn_uniformSampling_trainValSplit(filename)


# if __name__ == "__main__":

#     cfg = edict(

#             rootPath = Path("E:\PyProjects\PyTorch_TV_Transfer_Learning\data"),

#             patchsize = 256,
#             num_patch_per_image = 10,
#             train_val_split_rate = 0.7,
#             random_state = 42,

#         )

#     dataSampler = DataSampler(cfg)
#     dataSampler()
#     pprint(dataSampler.cfg)

    