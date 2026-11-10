import unittest

from app import app


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.sample = dict(vcc='12', r1='100', r2='22', rc='2.2', re='1', beta='100', vbe='0.7')

    def test_get_form(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        for field in self.sample:
            self.assertIn(f'name="{field}"', response.get_data(as_text=True))

    def test_sample_and_changed_input(self):
        body = self.client.post('/', data=self.sample).get_data(as_text=True)
        for value in ('1.9422', '9.2943', '1.2422', '8.0522', '1.2299', 'mA', 'V'):
            self.assertIn(value, body)
        self.sample['vcc'] = '15'
        self.assertNotEqual(body, self.client.post('/', data=self.sample).get_data(as_text=True))

    def test_invalid_inputs(self):
        for key, value in [('vcc', ''), ('r1', 'abc'), ('r2', 'nan'), ('rc', 'inf'), ('re', '0'), ('beta', '-1')]:
            data = dict(self.sample, **{key: value})
            response = self.client.post('/', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Error', response.get_data(as_text=True))

    def test_warnings(self):
        for values, warning in [({'vcc': '2', 'r1': '1', 'r2': '1', 'vbe': '1'}, 'Cutoff'),
                                ({'vcc': '4', 'r1': '1', 'r2': '1', 'rc': '2.8', 're': '.5', 'beta': '1', 'vbe': '.5'}, 'Saturation')]:
            body = self.client.post('/', data=dict(self.sample, **values)).get_data(as_text=True)
            self.assertIn(warning, body)
            self.assertIn('may be invalid', body)

    def test_extreme_finite_input_shows_error(self):
        data = dict(self.sample, r1='1e305', r2='1e305')
        response = self.client.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Error', response.get_data(as_text=True))

    def test_visual_structure_and_live_labels(self):
        body = self.client.get('/').get_data(as_text=True)
        for text in ('Input Parameters', 'Circuit: Common-Emitter Amplifier', 'DC Bias Results', 'Week 2 Goal', 'data-circuit="r1"'):
            self.assertIn(text, body)
        self.assertNotIn('Active region approximation OK', body)

    def test_status_depends_on_actual_result(self):
        body = self.client.post('/', data=self.sample).get_data(as_text=True)
        self.assertIn('Active region approximation OK', body)
        self.sample.update(vcc='2', r1='1', r2='1', vbe='1')
        body = self.client.post('/', data=self.sample).get_data(as_text=True)
        self.assertIn('Cutoff', body)
        self.assertNotIn('Active region approximation OK', body)

    def test_equivalent_units_calculate_same_result(self):
        converted = dict(vcc='12000', vcc_unit='mV', r1='100000', r1_unit='ohm',
                         r2='0.022', r2_unit='Mohm', rc='2200', rc_unit='ohm',
                         re='0.001', re_unit='Mohm', beta='100', vbe='700', vbe_unit='mV')
        body = self.client.post('/', data=converted).get_data(as_text=True)
        for value in ('1.9422', '9.2943', '1.2422', '8.0522', '1.2299'):
            self.assertIn(value, body)
        self.assertIn('data-circuit-unit="r1"', body)

    def test_unknown_units_are_rejected(self):
        response = self.client.post('/', data=dict(self.sample, r1_unit='bogus'))
        self.assertIn('Error', response.get_data(as_text=True))

    def test_unit_conversion_underflow_shows_error(self):
        for value in ('1e-320', '1e-307', '1e-308'):
            with self.subTest(value=value):
                response = self.client.post('/', data=dict(self.sample, vbe=value, vbe_unit='mV'))
                self.assertEqual(response.status_code, 200)
                self.assertIn('too small', response.get_data(as_text=True))

    def test_text_underflow_shows_error(self):
        response = self.client.post('/', data=dict(self.sample, vbe='1e-400', vbe_unit='V'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('too small', response.get_data(as_text=True))

    def test_intermediate_underflow_shows_error(self):
        data = dict(vcc='1e-200', r1='1e-200', r2='1e-200', rc='1e-200', re='1e-200', beta='1', vbe='0', r1_unit='ohm', r2_unit='ohm', rc_unit='ohm', re_unit='ohm')
        response = self.client.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('too small', response.get_data(as_text=True))

    def test_multiple_field_errors_are_specific(self):
        response = self.client.post('/', data=dict(self.sample, r1='', r2='abc', rc='0', vbe='-1'))
        body = response.get_data(as_text=True)
        for field, message in [('r1', 'required'), ('r2', 'number'), ('rc', 'greater than zero'), ('vbe', 'zero or greater')]:
            self.assertRegex(body, rf'id="{field}-error"[^>]*>\s*[^<]*{message}')
            self.assertRegex(body, rf'id="{field}"[^>]*aria-invalid="true"')
        self.assertNotIn('Active region approximation OK', body)

    def test_unit_error_is_attached_to_its_field(self):
        body = self.client.post('/', data=dict(self.sample, r1_unit='bogus')).get_data(as_text=True)
        self.assertRegex(body, r'id="r1-error"[^>]*>\s*[^<]*unit')

    def test_valid_fields_have_accessible_error_targets(self):
        body = self.client.get('/').get_data(as_text=True)
        self.assertIn('aria-describedby="r1-error"', body)
        self.assertIn('id="r1-error"', body)


if __name__ == '__main__':
    unittest.main()
