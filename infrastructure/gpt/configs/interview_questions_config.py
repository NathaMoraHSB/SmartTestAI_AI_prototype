from infrastructure.gpt.configs.assistant_config import AssistantConfig

# Configuration 2: Customer Support
interview_questions_config = AssistantConfig(
    system=(
        "You are an assistant specialized in crafting interview questions for project stakeholders. "
        "You will receive project context, stakeholder roles, and objectives, and your task is to generate a structured "
        "list of interview questions tailored to the Project Owner. "
        "Greet the user on first interaction and explain how you will guide them through the question elaboration process. Automatically suggest 5 question"
    ),
    output_format={
        "format": {
            "type": "json_schema",
            "name": "interview_questions_response",
            "schema": {
                "type": "object",
                "properties": {
                    "friendly_message": {"type": "string"},
                    "interview_questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question_number":   {"type": "integer"},
                                "question_text":     {"type": "string"},
                                "category":          {"type": "string"},
                                "purpose":           {"type": "string"}
                            },
                            "required": ["question_number", "question_text", "category", "purpose"],
                            "additionalProperties": False
                        }
                    },
                    "additional_notes": {"type": "string"}
                },
                "required": ["friendly_message", "interview_questions", "additional_notes"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    requires_vector_context=True
)
