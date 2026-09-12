import cv2
import os
import numpy as np
class FaceAuthenticator:
    def __init__(self, model_path="model.yml", dataset_dir="dataset", cascade_path=cv2.data.haarcascades + "haarcascade_frontalface_default.xml"):
        self.model_path = model_path
        self.dataset_dir = dataset_dir
        self.cascade_path = cascade_path
        self.recognizer = None
        self.face_cascade = None
        if not os.path.exists(self.dataset_dir):
            os.makedirs(self.dataset_dir)
            
        self._load_models()

    def _load_models(self):
        if os.path.exists(self.model_path):
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read(self.model_path)
        if os.path.exists(self.cascade_path):
            self.face_cascade = cv2.CascadeClassifier(self.cascade_path)

    def register_new_face(self, new_label_id):
        if not os.path.exists(self.cascade_path):
            return False, "Haar cascade classifier missing."

        face_cascade = cv2.CascadeClassifier(self.cascade_path)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Could not open webcam for registration."
        user_folder = os.path.join(self.dataset_dir, f"user_{new_label_id}")
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        count = 0
        max_samples = 60
        print(f"Starting face capture for user label: {new_label_id}. Look at the camera...")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(100, 100))
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1
                face_roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
                file_path = os.path.join(user_folder, f"{count}.jpg")
                cv2.imwrite(file_path, face_roi)

                cv2.putText(frame, f"Capturing Face: {count}/{max_samples}", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow("Registering Face ID", frame)
            if count >= max_samples or (cv2.waitKey(1) & 0xFF == ord('q')):
                break
        cap.release()
        cv2.destroyAllWindows()
        if count < max_samples:
            return False, "Face registration cancelled or not enough samples captured."       
        return self._retrain_all_models()
    def _retrain_all_models(self):
        faces_data = []
        labels_data = []
        if not os.path.exists(self.dataset_dir):
            return False, "Dataset directory not found."
        for user_folder in os.listdir(self.dataset_dir):
            if user_folder.startswith("user_"):
                try:
                    label_id = int(user_folder.split("_")[1])
                except ValueError:
                    continue
                path = os.path.join(self.dataset_dir, user_folder)
                for img_name in os.listdir(path):
                    img_path = os.path.join(path, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces_data.append(img)
                        labels_data.append(label_id)
        if not faces_data:
            return False, "No training data found."
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.train(faces_data, np.array(labels_data))
            self.recognizer.save(self.model_path)
            return True, "Model successfully retrained with isolated user profiles!"
        except Exception as e:
            return False, f"Retraining failed: {e}"
    def verify_face(self, expected_label=None):
        if not self.recognizer or not self.face_cascade:
            return False, "Face recognition model or cascade classifier missing."
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Could not open webcam."
        verified = False
        print(f"Starting strict face authentication scan for expected label: {expected_label}...")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(100, 100))
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (200, 200))
                label, confidence = self.recognizer.predict(face)
                score = max(0, min(100, 100 - confidence))
                label_matched = (expected_label is not None) and (label == int(expected_label))
                if confidence < 55 and label_matched:
                    cv2.putText(frame, f"VERIFIED ({int(score)}%)", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.imshow("Secure Face Scanner", frame)
                    cv2.waitKey(1000)
                    verified = True
                    break
                else:
                    status_text = f"Wrong User ({int(score)}%)" if not label_matched else f"Scanning... ({int(score)}%)"
                    cv2.putText(frame, status_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow("Secure Face Scanner (Press 'q' to abort)", frame)
            if verified:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        return verified, "Success" if verified else "Face verification failed or user mismatch."
