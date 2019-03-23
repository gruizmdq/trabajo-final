#PATHS
MODEL_PATH = 'face_detection_model/'
MODEL_PROTOTXT = 'deploy.prototxt'
MODEL_PRE_TRAINEED = 'res10_300x300_ssd_iter_140000.caffemodel'

EMBEDDING_MODEL_PATH = "openface_nn4.small2.v1.t7"
RECOGNIZER_PATH = "output/recognizer.pickle"
LABEL_ENCODER_PATH = "output/le.pickle"

UNRECOGNIZED_FACES_PATH = 'unrecognized/'

CONFIDENCE_TO_ACCEPT_DETECTION = .90
CONFIDENCE_TO_ACCEPT_RECOGNITION = .80

SECONDS_BETWEEN_CAPTURE = 2
