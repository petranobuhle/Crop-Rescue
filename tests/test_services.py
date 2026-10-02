import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from config import ConfigurationError, load_class_names
from services.diagnosis import predict_image, prepare_image
from services.image_quality import inspect_image
from services.model import ModelLoadError, validate_model


class FakeModel:
    input_shape = (None, 224, 224, 3)
    output_shape = (None, 3)

    def __init__(self, scores: np.ndarray | None = None) -> None:
        self.scores = scores if scores is not None else np.array([[0.1, 0.7, 0.2]])
        self.received: np.ndarray | None = None

    def predict(self, batch: np.ndarray, verbose: int = 0) -> np.ndarray:
        self.received = batch
        return self.scores


class ServiceTests(unittest.TestCase):
    def test_class_names_keep_json_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "classes.json"
            path.write_text(json.dumps(["first", "second"]), encoding="utf-8")

            self.assertEqual(load_class_names(str(path)), ("first", "second"))

    def test_invalid_class_mapping_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "classes.json"
            path.write_text(json.dumps(["duplicate", "duplicate"]), encoding="utf-8")

            with self.assertRaises(ConfigurationError):
                load_class_names(str(path))

    def test_model_input_and_output_shapes_are_checked(self) -> None:
        validate_model(FakeModel(), ("first", "second", "third"))

        with self.assertRaises(ModelLoadError):
            validate_model(FakeModel(), ("first", "second"))

        invalid_model = FakeModel()
        invalid_model.input_shape = (None, 160, 160, 3)
        with self.assertRaises(ModelLoadError):
            validate_model(invalid_model, ("first", "second", "third"))

        fixed_batch_model = FakeModel()
        fixed_batch_model.input_shape = (2, 224, 224, 3)
        with self.assertRaises(ModelLoadError):
            validate_model(fixed_batch_model, ("first", "second", "third"))

    def test_preprocessing_preserves_mobile_net_input_contract(self) -> None:
        received: list[np.ndarray] = []

        def preprocess(values: np.ndarray) -> np.ndarray:
            received.append(values.copy())
            return values / 127.5 - 1.0

        image = Image.new("RGB", (320, 180), color=(255, 127, 0))
        batch = prepare_image(image, preprocess_fn=preprocess)

        self.assertEqual(batch.shape, (1, 224, 224, 3))
        self.assertEqual(batch.dtype, np.float32)
        self.assertEqual(received[0].shape, (224, 224, 3))
        self.assertEqual(received[0].dtype, np.float32)
        self.assertAlmostEqual(float(batch[0, 0, 0, 0]), 1.0)

    def test_prediction_uses_the_supplied_label_order(self) -> None:
        model = FakeModel()
        labels = ("label zero", "label one", "label two")
        with patch(
            "services.diagnosis.prepare_image",
            return_value=np.zeros((1, 224, 224, 3), dtype=np.float32),
        ):
            result = predict_image(
                model,
                Image.new("RGB", (224, 224), color="green"),
                labels,
            )

        self.assertEqual(result.class_name, "label one")
        self.assertEqual(result.confidence_status, "moderate")
        self.assertEqual(model.received.shape, (1, 224, 224, 3))

    def test_image_quality_handles_valid_and_corrupt_images(self) -> None:
        image_data = BytesIO()
        Image.new("RGB", (320, 320), color="green").save(image_data, format="PNG")

        valid_result = inspect_image(image_data.getvalue())
        corrupt_result = inspect_image(b"not an image")

        self.assertTrue(valid_result.is_valid)
        self.assertEqual(valid_result.image.mode, "RGB")
        self.assertFalse(corrupt_result.is_valid)

    def test_dark_photo_produces_a_retake_warning(self) -> None:
        image_data = BytesIO()
        Image.new("RGB", (320, 320), color="black").save(image_data, format="PNG")

        result = inspect_image(image_data.getvalue())

        self.assertTrue(any("very dark" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()