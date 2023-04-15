import numpy as np
import cv2 as cv
import dlib
import os
from imutils import face_utils
from .yunet import YuNet
from scipy.spatial import distance as dist


def visualize(image, results, box_color=(0, 255, 0), text_color=(0, 0, 255), fps=None):
    output = image.copy()
    landmark_color = [
        (255,   0,   0),  # right eye
        (0,   0, 255),  # left eye
        (0, 255,   0),  # nose tip
        (255,   0, 255),  # right mouth corner
        (0, 255, 255)  # left mouth corner
    ]

    if fps is not None:
        cv.putText(output, 'FPS: {:.2f}'.format(
            fps), (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, text_color)

    for det in (results if results is not None else []):
        bbox = det[0:4].astype(np.int32)
        cv.rectangle(output, (bbox[0], bbox[1]),
                     (bbox[0]+bbox[2], bbox[1]+bbox[3]), box_color, 2)

        conf = det[-1]
        cv.putText(output, '{:.4f}'.format(
            conf), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)

        landmarks = det[4:14].astype(np.int32).reshape((5, 2))
        for idx, landmark in enumerate(landmarks):
            cv.circle(output, landmark, 2, landmark_color[idx], 2)

    return output


class FaceDetectionModel:

    def __init__(self) -> None:
        self.yunet = YuNet()

    def detect_face_in_image(self, path_to_image: str):
        '''
        path_to_image: ab path to image
        '''
        if path_to_image is None:
            raise Exception("No path provided.")

        print(path_to_image)

        image = cv.imread(filename=path_to_image)

        if image is None:
            raise Exception("Invalid image provided.")

        h, w, _ = image.shape

        self.yunet.setInputSize([w, h])
        results = self.yunet.infer(image)

        if results is None:
            return None
        else:
            # print('{} faces detected: {}'.format(results.shape[0], path_to_image))

            image = visualize(image, results)

            return image

    # only works if baby is facing front, cannot detect eyes for side view
    def detect_eye_in_image(self, path_to_image: str):
        '''
        path_to_image: relative path to image
        '''
        if path_to_image is None:
            raise Exception("No path provided.")

        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(
            os.path.abspath('ml/shape_predictor_68_face_landmarks.dat'))

        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        frame = cv.imread(path_to_image)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:

            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv.convexHull(leftEye)
            rightEyeHull = cv.convexHull(rightEye)
            cv.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear > 0.17:
                return (ear, False)
            else:
                return (ear, True)

        return (0, False)

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear
