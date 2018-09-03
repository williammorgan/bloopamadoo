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

    def test_lerp(self):
        self.assertEqual(makewave.lerp(10, 20, -0.5), 5)
        self.assertEqual(makewave.lerp(10, 20,  0.0), 10)
        self.assertEqual(makewave.lerp(10, 20,  0.5), 15)
        self.assertEqual(makewave.lerp(10, 20,  1.0), 20)
        self.assertEqual(makewave.lerp(10, 20,  1.5), 25)

if __name__ == '__main__':
    unittest.main()

