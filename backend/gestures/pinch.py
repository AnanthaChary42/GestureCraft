# Pinch gesture detection logic
from utils.math_utils import distance

THUMB_TIP = 4
INDEX_TIP = 8

class PinchGesture:
    def __init__(self, threshold=0.06):
        self.threshold = threshold

    def detect(self, landmarks):
        # landmarks is expected to be a numpy array of shape (N, 3)
        d = distance(landmarks[THUMB_TIP], landmarks[INDEX_TIP])
        return d < self.threshold
