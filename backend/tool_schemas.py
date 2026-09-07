"""JSON-Schema tool definitions.

Used two ways: (1) tool_registry.py validates incoming arguments against
these before executing anything, (2) assemblyai_gateway.py sends them
(wrapped as AssemblyAI "function" tools) in session.update so the LLM
knows what it can call and with what arguments.
"""

TOOL_SCHEMAS = [
    {
        "name": "get_asset_details",
        "description": "Look up an industrial compressor asset's model, site, and manufacturer by its asset ID.",
        "parameters": {
            "type": "object",
            "properties": {"asset_id": {"type": "string", "description": "Asset ID, e.g. AC-104"}},
            "required": ["asset_id"],
        },
    },
    {
        "name": "get_live_telemetry",
        "description": (
            "Get the current live sensor readings (temperature, vibration, discharge pressure) "
            "for a compressor asset."
        ),
        "parameters": {
            "type": "object",
            "properties": {"asset_id": {"type": "string", "description": "Asset ID, e.g. AC-104"}},
            "required": ["asset_id"],
        },
    },
    {
        "name": "get_maintenance_history",
        "description": "Get the maintenance and repair history for a compressor asset.",
        "parameters": {
            "type": "object",
            "properties": {"asset_id": {"type": "string", "description": "Asset ID, e.g. AC-104"}},
            "required": ["asset_id"],
        },
    },
    {
        "name": "search_manual",
        "description": (
            "Search the equipment service manual for troubleshooting guidance, filtered to a "
            "specific asset model."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "asset_model": {"type": "string", "description": "Equipment model, e.g. ACX-200"},
                "fault_code": {"type": "string", "description": "Fault code shown on the panel, if any"},
                "question": {"type": "string", "description": "Free-text question about the manual"},
            },
            "required": ["asset_model"],
        },
    },
    {
        "name": "check_parts_inventory",
        "description": "Check whether a specific spare part is in stock at a site, and how many are on hand.",
        "parameters": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "Site ID, e.g. SITE-01"},
                "part_number": {"type": "string", "description": "Part number, e.g. FLT-200"},
            },
            "required": ["site_id", "part_number"],
        },
    },
    {
        "name": "create_work_order",
        "description": "Create a new work order for an asset describing the problem being investigated.",
        "parameters": {
            "type": "object",
            "properties": {
                "asset_id": {"type": "string", "description": "Asset ID, e.g. AC-104"},
                "problem": {"type": "string", "description": "Short description of the problem"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                    "description": "Priority level",
                },
            },
            "required": ["asset_id", "problem"],
        },
    },
    {
        "name": "record_observation",
        "description": "Record a measurement the technician has just observed against an open work order.",
        "parameters": {
            "type": "object",
            "properties": {
                "work_order_id": {"type": "integer", "description": "The work order ID to record against"},
                "measurement": {"type": "string", "description": "What was measured, e.g. motor_temperature"},
                "value": {"type": "number", "description": "The observed value"},
                "unit": {"type": "string", "description": "Unit of measurement, e.g. F, psi, mm/s"},
            },
            "required": ["work_order_id", "measurement", "value", "unit"],
        },
    },
    {
        "name": "escalate_to_specialist",
        "description": (
            "Escalate the case to a specialist when a condition is beyond routine troubleshooting "
            "or unsafe to continue."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "asset_id": {"type": "string", "description": "Asset ID, e.g. AC-104"},
                "reason": {"type": "string", "description": "Why this needs specialist attention"},
                "work_order_id": {"type": "integer", "description": "Related work order ID, if one exists"},
            },
            "required": ["asset_id", "reason"],
        },
    },
    {
        "name": "complete_work_order",
        "description": "Mark a work order as complete with a resolution summary.",
        "parameters": {
            "type": "object",
            "properties": {
                "work_order_id": {"type": "integer", "description": "The work order ID to complete"},
                "resolution": {"type": "string", "description": "Summary of how the issue was resolved"},
            },
            "required": ["work_order_id", "resolution"],
        },
    },
    {
        "name": "set_risk_level",
        "description": (
            "Declare the current risk classification for this session, per the safety model: "
            "observation (retrieving info, recording measurements), low_risk_inspection (guiding an "
            "approved checklist one step at a time), lockout_required (a site lockout/tagout procedure "
            "must be independently verified complete before continuing), specialist_required (stop "
            "procedural guidance, a specialist is needed), or dangerous_condition (instruct the "
            "technician to move away and follow the site's emergency procedure). Call this whenever "
            "the classification changes, not only when it gets more severe."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": [
                        "observation",
                        "low_risk_inspection",
                        "lockout_required",
                        "specialist_required",
                        "dangerous_condition",
                    ],
                },
                "reason": {"type": "string", "description": "Why this classification applies now"},
            },
            "required": ["level", "reason"],
        },
    },
]

TOOL_SCHEMAS_BY_NAME = {schema["name"]: schema for schema in TOOL_SCHEMAS}
