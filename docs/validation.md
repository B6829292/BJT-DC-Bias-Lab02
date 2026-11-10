# Reference calculation

Worksheet example: VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V.

Using the worksheet equations independently: VTH = 12 × 22/122 = 2.163934 V; RTH = 100 × 22/122 = 18.032787 kΩ. Thus IB = (2.163934 − 0.7)/(18.032787 kΩ + 101 kΩ) = 0.0122986 mA. IC = 1.229858 mA, IE = 1.242157 mA, VE = 1.242157 V, VB = 1.942157 V, VC = 9.294312 V, VCE = 8.052155 V. These rounded values are used as independent test expectations.

## Numeric range

Python floating-point arithmetic has limited precision. Nonzero subnormal inputs and intermediate results are rejected because they have reduced precision; nonzero products or quotients that round to zero are also rejected. The threshold is the platform's smallest positive normal float (`sys.float_info.min`), not a circuit-design limit. Text values that round to zero and underflow during unit conversion are rejected before calculation. Exact zero remains permitted for VBE and valid zero-valued intermediate results. Very large inputs can also be rejected when arithmetic overflows.
