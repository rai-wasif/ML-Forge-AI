from pathlib import Path

import joblib


def save_training_artifacts(
    output_dir: Path,
    best_model,
    label_encoder,
    feature_summary: dict,
    training_summary: dict,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "best_model.pkl"
    preprocessing_path = output_dir / "preprocessing_pipeline.pkl"
    feature_path = output_dir / "feature_pipeline.pkl"
    label_encoder_path = output_dir / "label_encoder.pkl"

    joblib.dump(best_model, model_path)
    joblib.dump({"note": "Preprocessing engine metadata", "training": training_summary}, preprocessing_path)
    joblib.dump(feature_summary, feature_path)

    if label_encoder is not None:
        joblib.dump(label_encoder, label_encoder_path)
    else:
        joblib.dump(None, label_encoder_path)

    return {
        "model_path": str(model_path),
        "preprocessing_pipeline_path": str(preprocessing_path),
        "feature_pipeline_path": str(feature_path),
        "label_encoder_path": str(label_encoder_path),
    }
