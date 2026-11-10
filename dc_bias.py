"""Voltage-divider NPN bias, using the forward-active approximation."""

import math
import sys


def _normal(value, *, nonzero_expected=False):
    """Reject underflow and subnormal values whose precision is reduced."""
    if (value == 0 and nonzero_expected) or (0 < abs(value) < sys.float_info.min):
        raise ValueError('Value is too small for reliable calculation.')
    return value


def _multiply(a, b):
    return _normal(a * b, nonzero_expected=a != 0 and b != 0)


def _divide(a, b):
    return _normal(a / b, nonzero_expected=a != 0)


def calculate_bias(vcc: float, r1: float, r2: float, rc: float,
                   re: float, beta: float, vbe: float) -> dict:
    values = (vcc, r1, r2, rc, re, beta, vbe)
    if not all(math.isfinite(value) for value in values):
        raise ValueError('All values must be finite numbers.')
    for value in values:
        _normal(value)
    if any(value <= 0 for value in values[:6]) or vbe < 0:
        raise ValueError('VCC, resistances and beta must be positive; VBE must be nonnegative.')

    divider_sum = r1 + r2
    divider_voltage = _multiply(vcc, r2)
    divider_resistance = _multiply(r1, r2)
    if not all(map(math.isfinite, (divider_sum, divider_voltage, divider_resistance))):
        raise ValueError('Values are too large for the calculation.')
    vth = _divide(divider_voltage, divider_sum)
    rth = _divide(divider_resistance, divider_sum)
    denominator = rth + _multiply(beta + 1, re)
    if not math.isfinite(denominator):
        raise ValueError('Values are too large for the calculation.')
    ib = _divide(_normal(vth - vbe), denominator)
    ic = _multiply(beta, ib)
    ie = _multiply(beta + 1, ib)
    ve = _multiply(ie, re)
    vb = _normal(ve + vbe)
    vc = _normal(vcc - _multiply(ic, rc))
    vce = _normal(vc - ve)
    if not all(math.isfinite(value) for value in (ib, ic, ie, vb, vc, ve, vce, ib * 1000, ic * 1000, ie * 1000)):
        raise ValueError('Values are too large for the calculation.')
    warnings = []
    if vth <= vbe:
        warnings.append('Cutoff: forward-active results may be invalid; this is an approximation, not an exact model.')
    if vce <= 0.2 or math.isclose(vce, 0.2, rel_tol=0, abs_tol=1e-12):
        warnings.append('Saturation: VCE ≤ 0.2 V is an approximate threshold; forward-active results may be invalid, not an exact model.')
    return dict(ib=ib, ic=ic, ie=ie, vb=vb, vc=vc, ve=ve, vce=vce,
                vth=vth, warnings=warnings)
