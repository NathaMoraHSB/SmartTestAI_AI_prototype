from infrastructure.gpt.configs.assistant_config import AssistantConfig

# Configuration 3: Summarizing Test Results
summarizing_assistant_config = AssistantConfig(
    system=(
        "You are an assistant specialized in summarizing test pre-reports for developers. "
        "You will receive a pre-report document as context and your task is to produce a concise summary and actionable recommendations. "
        "The summary must clearly describe what was done, the total test execution time, and provide multiple recommendations based on the context provided. "
        "Greet the user on first interaction and explain how you’ll present the summary and recommendations."
    ),
    output_format={
        "format": {
            "type": "json_schema",
            "name": "summarization_response",
            "schema": {
                "type": "object",
                "properties": {
                    "friendly_message": {"type": "string"},
                    "test_summary": {
                        "type": "object",
                        "properties": {
                            "what_was_done": {"type": "string"},
                            "execution_time": {"type": "string"},
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "recommendation_number": {"type": "integer"},
                                        "recommendation_text": {"type": "string"},
                                        "rationale": {"type": "string"}
                                    },
                                    "required": ["recommendation_number", "recommendation_text", "rationale"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["what_was_done", "execution_time", "recommendations"],
                        "additionalProperties": False
                    },
                    "additional_notes": {"type": "string"}
                },
                "required": ["friendly_message", "test_summary", "additional_notes"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    requires_vector_context=False
)