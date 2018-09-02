import unittest
import makewave

class MyTest(unittest.TestCase):
    def test_mtof_middle_a(self):
        self.assertEqual(makewave.mtof(69.0), 440.0)

    def test_mtof_middle_c(self):
        self.assertEqual(makewave.mtof(60.0), 261.6255653005986)

    def test_ftom_middle_a(self):
        self.assertEqual(makewave.ftom(440.0), 69.0)

    def test_ftom_middle_c(self):
        self.assertEqual(makewave.ftom(261.6255653005986), 60.0)

if __name__ == '__main__':
    unittest.main()

