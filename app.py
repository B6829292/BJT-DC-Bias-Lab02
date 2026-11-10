from decimal import Decimal, InvalidOperation
import math

from flask import Flask, render_template, request

from dc_bias import _multiply, _normal, calculate_bias

app = Flask(__name__)
FIELDS = ('vcc', 'r1', 'r2', 'rc', 're', 'beta', 'vbe')
DEFAULTS = dict(zip(FIELDS, ('12', '100', '22', '2.2', '1', '100', '0.7')))
UNIT_FACTORS = {'vcc': {'V': 1, 'mV': 0.001}, 'vbe': {'V': 1, 'mV': 0.001},
                **{key: {'ohm': 1, 'kohm': 1000, 'Mohm': 1000000} for key in ('r1', 'r2', 'rc', 're')}}
DEFAULT_UNITS = {key: ('V' if key in ('vcc', 'vbe') else 'kohm') for key in UNIT_FACTORS}


@app.route('/', methods=['GET', 'POST'])
def index():
    values = DEFAULTS.copy() if request.method == 'GET' else {key: request.form.get(key, '') for key in FIELDS}
    units = {key: request.form.get(key + '_unit', default) if request.method == 'POST' else default
             for key, default in DEFAULT_UNITS.items()}
    result = error = None
    errors = {}
    if request.method == 'POST':
        numbers = {}
        for key in FIELDS:
            try:
                if not values[key].strip():
                    errors[key] = 'This field is required.'
                    continue
                decimal_value = Decimal(values[key])
                number = float(decimal_value)
                if not decimal_value.is_finite() or not math.isfinite(number):
                    errors[key] = 'Enter a finite number.'
                    continue
                numbers[key] = _normal(number, nonzero_expected=decimal_value.is_finite() and not decimal_value.is_zero())
                if key == 'vbe' and number < 0:
                    errors[key] = 'Enter zero or greater.'
                elif key != 'vbe' and number <= 0:
                    errors[key] = 'Enter a value greater than zero.'
                elif key in UNIT_FACTORS:
                    if units[key] not in UNIT_FACTORS[key]:
                        errors[key] = 'Choose a valid unit.'
                    else:
                        numbers[key] = _multiply(numbers[key], UNIT_FACTORS[key][units[key]])
                        if not math.isfinite(numbers[key]):
                            errors[key] = 'Value is too large after unit conversion.'
            except (ValueError, OverflowError, InvalidOperation) as exc:
                errors[key] = ('Value is too small for reliable calculation.' if 'too small' in str(exc)
                               else 'Enter a valid number.')
        if errors:
            error = 'Error: Correct the highlighted fields.'
        else:
            try:
                result = calculate_bias(**numbers)
            except (ValueError, OverflowError) as exc:
                error = ('Error: Values are too small for reliable calculation.' if 'too small' in str(exc)
                         else 'Error: The combination of values is too large for reliable calculation.')
    return render_template('index.html', values=values, units=units, result=result, error=error, errors=errors)
