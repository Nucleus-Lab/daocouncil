import dspy
from backend.data_structure import Side


class Juror:
    def __init__(self, persona: str):
        self.persona = persona

    def judge(self, topic: str, sides: list[Side], conv: str):
        f = dspy.ChainOfThought(JurorDecision)
        response = f(persona=self.persona, topic=topic, sides=sides, conv=conv)
        return response.correct_side_id, response.reasoning
    
def generate_juror_persona(topic: str):
    f = dspy.ChainOfThought(PersonaGeneration)
    response = f(topic=topic)
    return response.persona

class PersonaGeneration(dspy.Signature):
    """
    Generate five persona for jury given a debate topic.
    Guidelines:
    1. Generate 5 personas, each persona should be a short paragraph.
    2. Each persona should be unique and not similar to each other.
    3. Generate persona to represent a diverse group of stake holders.
    """
    topic = dspy.InputField(prefix="Topic：")
    persona:list[str] = dspy.OutputField(prefix="Persona：")

class JurorDecision(dspy.Signature):
    """
    Given a discussion of about a topic, determine which side is more correct.
    Output should be the id of the side that you think is more correct.
    Guidelines:
    Only output the id, do not include any other text.
    """
    
    persona = dspy.InputField(prefix="Persona：")
    topic = dspy.InputField(prefix="Topic：")
    sides: list[Side] = dspy.InputField(prefix="Sides：")
    conv = dspy.InputField(prefix="Conversation History：")
    correct_side_id = dspy.OutputField(prefix="Choice：", description="choose the id of the side that is more correct")

