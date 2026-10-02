import tempfile
import unittest
from pathlib import Path

from config import load_class_names
from data.catalog import catalog_entries, disease_info_for
from data.database import initialize_database
from data.feedback import pending_feedback, save_feedback
from data.history import recent_scans, save_scan


class DataFeatureTests(unittest.TestCase):
    def test_catalog_covers_all_authoritative_classes(self) -> None:
        class_names = load_class_names()

        self.assertEqual(len(class_names), 22)
        self.assertEqual(len(catalog_entries(class_names)), 22)
        self.assertTrue(all(disease_info_for(name) for name in class_names))

    def test_local_scan_history_and_pending_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "crop_rescue.db"
            initialize_database(database_path)
            scan = save_scan(
                "Tomato",
                "Tomato___Early_blight",
                0.82,
                "higher",
                database_path,
            )
            saved_feedback = save_feedback(
                scan.scan_id,
                "Not helpful",
                "The spots look different in my field.",
                database_path,
            )

            self.assertEqual(recent_scans(path=database_path), (scan,))
            self.assertEqual(saved_feedback.status, "pending")
            self.assertEqual(saved_feedback.note, "The spots look different in my field.")
            self.assertEqual(pending_feedback(path=database_path), (saved_feedback,))


if __name__ == "__main__":
    unittest.main()