from infrastructure.gpt.configs.assistant_config import AssistantConfig

# Configuration 1: Exploratory Testing
exploratory_testing_config = AssistantConfig(
    system=(
        "You are an assistant for exploratory testing. "
        "You will receive project and session information and your task is to generate a detailed list of goals for the exploratory test session. "
        "Each goal should describe what the tester aims to explore or evaluate during the session. "
        "Do not propose step-by-step procedures. "
        "If it's the user's first interaction, greet them and explain that you will help define the session goals. "
        "Always read and consider the current list of goals before generating a new response, as the user may modify or add to it. "
        "If the user asks a question or makes a comment that does not change the goal list, respond only in the 'friendly_message' and keep the list of goals unchanged."
    ),
    output_format = {
        "format": {
            "type": "json_schema",
            "name": "test_procedure_response",
            "schema": {
                "type": "object",
                "properties": {
                    "friendly_message": {"type": "string"},
                    "test_procedure": {
                        "type": "object",
                        "properties": {
                            "goals": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "goal_number": {"type": "integer"},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["goal_number", "description"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["goals"],
                        "additionalProperties": False
                    }
                },
                "required": ["friendly_message", "test_procedure"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    requires_vector_context=True
)