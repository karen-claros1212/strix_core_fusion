import unittest
from saga_fusion.telegram.command_parser import CommandParser
from saga_fusion.telegram.telegram_types import RiskLevel

class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_parse_valid_command(self):
        cmd = self.parser.parse("/status")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command, "status")
        self.assertEqual(cmd.args, [])

    def test_parse_command_with_args(self):
        cmd = self.parser.parse("/mission run")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command, "mission")
        self.assertEqual(cmd.args, ["run"])

    def test_parse_invalid_command(self):
        cmd = self.parser.parse("Hello World")
        self.assertIsNone(cmd)

    def test_classify_risk_run(self):
        cmd = self.parser.parse("/run")
        risk = self.parser.classify_risk(cmd)
        self.assertEqual(risk, RiskLevel.R4)

    def test_classify_risk_create(self):
        cmd = self.parser.parse("/create")
        risk = self.parser.classify_risk(cmd)
        self.assertEqual(risk, RiskLevel.R3)

    def test_classify_risk_unknown(self):
        cmd = self.parser.parse("/unknown")
        risk = self.parser.classify_risk(cmd)
        self.assertEqual(risk, RiskLevel.R0)

if __name__ == '__main__':
    unittest.main()