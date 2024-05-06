import cv2
import numpy as np
import face_recognition
from typing import List

class FaceRecognizer:
    def __init__(self, known_face_encodings: List[np.array], known_face_labels: List[str]):
        self.known_face_encodings = known_face_encodings
        self.known_face_labels = known_face_labels

    def recognize_faces(self, frame: np.array) -> List[str]:
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        face_labels = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = 'Unknown'

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_labels[best_match_index]
            face_labels.append(name)

        return face_locations, face_labels

if __name__ == "__main__":
    known_image_path_1 = 'C:\\Users\\Anastasia\\KPI\\Python-data\\practice3\\me1.jpg'
    known_image_path_2 = 'C:\\Users\\Anastasia\\KPI\\Python-data\\practice3\\ira1.jpg'

    known_image_1 = face_recognition.load_image_file(known_image_path_1)
    known_face_encoding_1 = face_recognition.face_encodings(known_image_1)[0]

    known_image_2 = face_recognition.load_image_file(known_image_path_2)
    known_face_encoding_2 = face_recognition.face_encodings(known_image_2)[0]

    known_face_encodings = [known_face_encoding_1, known_face_encoding_2]
    known_face_labels = ['Anastasiia', 'Iryna']

    face_recognizer = FaceRecognizer(known_face_encodings, known_face_labels)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        face_locations, face_labels = face_recognizer.recognize_faces(frame)

        for (top, right, bottom, left), name in zip(face_locations, face_labels):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()