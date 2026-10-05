import json
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "plant_disease_model.h5"
CLASS_NAMES_PATH = PROJECT_ROOT / "class_names.json"
DATABASE_PATH = PROJECT_ROOT / "data" / "crop_rescue.db"
IMAGE_SIZE = (224, 224)
EXPECTED_INPUT_SHAPE = (224, 224, 3)
MAX_UPLOAD_SIZE_MB = 12
HIGH_CONFIDENCE_THRESHOLD = 0.80
MODERATE_CONFIDENCE_THRESHOLD = 0.55
LOW_CONFIDENCE_THRESHOLD = 0.45
CONFIDENCE_GAP_THRESHOLD = 0.10
SUPPORTED_CROPS = ("Maize", "Potato", "Tomato", "Cassava")
CROP_CLASS_PREFIXES = {
    "Maize": "Corn_(maize)___",
    "Potato": "Potato___",
    "Tomato": "Tomato___",
    "Cassava": "Cassava___",
}


class ConfigurationError(ValueError):
    """Raised when local model configuration is missing or invalid."""


@st.cache_data(show_spinner=False)
def load_class_names(path: str = str(CLASS_NAMES_PATH)) -> tuple[str, ...]:
    class_names_path = Path(path)
    if not class_names_path.is_file():
        raise ConfigurationError(
            f"Class mapping file was not found: {class_names_path.name}"
        )

    try:
        class_names = json.loads(class_names_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(
            "The class mapping file could not be read as valid JSON."
        ) from exc

    if (
        not isinstance(class_names, list)
        or not class_names
        or any(not isinstance(name, str) or not name.strip() for name in class_names)
    ):
        raise ConfigurationError(
            "The class mapping must be a non-empty JSON list of class names."
        )

    if len(set(class_names)) != len(class_names):
        raise ConfigurationError("The class mapping contains duplicate labels.")

    return tuple(class_names)