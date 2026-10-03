import cv2


class LivenessDetector:

    def __init__(self):

        self.eye_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_eye_tree_eyeglasses.xml"
        )

        self.previous_eye_count = 0
        self.blink_detected = False

    def check_liveness(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        eyes = self.eye_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )

        current_eye_count = len(eyes)

        # Eyes open -> eyes closed
        if (
            self.previous_eye_count > 0
            and current_eye_count == 0
        ):
            self.blink_detected = True

        self.previous_eye_count = current_eye_count

        return self.blink_detected

    def reset(self):

        self.previous_eye_count = 0
        self.blink_detected = False