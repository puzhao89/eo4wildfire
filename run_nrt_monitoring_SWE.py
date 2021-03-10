import torch
from easydict import EasyDict as edict
from datasets.data_samping import DataSampler, NRT_DataSampler
from pathlib import Path
from prettyprinter import pprint
from imageio import imread, imsave
import os, json

from utils.setup_logs import setup_default_logging
logger = setup_default_logging("./outputs/logs", string='on-the-fly')

def run_cfg(fireEvent="BC2018R91947", beta=0, ref_mode="SARREF"):

    project_dir = Path(os.getcwd())
    cfg = edict(
        project_dir = str(project_dir),
        # data_folder = str(project_dir / "BC_Wildfire_Data"),
        nrt_data_folder = str(project_dir / f"Data/Temporal_Progressions_Data/{fireEvent}_Progression_Data_20m"),

        # PNG
        input_folder = "A0_SAR_RGB", 
        transfer_folder = "A0_SAR_RGB",

        # sampling config
        patchsize = 64,
        num_patch_per_image = 500, #500
        train_val_split_rate = 0.7,
        random_state = 42,

        # model config
        ARCH = 'UNet', 
        ENCODER = 'resnet18', # 'mobilenet_v2'
        learning_rate = 1e-5,
        weight_decay = 1e-4,
        BATCH_SIZE = 32, # 32,

        max_score = 0, # IoU
        max_epoch = 50,
        size_of_train = 3072, #3072,

        # loss
        gamma = 1, # dice
        alpha = 0.5, # focal
        beta = beta, # tv

        ref_mode = 'SARREF', #'SARREF', 'OptSAR', 'OptREF'
        
        ENCODER_WEIGHTS = 'imagenet',
        ACTIVATION = 'sigmoid', # could be None for logits or 'softmax2d' for multicalss segmentation

        CLASSES = ['fire'],
        DEVICE = 'cuda',
        verbose = True,
    )

    """ Data Sampling """
    # data_sampler = DataSampler(cfg)
    data_sampler = NRT_DataSampler(cfg)
    print("data_sampler")
    data_sampler()
    cfg.data_sampler = data_sampler

    cfg.ref_mode = ref_mode
    pprint(cfg)

    """ Model Training """
    from models.seg_model_nrt import SegModel
    cfg.data_sampler = data_sampler

    seg_model = SegModel(cfg)
    cfg.modelPath = str(seg_model.savePath)

    """ Save Configuration before run """
    cfg_file = Path(cfg.modelPath) / 'config.json'
    with open(str(cfg_file), 'w') as fp:
        if 'data_sampler' in cfg.keys(): del cfg['data_sampler']
        json.dump(cfg, fp)

    seg_model.run_nrt_experiment()


if __name__ == "__main__":

    for fireEvent in ["SE2018LjusdalsV1", "SE2018Ljusdals", "SE2018LillasenV1", "SE2018TrangsletV1", "SE2018Storbrattan"]: #, "elephantHill", "BC2018R92033", "BC2018R91947"
        for ref_mode in ["OptSAR"]:
            # run_cfg(fireEvent=fireEvent, beta=0, ref_mode=ref_mode)
            run_cfg(fireEvent=fireEvent, beta=2e-5, ref_mode=ref_mode)
            