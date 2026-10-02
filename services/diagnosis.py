from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from PIL import Image

from config import (
    HIGH_CONFIDENCE_THRESHOLD,
    IMAGE_SIZE,
    MODERATE_CONFIDENCE_THRESHOLD,
)


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


def _confidence_status(confidence: float) -> str:
    if confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return "higher"
    if confidence >= MODERATE_CONFIDENCE_THRESHOLD:
        return "moderate"
    return "low"


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

    return PredictionResult(
        class_name=best.class_name,
        confidence=best.confidence,
        confidence_status=_confidence_status(best.confidence),
        top_predictions=top_predictions,
    )