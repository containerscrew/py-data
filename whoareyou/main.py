import json
import tensorflow as tf
from deepface import DeepFace

tf.keras.config.disable_interactive_logging()


models = [
  "VGG-Face", 
  "Facenet", 
  "Facenet512", 
  "OpenFace", 
  "DeepFace", 
  "DeepID", 
  "ArcFace", 
  "Dlib", 
  "SFace",
  "GhostFaceNet",
]

result = DeepFace.verify(
    img1_path = "ex1.jpg",
    img2_path = "ex2.jpg",
)

data =  json.dumps(result, indent=4)
print(data)