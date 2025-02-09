import dspy
from backend.data_structure import Side


class Juror:
    def __init__(self, persona: str):
        self.persona = persona

    def judge(self, topic: str, sides: list[Side], conv_history: str, past_reasoning: str, previous_decision: int, new_message: str):
        f = dspy.ChainOfThought(JurorDecision)
        side_msg = ""
        for side in sides:
            side_msg += f"{side.id}: {side.description}\n"
        response = f(persona=self.persona, topic=topic, sides=side_msg, conv_history=conv_history, past_reasoning=past_reasoning, previous_decision=previous_decision, new_message=new_message)
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
    You are a juror in a debate. Your persona is given below.
    Given a discussion of about a topic, determine which side is more correct.
    Output should be the id of the side that you think is more correct.
    # Reasoning Guidelines:
    1. In your reasoning, you should reply in the first person.
    2. Summarize your concerns and reasoning in a concise manner, straight to the point.
    3.  
    4. Do not repeat your persona in your reasoning, instead, summarize your concerns and reasoning in a concise manner.
    5. You should consider the past reasoning and the new message when making your decision.
    6. Repeat the past reasoning if the new message is irrelevant to the debate.
    
    # Output Guidelines:
    1. If the new message addresses your concerns, or provides new information that convinces you, you should change your decision.
    2. If the new message is not strong enough to change your decision, do not change your decision.
    3. Only output the id of the side that you think is more correct.
    """
    
    persona = dspy.InputField(prefix="Persona：")
    topic = dspy.InputField(prefix="Topic：")
    sides = dspy.InputField(prefix="Sides：")
    conv_history = dspy.InputField(prefix="Conversation History：")
    past_reasoning = dspy.InputField(prefix="Your Past Reasoning：")
    previous_decision = dspy.InputField(prefix="Your Previous Decision：")
    new_message = dspy.InputField(prefix="New Message：")
    correct_side_id: int = dspy.OutputField(prefix="Choice：", description="choose the id of the side that is more correct")

