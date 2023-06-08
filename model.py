import os
import tensorflow as tf
from research.object_detection.utils import label_map_util
from research.object_detection.utils import visualization_utils as viz_utils
from research.object_detection.builders import model_builder
from research.object_detection.utils import config_util

import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches

CUSTOM_MODEL_NAME = 'my_faster_rcnn'
# PRETRAINED_MODEL_NAME = 'faster_rcnn_resnet101_v1_640x640_coco17_tpu-8'
# PRETRAINED_MODEL_URL = 'http://download.tensorflow.org/models/research.object_detection/tf2/20200711/faster_rcnn_resnet101_v1_640x640_coco17_tpu-8.tar.gz'
TF_RECORD_SCRIPT_NAME = 'generate_tfrecord.py'
LABEL_MAP_NAME = 'label_map.pbtxt'

paths = {
    'WORKSPACE_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace'),
    'SCRIPTS_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'scripts'),
    'APIMODEL_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'models'),
    'ANNOTATION_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'annotations'),
    'IMAGE_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'images'),
    'MODEL_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'models'),
    'PRETRAINED_MODEL_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'pre-trained-models'),
    'CHECKPOINT_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME),
    'OUTPUT_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME, 'export'),
    'TFJS_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME, 'tfjsexport'),
    'TFLITE_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME, 'tfliteexport'),
    'PROTOC_PATH': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'protoc')
}

files = {
    'PIPELINE_CONFIG': os.path.join('D:\semesters\\bachelor thesis\TFOD\Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME, 'pipeline.config'),
    'TF_RECORD_SCRIPT': os.path.join(paths['SCRIPTS_PATH'], TF_RECORD_SCRIPT_NAME),
    'LABELMAP': os.path.join(paths['ANNOTATION_PATH'], LABEL_MAP_NAME)
}

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(files['PIPELINE_CONFIG'])
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(paths['CHECKPOINT_PATH'], 'ckpt-11')).expect_partial()


@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


category_index = label_map_util.create_category_index_from_labelmap(files['LABELMAP'])
# IMAGE_PATH = os.path.join(paths['IMAGE_PATH'], 'test', 'asdfe.PNG')


def load(IMAGE_PATH):
    global image
    table_coords = []

    img = cv2.imread(IMAGE_PATH)
    image_np = np.array(img)

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
    # print(detections)

    label_id_offset = 1
    image_np_with_detections = image_np.copy()

    fig, ax = plt.subplots()
    ax.imshow(img)

    detection_boxes = detections['detection_boxes']
    scores = detections['detection_scores']
    for i in range(len(detection_boxes)):
        box = detection_boxes[i]
        score = scores[i]

        height, width, channels = img.shape
        scaled_boxes = box * np.array([height, width, height, width])
        scaled_boxes = scaled_boxes.astype(np.int32)
        ymin, xmin, ymax, xmax = np.transpose(scaled_boxes)

        if score >= 0.95:
            start_point = (xmin, ymin)
            end_point = (xmax, ymax)
            table_coords.append([start_point, end_point])


    # print(table_coords)
    return table_coords
