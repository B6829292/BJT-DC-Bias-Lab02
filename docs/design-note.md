# Lab 02 design note

The brainstorming discussion approved a minimal, single-page Flask/Jinja application for the NPN voltage-divider DC bias circuit. Flask calls an independent Python engineering module; HTML, CSS and tests are separate. No AC, transient or SPICE simulation is included.

The considered alternative was a Flask API with JavaScript rendering; server-rendered Jinja was chosen for lower complexity. A later approved UI refinement added an SVG circuit and unit selectors; the server still performs the engineering calculation.

The model assumes constant β and VBE in forward active operation. It warns when VTH ≤ VBE or VCE ≤ 0.2 V; the latter is an approximate threshold, not an exact saturation model. The implementation plan is in `superpowers/plans/2026-11-10-bjt-dc-bias.md`, and the independent reference calculation is in `validation.md`.
