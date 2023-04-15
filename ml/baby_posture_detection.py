from .face_detection_model import FaceDetectionModel
import cv2 as cv
import pandas as pd
import numpy as np
import os
import math
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.metrics import roc_curve, auc, precision_recall_curve
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline

SENSOR_DIR = 'images/sensor/'
RESULT_DIR = 'images/predicted/'


def evaluation(y_test, y_pred, y_pred_prob):
    print('==========')
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
    precision, recall, thresholds = precision_recall_curve(
        y_test, y_pred_prob)
    print("Accuracy:\t{}\nPrecision:\t{}\nRecall:\t{}\nF1:\t{}\nROC-AUC:\t{}\nPR-AUC:\t{}".format(accuracy_score(y_test, y_pred),
                                                                                                  precision_score(
        y_test, y_pred),
        recall_score(
        y_test, y_pred),
        f1_score(y_test, y_pred),
        auc(fpr, tpr), auc(recall, precision)))
    print('==========')


class BabyPostureDetection:

    def __init__(self) -> None:
        self.face_detection_model = FaceDetectionModel()

        self.flip_classification_model = self.__train__(
            os.path.abspath('ml/train_flipped.csv'), "flipped")

    def __train__(self, training_file_path, label):
        # train test split
        train = pd.read_csv(training_file_path)

        X, y = train.drop(label, axis=1), train[label]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.30, random_state=0)

        # pipeline of baseline model
        estimator_pipeline = Pipeline(steps=[
            ('scaler', MinMaxScaler()),
            ('clf', LogisticRegression(random_state=0))
        ])

        # hyper parameter tuning using grid search
        parameters = {
            'clf__penalty': ['l2', 'l1'],
            'clf__C': np.logspace(-4, 4, 20),
            'clf__solver': ['saga', 'liblinear'],
        }

        clf = GridSearchCV(estimator_pipeline,
                           param_grid=parameters,
                           scoring='accuracy',
                           cv=10)

        # fit model
        clf.fit(X_train, y_train)
        clf.predict(X_test)
        clf.predict(X_train)
        clf.predict_proba(X_test)[:, 1]

        # optimal parameter
        # print(clf.best_params_)

        estimator_pipeline = Pipeline(steps=[
            ('scaler', MinMaxScaler()),
            ('clf', LogisticRegression(
                random_state=0,
                solver=clf.best_params_['clf__solver'],
                penalty=clf.best_params_['clf__penalty'],
                C=clf.best_params_['clf__C']
            ))
        ])

        # fit training data
        estimator_pipeline.fit(X_train, y_train)
        y_pred = estimator_pipeline.predict(X_test)
        y_pred_prob = estimator_pipeline.predict_proba(X_test)[:, 1]
        estimator_pipeline.predict(X_train)
        estimator_pipeline.fit(X, y)

        # model results
        evaluation(y_test, y_pred, y_pred_prob)

        # print(X_train)
        # print(estimator_pipeline.predict(X_train))
        return estimator_pipeline

    def __detect_face_in_image__(self, image_name: str) -> bool:
        results = self.face_detection_model.detect_face_in_image(
            path_to_image=str(os.path.abspath(SENSOR_DIR + image_name)))

        if results is None:
            return False
        else:
            cv.imwrite(os.path.abspath(RESULT_DIR + image_name), results)
            return True

    def predict_flip(self, data: list):
        '''
        data format: [image_name, pressure, gyro, left_distance, right_distance]
        '''
        print("Raw data: {}".format(data))

        df = pd.DataFrame(
            columns=["face_present", "pressure", "gyro", "left_distance", "right_distance"])

        # convert image path to 1/0 depending on whether face is detected
        if self.__detect_face_in_image__(data[0]):
            data[0] = 1
        else:
            data[0] = 0

        df.loc[len(df.index)] = data
        print("Processed data frame: \n{}".format(df))

        y_pred = int(self.flip_classification_model.predict(df)[0])
        print("Prediction: {}".format(y_pred))

        y_pred_prob = math.floor(
            self.flip_classification_model.predict_proba(df)[:, 1][0] * 100)
        print("Probability: {}".format(y_pred_prob))

        return (y_pred, y_pred_prob)

    # used to check when the baby is sleeping or awake
    def detect_eye_open_close_in_image(self, image_name: str) -> bool:
        ear, is_eye_open = self.face_detection_model.detect_eye_in_image(
            path_to_image=os.path.abspath(SENSOR_DIR + image_name))

        if is_eye_open:
            print("Eyes open detected, eyes aspect ratio: {}".format(ear))
        else:
            print("Eyes close detected, eyes aspect ratio: {}".format(ear))

        return (ear, is_eye_open)


if __name__ == '__main__':
    model = BabyPostureDetection()
