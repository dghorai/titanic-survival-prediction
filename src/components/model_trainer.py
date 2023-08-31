import os
import sys

from dataclasses import dataclass
from sklearn.tree import DecisionTreeClassifier
from imblearn.over_sampling import RandomOverSampler

from src.exception import CustomException
from src.logger import logging, project_dir
from src.utils import save_object, evaluate_model


@dataclass
class ModelTrainerConfig:
    trained_model_filepath = os.path.join(
        project_dir, "artifacts", "model.pkl")


class ModelTrainer:

    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_training(self, train_arrc, test_arrc):
        try:
            logging.info(
                'Splitting dependent and independent variables from train and test data')

            X_train, y_train, X_test, y_test = (
                train_arrc[:, :-1], train_arrc[:, -1], test_arrc[:, :-1], test_arrc[:, -1])

            # up sampling to balance the training dataset
            ros = RandomOverSampler(random_state=42)
            X_train, y_train = ros.fit_resample(X_train, y_train)

            # change/add based on model
            gridsearch_best_params = {'criterion': 'gini', 'max_depth': 20,
                                      'min_samples_leaf': 1, 'min_samples_split': 2, 'splitter': 'random'}
            models = {'DecisionTreeClassifier': DecisionTreeClassifier(
                **gridsearch_best_params)}

            model_report: dict = evaluate_model(
                X_train, y_train, X_test, y_test, models)

            print(model_report)
            print('\n===========================\n')
            logging.info(f'Model Report: {model_report}')

            # get the best model score and name from dictionary
            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[list(
                model_report.values()).index(best_model_score)]

            best_model = models[best_model_name]

            print(
                f'Best model found -> Model Name: {best_model_name}, accuracy report: {best_model_score}')
            print('\n===========================\n')
            logging.info(
                f'Best model found -> Model Name: {best_model_name}, accuracy report: {best_model_score}')

            # save model
            save_object(
                file_path=self.model_trainer_config.trained_model_filepath,
                obj=best_model
            )
        except Exception as e:
            logging.info('Exception occured at model training stage')
            raise CustomException(e, sys)
