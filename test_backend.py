import unittest
import os
from index import classify_image_vit, vit_with_ocr, get_api_output, app
from PIL import Image
import time
import io
from unittest.mock import patch

# Paths to test images
IMAGE_DIR = "tests"
TEST_IMAGES = {
    "battery": "processed_battery.jpg",
    "glass": "processed_sprite.png",
    "syringe": "processed_needle.png",
    "compost": "processed_compost.png",
    "trash": "processed_trash.png",
    "metal": "processed_coke.jpg",
    "cardboard": "processed_cardboard.png",
    "plastic": "processed_tropicana.png",
    "paper": "processed_paper.png"
}

class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    # UNIT TESTS
    def test_all_predictions_under_10_seconds(self):
        """Ensure /predict endpoint responds under 10s for test images"""
        for label, filename in list(TEST_IMAGES.items())[:2]:
            with self.subTest(label=label):
                with open(os.path.join(IMAGE_DIR, filename), 'rb') as img_file:
                    data = {'image': (io.BytesIO(img_file.read()), filename)}

                    start = time.time()
                    response = self.client.post('/predict', content_type='multipart/form-data', data=data)
                    duration = time.time() - start

                    self.assertEqual(response.status_code, 200, f"{label} failed with status {response.status_code}")
                    self.assertLess(duration, 10, f"{label} took too long: {duration:.2f}s")


    def test_hazardous_classification(self):
        """Battery and syringe must be hazardous"""
        for label in ["battery", "syringe"]:
            path = os.path.join(IMAGE_DIR, TEST_IMAGES[label])
            scores, class_name, _, _ = vit_with_ocr(path)
            if class_name == label:
                status = "hazardous"
            else:
                status = "trash"
            self.assertEqual(status, "hazardous", f"{label} was classified as {status}")


    def test_ocr_works(self):
        """OCR should detect 'tropicana' in juice bottle image"""
        path = os.path.join(IMAGE_DIR, TEST_IMAGES["plastic"])
        _, _, logs, _ = vit_with_ocr(path)

        # Ensure OCR was actually used
        self.assertNotIn("No OCR", logs, "OCR was not triggered for plastic image")

        # Check if 'tropicana' is mentioned in logs (case insensitive)
        found = any("tropicana" in log.lower() for log in logs)
        self.assertTrue(found, "OCR logs do not mention 'tropicana'")

    def test_zip_code_difference(self):
        """Different ZIP codes yield different recyclable sets"""
        zip1 = "77845"  # College Station, TX
        zip2 = "33109"  # Miami Beach, FL

        recyclable_1 = get_api_output(zip1)
        recyclable_2 = get_api_output(zip2)

        self.assertIsInstance(recyclable_1, set)
        self.assertIsInstance(recyclable_2, set)

        self.assertNotEqual(recyclable_1, recyclable_2,
            f"Expected different recycling sets for ZIP codes {zip1} and {zip2}, but got the same: {recyclable_1}")

    # INTEGRATION TESTS
    def test_ocr_triggered_only_below_threshold(self):
        """OCR should trigger for low-confidence predictions, not for high-confidence ones"""
        # Case 1: Plastic image expected to trigger OCR
        plastic_path = os.path.join(IMAGE_DIR, TEST_IMAGES["plastic"])
        scores_p, class_p, logs_p, _ = vit_with_ocr(plastic_path)
        top_score_p = scores_p.get(class_p, 0)

        # threshold + ocr_bonus
        if top_score_p <= 0.85 + 0.5:
            self.assertNotIn("No OCR", logs_p, "OCR should have been triggered for plastic but wasn't")
        else:
            self.assertIn("No OCR", logs_p, "OCR was triggered unnecessarily for plastic")

        # Case 2: Glass image expected NOT to trigger OCR
        glass_path = os.path.join(IMAGE_DIR, TEST_IMAGES["glass"])
        scores_g, class_g, logs_g, _ = vit_with_ocr(glass_path)
        top_score_g = scores_g.get(class_g, 0)

        self.assertGreaterEqual(top_score_g, 0.8, "Glass prediction confidence unexpectedly low")
        self.assertIn("No OCR", logs_g, "OCR was triggered unnecessarily for high-confidence glass prediction")
    
    def test_classification_matches_api(self):
        """Ensure classification status matches API recyclable classes from /predict"""
        for label, filename in list(TEST_IMAGES.items())[:2]:
            with self.subTest(label=label):
                with open(os.path.join(IMAGE_DIR, filename), 'rb') as img_file:
                    data = {'image': (io.BytesIO(img_file.read()), filename)}
                    response = self.client.post('/predict', content_type='multipart/form-data', data=data)
                    self.assertEqual(response.status_code, 200)

                    result = response.get_json()
                    prediction = result["prediction"]
                    status = result["status"]
                    recyclable_classes = set(result["recyclable_classes"])

                    expected_status = "hazardous" if prediction in {"battery", "syringe"} else (
                        "recyclable" if prediction in recyclable_classes else "trash"
                    )

                    self.assertEqual(status, expected_status,
                                    f"{label}: Prediction '{prediction}' classified as '{status}', expected '{expected_status}'")

if __name__ == '__main__':
    unittest.main()