import openai
from get_api_key import get_api_key

openai.api_key = get_api_key()

def evaluate_ml(text):
    core_prompt = """Please analyze the given letter and provide feedback on the following aspects:
1. On a scale of 1 to 10, rate the motivation level of the applicant based on the content of the letter.
2. Determine the overall sentiment of the letter (positive, negative, neutral, etc.).
3. Describe the tone of the letter (e.g., formal, enthusiastic, professional).
4. Provide the word count of the letter.
5. Assess the grammar and language usage in the letter, pointing out any errors or improvements needed.
"""
    core_prompt2 = """Analyze the given letter and provide feedback on the following aspects using keywords:
1. Motivation level (scale of 1 to 10)
2. Overall sentiment (positive, negative, neutral)
3. Tone (can have up to 3 words)
4. Grammar and language usage (errors or improvements in 1 short sentence)
"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text + core_prompt2,
        max_tokens=200
    )
    
    return response.choices[0].text.strip()
    # return response
