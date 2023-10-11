import argparse
import tensorflow as tf
import tensorflow_hub as hub

parser = argparse.ArgumentParser(description='generate tflite embedding model from the tensorflow hub https://tfhub.dev',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-u', '--hub_url', type=str, default='https://tfhub.dev/google/imagenet/resnet_v1_50/feature_vector/5',
                    help='''url to model stored in tensorflow hub''')
parser.add_argument('-n', '--model_filename', type=str, default='resnet_v1_50.tflite',
                    help='''tflite model filename''')
parser.add_argument('-iw', '--image_width', type=int, default=224,
                    help='''input image width''')
parser.add_argument('-ih', '--image_height', type=int, default=224,
                    help='''input image height''')
parser.add_argument("-a","--auto_mode", help="infer and automatically fill out the metadata part",
                    action="store_true")

args = parser.parse_args()

hub_url = args.hub_url
model_filename = args.model_filename
image_width = args.image_width
image_height = args.image_height
auto_mode = args.auto_mode


hub.load(hub_url)
temp_path = hub.resolve(hub_url)
print(f'loading tensorflow hub model = {hub_url}')
print(f'forming tflite model file {model_filename}')

converter = tf.lite.TFLiteConverter.from_saved_model(temp_path)

converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,  # enable TensorFlow Lite ops.
    tf.lite.OpsSet.SELECT_TF_OPS,  # enable TensorFlow ops.
]

with open(model_filename, 'wb') as f:
  f.write(converter.convert())

print(f'forming model metadata for {model_filename}')
from tflite_support import flatbuffers
from tflite_support import metadata as _metadata
from tflite_support import metadata_schema_py_generated as _metadata_fb

# Creates model info.
model_meta = _metadata_fb.ModelMetadataT()

if auto_mode:
    model_meta.name = model_filename
else:
    default_name = 'a feature extractor'
    print(f'model_meta.name (default={default_name}):')
    name = input()
    model_meta.name = default_name if name == '' else name

if auto_mode:
    model_meta.description = hub_url
else:
    default_description = hub_url
    print(f'model_meta.description (default={default_description}):')
    description = input()
    model_meta.description = (default_description) if description == '' else (description)


model_meta.hub_url = hub_url
model_meta.version = "v1"
model_meta.author = "pretrained"
model_meta.license = ("Apache License. Version 2.0 "
                      "http://www.apache.org/licenses/LICENSE-2.0.")

# Creates input info.
input_meta = _metadata_fb.TensorMetadataT()

# Creates output info.
output_meta = _metadata_fb.TensorMetadataT()

input_meta.name = "image"

if auto_mode:
    pass
else:
    default_image_width = 224
    print(f'image_width (default={default_image_width}):')
    image_width = input()
    image_width = default_image_width if image_width == '' else int(image_width)

if auto_mode:
    pass
else:
    default_image_height = 224
    print(f'image_height (default={default_image_height}):')
    image_height = input()
    image_height = default_image_height if image_height == '' else int(image_height)

input_meta.description = (f'optimal_input_size=[{image_width},{image_height}]')

input_meta.content = _metadata_fb.ContentT()
input_meta.content.contentProperties = _metadata_fb.ImagePropertiesT()
input_meta.content.contentProperties.colorSpace = (
    _metadata_fb.ColorSpaceType.RGB)
input_meta.content.contentPropertiesType = (
    _metadata_fb.ContentProperties.ImageProperties)
input_normalization = _metadata_fb.ProcessUnitT()
input_normalization.optionsType = (
    _metadata_fb.ProcessUnitOptions.NormalizationOptions)
input_normalization.options = _metadata_fb.NormalizationOptionsT()
input_normalization.options.mean = [0.]
input_normalization.options.std = [255.]
input_meta.processUnits = [input_normalization]
input_stats = _metadata_fb.StatsT()
input_stats.max = [1.0]
input_stats.min = [0.0]
input_meta.stats = input_stats

# Creates output info.
output_meta = _metadata_fb.TensorMetadataT()
output_meta.name = "feature_vector"

n_features = tf.lite.Interpreter(model_filename).get_output_details()[0]['shape'][-1]
output_meta.description = f'n_features={n_features}'
# output_meta.content = _metadata_fb.ContentT()
# output_meta.content.content_properties = _metadata_fb.FeaturePropertiesT()
# output_meta.content.contentPropertiesType = (
#     _metadata_fb.ContentProperties.FeatureProperties)
# output_stats = _metadata_fb.StatsT()
# output_stats.max = [1.0]
# output_stats.min = [0.0]
# output_meta.stats = output_stats
# label_file = _metadata_fb.AssociatedFileT()
# label_file.name = os.path.basename("your_path_to_label_file")
# label_file.description = "Labels for objects that the model can recognize."
# label_file.type = _metadata_fb.AssociatedFileType.TENSOR_AXIS_LABELS
# output_meta.associatedFiles = [label_file]


# Creates subgraph info.
subgraph = _metadata_fb.SubGraphMetadataT()
subgraph.inputTensorMetadata = [input_meta]
subgraph.outputTensorMetadata = [output_meta]
model_meta.subgraphMetadata = [subgraph]

b = flatbuffers.Builder(0)
b.Finish(
    model_meta.Pack(b),
    _metadata.MetadataPopulator.METADATA_FILE_IDENTIFIER)
metadata_buf = b.Output()

print(f'appending metadata to model file {model_filename}')
populator = _metadata.MetadataPopulator.with_model_file(model_filename)
populator.load_metadata_buffer(metadata_buf)
# populator.load_associated_files(["your_path_to_label_file"])
populator.populate()

