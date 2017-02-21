#!/bin/bash
env_name=${1%/}
conda create --name $env_name --clone base;
source activate $env_name
pip install -r $2;