import logging
from typing import Any

import streamlit as st

from config import (
    CLASS_NAMES_PATH,
    EXPECTED_INPUT_SHAPE,
    MODEL_PATH,
    ConfigurationError,
    load_class_names,
)


logger = logging.getLogger(__name__)


class ModelLoadError(RuntimeError):
    """Raised when the local model cannot be loaded or validated."""


def validate_model(model: Any, class_names: tuple[str, ...]) -> None:
    input_shape = getattr(model, "input_shape", None)
    if (
        not isinstance(input_shape, (tuple, list))
        or len(input_shape) != 4
        or tuple(input_shape[1:]) != EXPECTED_INPUT_SHAPE
        or input_shape[0] not in (None, 1)
    ):
        raise ModelLoadError(
            "The model input must be a single 224x224 RGB image."
        )

    output_shape = getattr(model, "output_shape", None)
    if (
        not isinstance(output_shape, (tuple, list))
        or not output_shape
        or isinstance(output_shape[0], (tuple, list))
    ):
        raise ModelLoadError("The model must have one classification output.")

    output_count = output_shape[-1]
    if not isinstance(output_count, int) or output_count != len(class_names):
        raise ModelLoadError(
            "Model/class mismatch: the model output count does not match "
            "class_names.json."
        )


@st.cache_resource(show_spinner=False)
def load_model() -> Any:
    if not MODEL_PATH.is_file():
        raise ModelLoadError("The trained model file could not be found.")

    try:
        class_names = load_class_names(str(CLASS_NAMES_PATH))
    except ConfigurationError as exc:
        raise ModelLoadError(str(exc)) from exc

    try:
        import tensorflow as tf

        model = tf.keras.models.load_model(str(MODEL_PATH), compile=False)
        validate_model(model, class_names)
        return model
    except ModelLoadError:
        raise
    except Exception as exc:
        logger.exception("Unable to load the local Crop Rescue model")
        raise ModelLoadError(
            "The trained model could not be loaded. Check the local model file "
            "and TensorFlow installation."
        ) from exc