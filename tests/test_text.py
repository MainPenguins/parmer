from unittest import TestCase

from core.text_tracker import changed_span

# Just for komeil
class TestChangedSpan(TestCase):
    def test_changes(self):
        cases = (
            ("hello", "hello", None),
            ("hello", "hello world", (5, 5, 11)),
            ("hello world", "hello", (5, 11, 5)),
            ("hello", "hullo", (1, 2, 2)),
            ("", "hello", (0, 0, 5)),
            ("hello", "", (0, 5, 0)),
            ("سلام", "سلام دنیا", (4, 4, 9)),
        )

        for old_text, new_text, expected in cases:
            with self.subTest(old_text=old_text, new_text=new_text):
                self.assertEqual(
                    changed_span(old_text, new_text),
                    expected,
                )
