---
tag: m211
title: Software Endstops
brief: Set and/or get the software endstops state

experimental: false
requires: (MIN|MAX)_SOFTWARE_ENDSTOPS
group: planner

codes:
  - M211

long:
  - Optionally enable/disable software endstops, then report the current state.
  - With software endstops enabled, moves will be clipped to the physical boundaries from `[XYZ]_MIN_POS` to `[XYZ]_MAX_POS`.

notes:
  - Requires either `MIN_SOFTWARE_ENDSTOPS` or `MAX_SOFTWARE_ENDSTOPS` for the enable option.

parameters:
  -
    tag: S
    optional: true
    description: Software endstops state
    values:
      -
        tag: flag
        type: bool

examples:

---

