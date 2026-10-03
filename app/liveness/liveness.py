import cv2


class LivenessDetector:

    def __init__(self):

        self.eye_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_eye_tree_eyeglasses.xml"
        )

        if self.eye_detector.empty():
            raise RuntimeError(
                "Could not load Haar eye detector."
            )

        self.previous_eye_count = 0
        self.blink_detected = False

    # ========================================================
    # CHECK LIVENESS
    # ========================================================

    def check_liveness(self, frame):

        if frame is None:
            return False

        try:

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            gray = cv2.equalizeHist(gray)

            eyes = self.eye_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(20, 20)
            )

            current_eye_count = len(eyes)

            # Eyes visible -> eyes disappear -> blink detected
            if (
                self.previous_eye_count > 0
                and current_eye_count == 0
            ):
                self.blink_detected = True

            self.previous_eye_count = current_eye_count

            return self.blink_detected

        except Exception as e:

            print("Liveness detection error:", e)
            return False

    # ========================================================
    # STATUS
    # ========================================================

    def is_live(self):
        return self.blink_detected

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.previous_eye_count = 0
        self.blink_detected = False