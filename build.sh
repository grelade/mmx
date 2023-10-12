#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Usage: $0 [dev | prod] ..."
  exit 1
fi

if [ $# -ge 1 ]; then

  if [ ! -d "mmx/feat_extract_model" ]; then
    echo "creating mmx/feat_extract_model dir"
    mkdir mmx/feat_extract_model
  fi

  if [ ! -d "img" ]; then
    echo "creating local img folder"
    mkdir img
  fi

  # find efficientnet
  if [ ! -e "mongodb_url" ]; then
    echo "creating mongodb_url with mongodb address"
    echo "mongodb://localhost:27017" > mongodb_url
  fi

  # find efficientnet
  net_checksum="44a7f924be5ab2338392fe05672d47b9"
  model="mmx/feat_extract_model/efficientnet_v2_m.tflite"
  checksum=$(md5sum $model | awk '{print $1}')
  if [ -e "$model" ] && [ "$net_checksum" = "$checksum" ]; then
    # echo "efficientnet_v2_m exists"
    :
  else
    echo "creating efficientnet_v2_m feat_extract_model"
    python mmx/get_feat_extract_model.py --hub_url https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_m/feature_vector/2 --model_filename mmx/feat_extract_model/efficientnet_v2_m.tflite --image_width 480 --image_height 480 --auto_mode
  fi

  if [ "$1" = "dev" ]; then
    docker compose --env-file .env.dev -f compose-dev.yaml build
  elif [ "$1" = "prod" ]; then
    docker compose --env-file .env -f compose.yaml build
  fi
fi

