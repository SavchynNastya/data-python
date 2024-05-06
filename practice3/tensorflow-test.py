import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import decode_predictions
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input
from tensorflow.keras.applications.densenet import DenseNet121
from typing import List, Tuple

class ObjectRecognizer:
    def __init__(self, model_name: str = 'densenet121') -> None:
        if model_name == 'inception_v3':
            self.model = InceptionV3(weights='imagenet')
        elif model_name == 'densenet121':
            self.model = DenseNet121(weights='imagenet')
        else:
            raise ValueError("Invalid model name. Supported models: 'inception_v3', 'densenet121'.")

    def recognize_object(self, img_path: str) -> List[Tuple[str, str, float]]:
        img_size = (299, 299) if self.model.name == 'inception_v3' else (224, 224)
        img = image.load_img(img_path, target_size=img_size)
        img_array = image.img_to_array(img)
        img_array = preprocess_input(img_array)
        img_array = tf.expand_dims(img_array, 0)

        predictions = self.model.predict(img_array)
        decoded_predictions = decode_predictions(predictions)[0]

        return decoded_predictions

if __name__ == "__main__":
    img_paths: List[str] = [
        'C:\\Users\\Anastasia\\KPI\\Python-data\\practice3\\kitty.jpg',
        'C:\\Users\\Anastasia\\KPI\\Python-data\\practice3\\dog.jpg',
    ]

    try:
        recognizer: ObjectRecognizer = ObjectRecognizer(model_name='inception_v3')
        for img_path in img_paths:
            recognized_objects: List[Tuple[str, str, float]] = recognizer.recognize_object(img_path)
            print("Top predictions:")
            for i, (imagenet_id, label, score) in enumerate(recognized_objects):
                print(f"{i + 1}. {label} ({score:.2f})")
    except Exception as e:
        print(f"Error: {str(e)}")
