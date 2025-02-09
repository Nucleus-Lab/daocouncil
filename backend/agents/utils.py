import dspy

def generate_juror_persona(topic: str):
    f = dspy.ChainOfThought(PersonaGeneration)
    response = f(topic=topic)
    return response.persona

def summarize_debate(topic: str, sides: list[str], messages: str):
    f = dspy.ChainOfThought(DebateSummarizer)
    response = f(topic=topic, sides=sides, messages=messages)
    return response.summary

class DebateSummarizer(dspy.Signature):
    """
    Summarize a debate given a topic and a list of messages.
    Guidelines:
    1. List out points and group by their sides in point form.
    2. Be short and concise.
    3. Use simple language.
    4. Summarize the overall sentiment of the debate.
    5. Output in markdown format.
    """
    topic = dspy.InputField(prefix="Topic：")
    sides = dspy.InputField(prefix="Sides：")
    messages = dspy.InputField(prefix="Messages：")
    summary = dspy.OutputField(prefix="Summary：")


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