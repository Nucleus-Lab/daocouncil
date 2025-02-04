import dspy
from backend.data_structure import Side


class Juror:
    def __init__(self, persona: str):
        self.persona = persona

    def judge(self, topic: str, sides: list[Side], conv: str):
        f = dspy.ChainOfThought(JurorDecision)
        response = f(persona=self.persona, topic=topic, sides=sides, conv=conv)
        return response.correct_side_id, response.reasoning
    

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

