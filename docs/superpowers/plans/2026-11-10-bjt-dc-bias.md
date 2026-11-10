# BJT DC Bias Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development. Track the steps below with checkboxes.

**Goal:** Build a minimal, testable Flask DC bias calculator for the Lab 02 voltage-divider NPN circuit.

**Architecture:** A single Jinja form submits to Flask, which validates input and calls a separate engineering module. Display calculated values with units and conspicuous warnings when forward-active assumptions are questionable.

**Tech Stack:** Python 3, Flask, Jinja, CSS, unittest.

**Spec:** Approved design in the conversation; `Lab02_BJT_Simulator_Brainstorm_2-2569.html` sections 04, 06 and 09 are the authoritative lab requirements.

## Global Constraints

- Preserve all pre-existing files; create application files only inside `BJT-DC-Bias-Lab02/`.
- Inputs: VCC and VBE in V; R1, R2, RC, RE in kΩ; beta dimensionless. Convert resistance to Ω before calculation.
- VCC, resistances and beta must be positive; missing, nonnumeric and nonfinite values are invalid. Require nonnegative VBE.
- Use the worksheet's forward-active equations; `VTH <= VBE` warrants a cutoff warning; `VCE <= 0.2 V` warrants an approximate saturation warning. Explicitly state forward-active results may be invalid and this is not an exact transistor model.
- No AC, transient, circuit editor or SPICE solver. Do not commit or push without user authorization.
- Implementation begins only after plan approval.

## Review Focus

- Empty or nonnumeric form input: return readable errors without server failure (Task 2).
- NaN and infinity: reject rather than silently propagate (Tasks 1 and 2).
- Zero or negative component values: reject with clear errors (Tasks 1 and 2).
- Exact cutoff and saturation boundaries: display warnings at equality (Tasks 1 and 2).
- Existing repository and localhost safety: preserve prior files; development server binds to localhost only (Task 3).

### Task 1: Engineering model

**Files:** Create `BJT-DC-Bias-Lab02/dc_bias.py` and `BJT-DC-Bias-Lab02/tests/test_dc_bias.py`.

**Interface:** `calculate_bias(vcc: float, r1: float, r2: float, rc: float, re: float, beta: float, vbe: float) -> dict`; resistance arguments are Ω. Return keys `ib`, `ic`, `ie` in A; `vb`, `vc`, `ve`, `vce`, `vth` in V; `warnings` as a list of strings. Raise `ValueError` for invalid input.

- [ ] Write unittest cases for worksheet sample `(12, 100000, 22000, 2200, 1000, 100, 0.7)`: IB≈0.00001229858146 A, IC≈0.00122985815 A, IE≈0.00124215673 A, VB≈1.94215673 V, VC≈9.29431208 V, VE≈1.24215673 V, VCE≈8.05215535 V; no warnings.
- [ ] Add tests for zero/negative VCC, each resistance and beta; negative VBE; NaN/infinity; cutoff at `VTH == VBE`; and saturation at `VCE == 0.2 V` and below. Assert the relevant warning and that the model is identified as approximate.
- [ ] Run `python -m unittest discover -s tests -p test_dc_bias.py -v` from `BJT-DC-Bias-Lab02/`; verify failure because the module does not exist.
- [ ] Implement `calculate_bias` using the equations in the worksheet, returning raw forward-active estimates even when warnings apply; label them as potentially invalid in those cases.
- [ ] Run the same command; verify all tests pass.

### Task 2: Flask form and HTTP tests

**Files:** Create `BJT-DC-Bias-Lab02/app.py`, `templates/index.html`, `static/style.css`, `tests/test_web.py`, and `requirements.txt` within the project directory.

**Interface:** expose Flask `app`; GET `/` renders the form; POST `/` accepts the seven named inputs and calls `calculate_bias` after converting kΩ to Ω.

- [ ] Write Flask test-client tests: GET `/` returns 200 and all seven fields; POST the worksheet sample returns the independently calculated results and units; changing inputs changes results; missing, text, nonfinite, zero and negative inputs show errors without a 500; cutoff and saturation display clear warnings, including potentially invalid forward-active results.
- [ ] Install the declared Flask dependency in an isolated local environment; run `python -m unittest discover -s tests -p test_web.py -v` and verify failure because the app is not implemented.
- [ ] Implement the route, Jinja form and minimal responsive CSS. Label units, display IB/IC/IE and VB/VC/VE/VCE, retain entered values on errors, and explain the 0.2 V threshold is an approximation rather than an exact model.
- [ ] Run `python -m unittest discover -s tests -v`; verify all engineering and HTTP tests pass.

### Task 3: Reproducibility and verification

**Files:** Create `BJT-DC-Bias-Lab02/README.md` and `docs/validation.md`.

- [ ] Document Windows and cross-platform setup, dependency installation, localhost start, tests, units, equations, thresholds and limitations. Record the independent worksheet sample calculation in `docs/validation.md`.
- [ ] Run `python -m unittest discover -s tests -v` from the app directory and verify all tests pass, including at least three engineering tests and one Flask test-client test.
- [ ] Start `python -m flask --app app run` bound to `127.0.0.1`, verify GET and sample calculation through a browser, and stop the server. Record actual evidence, not assumed results.
- [ ] Review `git status` and the diff; confirm existing files were not modified and no virtual environment or credentials are staged. Present commit/push for explicit user approval.
