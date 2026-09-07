"""Synthetic ACX-200 Service Manual.

Not a real manufacturer document — written for this project per
CLAUDE.md's MVP boundary ("one synthetic or openly-licensed equipment
manual"). Covers the sections needed for M4's search_manual tool and
M5's three demo scenarios (overheating, dangerous vibration, low
discharge pressure), plus general reference sections.

Each entry becomes one chunk in Chroma, tagged with the metadata shape
from README's "Chroma Cloud" section: equipment_type, manufacturer,
model, document, section, page, content_type.
"""

DOCUMENT_NAME = "ACX-200 Service Manual"
EQUIPMENT_TYPE = "air_compressor"
MANUFACTURER = "DemoAir"
MODEL = "ACX-200"

SECTIONS = [
    {
        "section": "Overview and Specifications",
        "page": 3,
        "content_type": "specifications",
        "text": (
            "The DemoAir ACX-200 is a single-stage rotary screw air compressor rated for "
            "continuous industrial duty. Rated discharge pressure is 125 psi at a normal "
            "operating temperature range of 160-190F. Rated motor vibration under normal "
            "load is 1.5-2.5 mm/s RMS. Sustained vibration above 4.0 mm/s indicates a "
            "mechanical fault and should not be run through routine troubleshooting."
        ),
    },
    {
        "section": "Safety Warnings",
        "page": 5,
        "content_type": "safety",
        "text": (
            "Do not perform internal inspection or component replacement while the unit is "
            "energized or under pressure. Lockout/tagout procedures must be independently "
            "verified before opening any access panel. If motor temperature exceeds 220F or "
            "vibration exceeds 4.0 mm/s, do not attempt continued operation or routine "
            "troubleshooting — the unit must be shut down and a specialist notified."
        ),
    },
    {
        "section": "Fault E27: Motor Stall",
        "page": 42,
        "content_type": "troubleshooting",
        "text": (
            "Fault E27 indicates a stalled motor, typically triggered by restricted intake "
            "airflow causing the motor to draw excess current. Check the intake filter for "
            "clogging or excessive dust loading, and check the motor thermal cutoff before "
            "attempting a restart. Intake filters should be replaced at the interval in the "
            "Maintenance Schedule; an overdue filter is the most common cause of this fault."
        ),
    },
    {
        "section": "Overheating and Elevated Temperature",
        "page": 47,
        "content_type": "troubleshooting",
        "text": (
            "Elevated discharge or motor temperature (above the 190F normal range) is most "
            "often caused by restricted intake airflow from a clogged or overdue intake "
            "filter, similar to the root cause of fault E27. Cross-reference the asset's "
            "maintenance history for the last intake filter replacement date before "
            "escalating — if the filter is overdue, replacement is the first troubleshooting "
            "step. If temperature remains elevated after a known-good filter is confirmed, "
            "treat as a specialist-required condition rather than continuing routine checks."
        ),
    },
    {
        "section": "Excessive Vibration",
        "page": 51,
        "content_type": "troubleshooting",
        "text": (
            "Vibration readings above 4.0 mm/s RMS exceed the safe operating limit and "
            "indicate a possible mechanical fault such as bearing wear, rotor imbalance, or "
            "loose mounting hardware. This condition is not part of routine troubleshooting: "
            "do not attempt disassembly or continued operation. Stop routine diagnostic "
            "steps and escalate to a specialist immediately, providing the current vibration "
            "reading and recent trend if available."
        ),
    },
    {
        "section": "Low Discharge Pressure",
        "page": 55,
        "content_type": "troubleshooting",
        "text": (
            "Discharge pressure sustained below 100 psi (against a 125 psi rating) with "
            "normal motor operation most often indicates an air leak in the discharge "
            "piping, a fitting, or a worn seal, rather than a compressor fault. Combine the "
            "current reading with maintenance history: a recently serviced seal or fitting "
            "narrows the likely leak location. Check accessible fittings and connections "
            "before escalating; persistent low pressure with no visible leak should be "
            "treated as a specialist-required condition."
        ),
    },
    {
        "section": "Maintenance Schedule",
        "page": 60,
        "content_type": "maintenance",
        "text": (
            "Intake filter: inspect every 90 days, replace every 6 months or sooner under "
            "heavy dust loading. Drive belt: inspect every 90 days, replace at first sign of "
            "cracking or glazing. Full inspection: every 6 months. Discharge seals and "
            "fittings: inspect annually or immediately following any low discharge pressure "
            "event."
        ),
    },
    {
        "section": "Parts Reference",
        "page": 63,
        "content_type": "specifications",
        "text": (
            "Intake filter part number FLT-200. Drive belt part number BLT-200. Always "
            "confirm part availability before scheduling a repair that depends on a "
            "replacement part."
        ),
    },
]
