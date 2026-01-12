# Open palm gesture detection logic
from utils.math_utils import distance

PALM = 0
FINGERS = [8, 12, 16, 20]

class OpenPalmGesture:
    def __init__(self, threshold=0.15):
        self.threshold = threshold

    def detect(self, landmarks):
        for finger in FINGERS:
            if distance(landmarks[PALM], landmarks[finger]) < self.threshold:
                return False
        return True
