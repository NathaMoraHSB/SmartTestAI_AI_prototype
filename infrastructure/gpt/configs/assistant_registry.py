from infrastructure.gpt.models.assistant_name import AssistantName
from infrastructure.gpt.configs.exploratory_testing_config import exploratory_testing_config
from infrastructure.gpt.configs.interview_questions_config import interview_questions_config
from infrastructure.gpt.configs.results_table_config import results_table_config
from infrastructure.gpt.configs.summarizing_assistant_config import summarizing_assistant_config

# Dictionary of assistants
ASSISTANTS = {
    AssistantName.EXPLORATORY_TESTING:   exploratory_testing_config,
    AssistantName.INTERVIEW_PREPARATION: interview_questions_config,
    AssistantName.SUMMARIZING:           summarizing_assistant_config,
    AssistantName.TEST_RESULTS:          results_table_config,
}