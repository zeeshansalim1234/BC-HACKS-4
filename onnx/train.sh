#!/usr/bin/env bash

CONFIG=$1

python -m torch.distributed.launch --nproc_per_node=16 --master_port=3003 basicsr/train.py -opt $CONFIG --launcher pytorch