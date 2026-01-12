import numpy as np

def extract_landmarks(hand_landmarks):
    # hand_landmarks is a list of NormalizedLandmark objects
    return np.array([
        [lm.x, lm.y, lm.z]
        for lm in hand_landmarks
    ])
