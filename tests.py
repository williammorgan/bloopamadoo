import unittest
import makewave

class MyTest(unittest.TestCase):
    def test_mtof_middle_a(self):
        self.assertEqual(makewave.mtof(69.0), 440.0)

    def test_mtof_middle_c(self):
        self.assertAlmostEqual(makewave.mtof(60.0), 261.63, places = 2)

    def test_ftom_middle_a(self):
        self.assertEqual(makewave.ftom(440.0), 69.0)

    def test_ftom_middle_c(self):
        self.assertAlmostEqual(makewave.ftom(261.63), 60.0, places = 2)

    def test_lerp(self):
        self.assertEqual(makewave.lerp(10, 20, -0.5), 5)
        self.assertEqual(makewave.lerp(10, 20,  0.0), 10)
        self.assertEqual(makewave.lerp(10, 20,  0.5), 15)
        self.assertEqual(makewave.lerp(10, 20,  1.0), 20)
        self.assertEqual(makewave.lerp(10, 20,  1.5), 25)

    def test_adsr(self):
        test_adsr = makewave.adsr(0.5, 0.5, 0.75, 0.5, 10)
        self.assertAlmostEqual(test_adsr.__next__(), 0.2,  places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.4,  places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.6,  places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.8,  places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 1.0,  places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.95, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.90, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.85, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.80, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.75, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.75, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.75, places = 2)
        self.assertAlmostEqual(test_adsr.send(True), 0.60, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.45, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.30, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.15, places = 2)
        self.assertAlmostEqual(test_adsr.__next__(), 0.0, places = 2)
        with self.assertRaises(StopIteration):
            test_adsr.__next__()

if __name__ == '__main__':
    unittest.main()

