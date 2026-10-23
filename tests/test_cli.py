"""CLI path parsing checks migrated unchanged from the SDK repository."""
import unittest


class TestSplitCommand(unittest.TestCase):
    """demo_cli.split_command 必须保留 Windows 反斜杠路径（shlex posix 会吃掉）。"""

    def setUp(self):
        import importlib
        self.demo_cli = importlib.import_module("demo_cli")

    def test_windows_absolute_path_preserved(self):
        got = self.demo_cli.split_command(r"photo F:\Codes\wintest.jpg")
        self.assertEqual(got, ["photo", r"F:\Codes\wintest.jpg"])

    def test_quoted_path_with_space(self):
        got = self.demo_cli.split_command('photo "C:\\a b\\x.jpg"')
        self.assertEqual(got, ["photo", r"C:\a b\x.jpg"])

    def test_plain_tokens(self):
        self.assertEqual(self.demo_cli.split_command("led inner blink green fast"),
                         ["led", "inner", "blink", "green", "fast"])


if __name__ == '__main__':
    unittest.main()
