# EO4Wildfire Project

Please follow this notebook tutorial (Google Drive + colab): <br>

[main_eo4wildfire_4_colab.ipynb](https://colab.research.google.com/drive/1-XxcVGYCFDXUsJEPlnuJTeLNnP1OHHWW?usp=sharing)

After cloning this project, go to the project folder and open the script "main_eo4wildfire_4_colab.ipynb" with colab, then config GPU for this notebook script: File -> Notebook settings -> Hardware accelerator -> GPU. 

Or clone this project to your local machine:
```
git clone https://github.com/puzhao89/eo4wildfire.git
```
## **eo4wildfire** <br>
++| Data ([Google Drive])(https://drive.google.com/drive/folders/63ujMrEMBTIsv-OcbvzTXq_GI_EZ24FL?usp=sharing)<br>

------| Historical_Wildfire_Dataset (For offline model training) <br>
----------| BC_SAR4Wildfire_Dataset <br>
----------| Global_SAR4Wildfire_Dataset <br>
------| Temporal_Progression_Data (For on-the-fly and evaluating progression) <br>
----------| BC2018R91947_Progression_Data_20m <br>
---------------| A0_Opt_RGB (Optical RGB: R=SWIR2, G=NIR, B=SWIR1) <br>
---------------| A0_SAR_RGB (SAR RGB: R=kCR, G=kVH, B=kVV) <br>
---------------| A1_SARREF (SAR-based Pseudo Reference Masks) <br>
---------------| A2_OptSAR (OptSAR: Improved SARREF with OptREF)<br>
---------------| A3_OptREF (Optical Pseudo Reference Masks) <br>
---------------| A4_OptGTM (Optical Ground Truth Masks)<br>
----------| BC2018R92033_Progression_Data_20m <br>
----------| FraserIsland_Progression_Data_20m <br>
----------| CAL_Creek_Progression_Data_20m <br>
++| outputs/ <br>
------| logs/ <br>
------| Sampled_Patches/ <br>
------| Experiments_Fly/ <br>
------| Experiments_Offline/ <br>
++| config/ <br>
++| datasets/ <br>
++| evaluation/ <br>
++| models/ <br>
++| preprocessing/ <br>
++| main_eo4wildfire_4_colab.ipynb <br>