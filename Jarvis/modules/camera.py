# ============================================================
# JARVIS - Camera Module
# ============================================================

import os
from datetime import datetime

import cv2

import config


class CameraModule:
    """Webcam, photo capture, and face detection using OpenCV."""

    _camera_active = False
    _cap = None

    @classmethod
    def open_webcam(cls, duration=30):
        """
        Open webcam preview window.
        Press Q to quit early.
        """
        try:
            cls._cap = cv2.VideoCapture(0)
            if not cls._cap.isOpened():
                return False, "Could not access webcam, sir."

            cls._camera_active = True
            start = datetime.now()

            while cls._camera_active:
                ret, frame = cls._cap.read()
                if not ret:
                    break
                cv2.imshow("JARVIS Camera - Press Q to close", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                if (datetime.now() - start).seconds >= duration:
                    break

            cls.close_webcam()
            return True, "Webcam session ended, sir."
        except Exception as e:
            cls.close_webcam()
            return False, f"Webcam error: {e}"

    @classmethod
    def take_photo(cls):
        """Capture a photo and save to Desktop."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Could not access webcam, sir."

            ret, frame = cap.read()
            cap.release()

            if not ret:
                return False, "Failed to capture photo, sir."

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_photo_{timestamp}.jpg"
            filepath = os.path.join(config.SCREENSHOT_DIR, filename)
            cv2.imwrite(filepath, frame)
            return True, f"Photo saved to Desktop as {filename}, sir."
        except Exception as e:
            return False, f"Photo capture failed: {e}"

    @classmethod
    def face_detection(cls, duration=20):
        """Run face detection on webcam feed."""
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Could not access webcam, sir."

            start = datetime.now()
            face_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    face_count = max(face_count, len(faces))

                cv2.putText(
                    frame,
                    f"Faces: {len(faces)}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("JARVIS Face Detection - Press Q to close", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                if (datetime.now() - start).seconds >= duration:
                    break

            cap.release()
            cv2.destroyAllWindows()
            return True, f"Face detection complete. Maximum faces detected: {face_count}, sir."
        except Exception as e:
            cv2.destroyAllWindows()
            return False, f"Face detection failed: {e}"

    @classmethod
    def close_webcam(cls):
        """Release camera resources."""
        cls._camera_active = False
        if cls._cap is not None:
            cls._cap.release()
            cls._cap = None
        cv2.destroyAllWindows()

    @classmethod
    def read_text_from_camera(cls):
        """Capture a photo and extract text using Tesseract OCR."""
        try:
            import pytesseract
            # Note: Tesseract must be installed on the system (e.g., via installer on Windows)
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Could not access webcam for OCR, sir."
            
            # Read a few frames to let camera adjust brightness
            for _ in range(5):
                cap.read()
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return False, "Failed to capture photo for OCR, sir."
            
            text = pytesseract.image_to_string(frame).strip()
            if not text:
                return True, "I couldn't detect any readable text in the image, sir."
            return True, f"I read the following text:\n{text}"
        except ImportError:
            return False, "pytesseract is not installed, sir. Run pip install pytesseract."
        except Exception as e:
            return False, f"OCR failed (ensure Tesseract is installed on your OS): {e}"
