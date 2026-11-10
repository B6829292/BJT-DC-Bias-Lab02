import unittest

from dc_bias import calculate_bias


class BiasTests(unittest.TestCase):
    def test_reference(self):
        result = calculate_bias(12, 100000, 22000, 2200, 1000, 100, 0.7)
        for key, expected in {'ib': 0.00001229858146, 'ic': 0.00122985815,
                              'ie': 0.00124215673, 'vb': 1.94215673,
                              'vc': 9.29431208, 've': 1.24215673,
                              'vce': 8.05215535}.items():
            self.assertAlmostEqual(result[key], expected, places=7)
        self.assertEqual(result['warnings'], [])

    def test_invalid(self):
        values = [12, 100000, 22000, 2200, 1000, 100, 0.7]
        for i in range(7):
            for value in ([0, -1, float('nan'), float('inf')] if i < 6 else [-1, float('nan'), float('inf')]):
                inputs = values.copy()
                inputs[i] = value
                with self.subTest(index=i, value=value), self.assertRaises(ValueError):
                    calculate_bias(*inputs)

    def test_cutoff_boundary(self):
        result = calculate_bias(2, 1000, 1000, 1000, 1000, 100, 1)
        self.assertTrue(any('cutoff' in warning.lower() for warning in result['warnings']))

    def test_below_cutoff_warns(self):
        result = calculate_bias(2, 1000, 1000, 1000, 1000, 100, 1.1)
        self.assertTrue(any('cutoff' in warning.lower() for warning in result['warnings']))

    def test_extreme_finite_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_bias(12, 1e308, 1e308, 2200, 1000, 100, 0.7)

    def test_intermediate_product_underflow_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'too small'):
            calculate_bias(1e-200, 1e-200, 1e-200, 1e-200, 1e-200, 1, 0)

    def test_subnormal_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'too small'):
            calculate_bias(12, 100000, 22000, 2200, 1000, 100, 5e-324)

    def test_zero_vbe_is_allowed(self):
        self.assertGreater(calculate_bias(12, 100000, 22000, 2200, 1000, 100, 0)['ic'], 0)

    def test_saturation_boundary_and_below(self):
        # beta=1, VTH=2, RTH=500, RE=500 gives IB=0.001 A.
        # VCC=4, RC=2800 gives VCE=0.2 V.
        for rc in (2800, 3000):
            result = calculate_bias(4, 1000, 1000, rc, 500, 1, 0.5)
            self.assertTrue(any('saturation' in warning.lower() for warning in result['warnings']))


if __name__ == '__main__':
    unittest.main()
