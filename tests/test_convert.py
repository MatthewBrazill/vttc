import os
import tempfile
import unittest

from convert import main


def normalize_vtt(text: str) -> str:
    # Normalize line endings and strip trailing whitespace for reliable comparison
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


class TestVttConverter(unittest.TestCase):
    def run_conversion_and_compare(self, input_path: str, expected_path: str):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "output.vtt")
            main(input_path, out_path, False)

            with open(out_path, "r", encoding="utf-8") as f:
                actual = normalize_vtt(f.read())

            with open(expected_path, "r", encoding="utf-8") as f:
                expected = normalize_vtt(f.read())

            self.assertEqual(actual, expected)

    def test_google_meet_example(self):
        self.run_conversion_and_compare(
            input_path=os.path.join(os.path.dirname(__file__), "..", "examples", "google-example.txt"),
            expected_path=os.path.join(os.path.dirname(__file__), "..", "examples", "google-out.vtt"),
        )

    def test_zoom_example(self):
        self.run_conversion_and_compare(
            input_path=os.path.join(os.path.dirname(__file__), "..", "examples", "zoom-example.txt"),
            expected_path=os.path.join(os.path.dirname(__file__), "..", "examples", "zoom-out.vtt"),
        )


if __name__ == "__main__":
    unittest.main()
