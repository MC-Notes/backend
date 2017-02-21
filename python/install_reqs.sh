#!/bin/bash

conda create --name $1 --clone base;
pip install $2;