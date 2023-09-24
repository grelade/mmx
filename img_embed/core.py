import numpy as np
import mediapipe as mp

model_path = 'mobilenet_v3_small_075_224_embedder.tflite'

BaseOptions = mp.tasks.BaseOptions
ImageEmbedder = mp.tasks.vision.ImageEmbedder
ImageEmbedderOptions = mp.tasks.vision.ImageEmbedderOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = ImageEmbedderOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    quantize=False,
    running_mode=VisionRunningMode.IMAGE)

class embedder:

    def __init__(self):

        self.model_name = None
        self.model = None

    def load_model(self,model_name: str):
        if model_name != self.model_name:
            self.model = ImageEmbedder.create_from_options(options)
            self.model_name = model_name

    def embed(self,mp_image) -> np.ndarray:
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=mp_image)
        embedding_result = self.model.embed(img)
        return embedding_result.embeddings[0].embedding

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.model.close()


