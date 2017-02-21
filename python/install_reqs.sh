#!/bin/bash
conda create --name $1 --clone base;
source activate $folder
pip install $2;