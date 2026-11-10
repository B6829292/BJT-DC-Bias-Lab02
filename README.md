# Lab 02: BJT DC Bias Web App

Flask app for an NPN common-emitter voltage-divider bias circuit, using a constant-β, constant-VBE forward-active approximation.

## Setup and run

From this directory, with Python 3 installed:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run
```

On macOS/Linux use `source .venv/bin/activate` instead. Open <http://127.0.0.1:5000/>. The development server is for local use, not public deployment.

Run tests from the same directory and environment:

```text
python -m unittest discover -s tests -v
```

## Inputs and model

Choose V or mV for VCC and VBE; choose Ω, kΩ or MΩ for R1, R2, RC and RE. Changing units converts the displayed number while preserving the electrical value. β is dimensionless. The server converts voltages to V and resistances to Ω. VCC, resistances and β must be positive, VBE nonnegative, and all inputs finite.

`VTH=VCC*R2/(R1+R2)`, `RTH=R1*R2/(R1+R2)`, `IB=(VTH-VBE)/(RTH+(β+1)*RE)`, `IC=β*IB`, `IE=(β+1)*IB`, `VE=IE*RE`, `VB=VE+VBE`, `VC=VCC-IC*RC`, `VCE=VC-VE`.

The app reports these forward-active estimates even outside the model's valid region, with warnings. `VTH ≤ VBE` indicates possible cutoff; `VCE ≤ 0.2 V` is an approximate saturation warning threshold, not an exact transistor model. In either case results may be invalid. See `docs/validation.md` for a reference calculation.

Inputs or intermediate values too small for reliable normal floating-point arithmetic are rejected; see `docs/validation.md` for the numerical limits.
