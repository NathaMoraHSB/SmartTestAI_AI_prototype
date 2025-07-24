class AssistantConfig:
    def __init__(self, system, output_format, requires_vector_context=False):
        self.system = system
        self.output_format = output_format
        self.requires_vector_context = requires_vector_context