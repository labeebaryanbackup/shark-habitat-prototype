import unittest
from pathlib import Path


# app.py lives at the repo root; AppTest.from_file resolves relative paths
# against the *calling* file (tests/), so point it there explicitly.
APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError:
    AppTest = None


@unittest.skipIf(
    AppTest is None,
    "Streamlit is not installed in the dependency-free CI job",
)
class StreamlitRuntimeTests(unittest.TestCase):
    def test_welcome_screen_renders_without_exceptions(self):
        app = AppTest.from_file(APP_PATH).run(timeout=20)

        self.assertEqual(list(app.exception), [])
        rendered = "\n".join(block.value for block in app.markdown)
        self.assertIn("Shark Habitat Suitability Explorer", rendered)
        self.assertIn("not a tracking system", rendered)
        self.assertNotIn("maximum accuracy", rendered.casefold())

    def test_default_score_run_completes_without_network_data(self):
        app = AppTest.from_file(APP_PATH).run(timeout=20)
        app.button[0].click().run(timeout=40)

        self.assertEqual(list(app.exception), [])
        messages = "\n".join(block.value for block in app.success)
        self.assertIn("Prototype score complete", messages)


if __name__ == "__main__":
    unittest.main()
