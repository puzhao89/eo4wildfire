
import os, sys, logging
from datetime import datetime

def setup_default_logging(log_path, string = 'logs', default_level=logging.INFO,
                         format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s"):
   output_dir = os.path.join(log_path)

   os.makedirs(output_dir, exist_ok=True)
 
   logger = logging.getLogger(string)
 
   def time_str(fmt=None):
       if fmt is None:
           fmt = '%Y-%m-%d_%H%M%S'
       return datetime.today().strftime(fmt)
 
   logging.basicConfig(  # unlike the root logger, a custom logger can’t be configured using basicConfig()
       filename=os.path.join(output_dir, f'{time_str()}.log'),
       format=format,
       datefmt="%m/%d/%Y %H:%M:%S",
       level=default_level)
 
   # print
   # file_handler = logging.FileHandler(filename=os.path.join(output_dir, f'{time_str()}.log'), mode='a')
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setLevel(default_level)
   console_handler.setFormatter(logging.Formatter(format))
   # logger.addHandler(file_handler)
   logger.addHandler(console_handler)
 
   return logger
