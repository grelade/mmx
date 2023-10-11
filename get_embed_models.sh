#/bin/bash

echo "*** forming mobilenet_v3_small"
if [ -e "mmx/embed_model/mobilenet_v3_small.tflite" ]; then
  echo "model exists; skipping"
else
  python mmx/get_embed_model.py --hub_url https://tfhub.dev/google/imagenet/mobilenet_v3_small_100_224/feature_vector/5 --model_filename mmx/embed_model/mobilenet_v3_small.tflite --image_width 224 --image_height 224 --auto_mode
fi


echo "*** forming mobilenet_v3_large"
if [ -e "mmx/embed_model/mobilenet_v3_large.tflite" ]; then
  echo "model exists; skipping"
else
  python mmx/get_embed_model.py --hub_url https://tfhub.dev/google/imagenet/mobilenet_v3_large_100_224/feature_vector/5 --model_filename mmx/embed_model/mobilenet_v3_large.tflite --image_width 224 --image_height 224 --auto_mode
fi

echo "*** forming resnet_v1_50"
if [ -e "mmx/embed_model/resnet_v1_50.tflite" ]; then
  echo "model exists; skipping"
else
  python mmx/get_embed_model.py --hub_url https://tfhub.dev/google/imagenet/resnet_v1_50/feature_vector/5 --model_filename mmx/embed_model/resnet_v1_50.tflite --image_width 224 --image_height 224 --auto_mode
fi


echo "*** forming efficientnet_v2_m"
if [ -e "mmx/embed_model/efficientnet_v2_m.tflite" ]; then
  echo "model exists; skipping"
else
  python mmx/get_embed_model.py --hub_url https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_m/feature_vector/2 --model_filename mmx/embed_model/efficientnet_v2_m.tflite --image_width 480 --image_height 480 --auto_mode
fi

