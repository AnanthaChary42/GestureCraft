from gestures.pinch import PinchGesture
from gestures.open_palm import OpenPalmGesture

class GestureManager:
    def __init__(self):
        self.pinch_detector = PinchGesture()
        self.palm_detector = OpenPalmGesture()
        
        self.current_state = "NONE"
        self.history = []
        self.history_length = 5  # Number of frames to confirm a gesture change

    def update(self, landmarks):
        """
        Updates the state based on new landmarks.
        Returns the current stable state.
        """
        # 1. Detect raw gesture for this frame
        detected = "NONE"
        if self.pinch_detector.detect(landmarks):
            detected = "PINCH"
        elif self.palm_detector.detect(landmarks):
            detected = "OPEN_PALM"
        
        # 2. Add to history
        self.history.append(detected)
        if len(self.history) > self.history_length:
            self.history.pop(0)

        # 3. Check for stable state (all frames in history must match)
        # If the history is consistent, update current state
        if all(x == detected for x in self.history):
            self.current_state = detected
        
        # Note: If history is mixed (e.g. ["PINCH", "PINCH", "NONE"]), 
        # we keep the OLD current_state until the buffer clears.
        
        return self.current_state
