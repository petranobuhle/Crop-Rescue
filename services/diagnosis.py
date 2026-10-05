from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from PIL import Image

from config import (
    CONFIDENCE_GAP_THRESHOLD,
    HIGH_CONFIDENCE_THRESHOLD,
    IMAGE_SIZE,
    LOW_CONFIDENCE_THRESHOLD,
    MODERATE_CONFIDENCE_THRESHOLD,
)
from data.catalog import crop_for_class


class PredictionError(RuntimeError):
    """Raised when model output cannot be interpreted as a prediction."""


@dataclass(frozen=True)
class RankedPrediction:
    class_name: str
    confidence: float


@dataclass(frozen=True)
class PredictionResult:
    class_name: str
    confidence: float
    confidence_status: str
    top_predictions: tuple[RankedPrediction, ...]
    second_prediction: RankedPrediction | None = None
    confidence_gap: float = 0.0


def prepare_image(
    image: Image.Image,
    preprocess_fn: Callable[[np.ndarray], np.ndarray] | None = None,
) -> np.ndarray:
    rgb_image = image.convert("RGB").resize(IMAGE_SIZE)
    image_array = np.asarray(rgb_image, dtype=np.float32)

    if preprocess_fn is None:
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        preprocess_fn = preprocess_input

    preprocessed = preprocess_fn(image_array)
    return np.expand_dims(preprocessed, axis=0)


def _confidence_status(confidence: float, gap: float) -> str:
    if confidence >= HIGH_CONFIDENCE_THRESHOLD and gap >= CONFIDENCE_GAP_THRESHOLD:
        return "high"
    if confidence >= MODERATE_CONFIDENCE_THRESHOLD or gap < CONFIDENCE_GAP_THRESHOLD:
        return "moderate"
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return "low"
    return "moderate"


def matches_selected_crop(class_name: str, selected_crop: str) -> bool:
    return crop_for_class(class_name) == selected_crop


def predict_image(
    model: Any,
    image: Image.Image,
    class_names: tuple[str, ...],
) -> PredictionResult:
    if not class_names:
        raise PredictionError("No model class labels are available.")

    predictions = np.asarray(
        model.predict(prepare_image(image), verbose=0),
        dtype=np.float32,
    )
    if predictions.ndim == 2 and predictions.shape[0] == 1:
        scores = predictions[0]
    elif predictions.ndim == 1:
        scores = predictions
    else:
        raise PredictionError("The model returned an unexpected output shape.")

    if scores.size != len(class_names):
        raise PredictionError(
            "The model output count does not match class_names.json."
        )
    if not np.all(np.isfinite(scores)):
        raise PredictionError("The model returned invalid prediction values.")

    ranked_indices = np.argsort(scores)[::-1][: min(3, len(class_names))]
    top_predictions = tuple(
        RankedPrediction(
            class_name=class_names[int(index)],
            confidence=float(scores[int(index)]),
        )
        for index in ranked_indices
    )
    best = top_predictions[0]
    second = top_predictions[1] if len(top_predictions) > 1 else None
    gap = 0.0 if second is None else max(0.0, float(best.confidence - second.confidence))

    return PredictionResult(
        class_name=best.class_name,
        confidence=best.confidence,
        confidence_status=_confidence_status(best.confidence, gap),
        top_predictions=top_predictions,
        second_prediction=second,
        confidence_gap=gap,
    )