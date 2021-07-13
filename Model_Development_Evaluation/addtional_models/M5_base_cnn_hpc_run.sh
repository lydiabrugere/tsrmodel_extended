#!/bin/sh
echo "Loading modules to run CNN models..."
#module load python/3.6.6
#virtualenv $HOME/python/3.6.6
source $HOME/python/3.6.6/bin/activate
echo "Running script..."
/home/lfeng/python/3.6.6/bin/python3.6 /home/scratch/lfeng/machine_learning/M5_base_cnn.py