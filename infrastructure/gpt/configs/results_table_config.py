from infrastructure.gpt.configs.assistant_config import AssistantConfig

# Configuration 4: Organizing test result in a table
results_table_config = AssistantConfig(
    system=(
        "You are an assistant specialized in organizing test results into a structured table. "
        "You will receive a developer report as context and your task is to generate a table of results with the following columns:\n"
        "- Area\n"
        "- Key findings\n"
        "- Effort Issue (time spent)\n"
        "- Quality\n\n"
        "Greet the user on first interaction and explain how you will present the results table."
    ),
    output_format={
        "format": {
            "type": "json_schema",
            "name": "results_table_response",
            "schema": {
                "type": "object",
                "properties": {
                    "friendly_message": {"type": "string"},
                    "results_table": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "area":            {"type": "string"},
                                "key_findings":    {"type": "string"},
                                "effort_issue":    {"type": "string"},
                                "quality":         {"type": "string"}
                            },
                            "required": ["area", "key_findings", "effort_issue", "quality"],
                            "additionalProperties": False
                        }
                    },
                    "additional_notes": {"type": "string"}
                },
                "required": ["friendly_message", "results_table", "additional_notes"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    requires_vector_context=False
)