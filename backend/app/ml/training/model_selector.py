from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from xgboost import XGBClassifier, XGBRegressor


RANDOM_STATE = 42


def select_models(problem_type: str) -> dict:
    if problem_type == "classification":
        return {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            "Random Forest": RandomForestClassifier(n_estimators=80, random_state=RANDOM_STATE, n_jobs=-1),
            "XGBoost": XGBClassifier(
                n_estimators=60,
                max_depth=3,
                learning_rate=0.1,
                subsample=0.9,
                colsample_bytree=0.9,
                eval_metric="logloss",
                random_state=RANDOM_STATE,
                n_jobs=1,
                verbosity=0,
            ),
            "LightGBM": LGBMClassifier(n_estimators=60, random_state=RANDOM_STATE, verbosity=-1),
            "CatBoost": CatBoostClassifier(
                iterations=60,
                depth=4,
                learning_rate=0.1,
                random_state=RANDOM_STATE,
                verbose=False,
                allow_writing_files=False,
            ),
        }

    return {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=80, random_state=RANDOM_STATE, n_jobs=-1),
        "XGBoost Regressor": XGBRegressor(
            n_estimators=60,
            max_depth=3,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=RANDOM_STATE,
            n_jobs=1,
            verbosity=0,
        ),
        "LightGBM Regressor": LGBMRegressor(n_estimators=60, random_state=RANDOM_STATE, verbosity=-1),
        "CatBoost Regressor": CatBoostRegressor(
            iterations=60,
            depth=4,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
            verbose=False,
            allow_writing_files=False,
        ),
    }
