import openai
from get_api_key import get_api_key

openai.api_key = get_api_key()

def extract_cv(text):
    core_prompt = """Extract the following information from the given CV: 1. first name, 2. last name, 3. email, 4. phone number, 5. address, 6. postal code, 7. city, 8. country, 9. date of birth CV: """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=core_prompt + text,
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].text.strip()

def evaluate_cv(text):
    core_prompt = """Analyze the given CV and provide feedback on the following aspects using keywords:
1. Structure and organization (scale of 1 to 5)
2. Contact information (is all information present?, scale of 1 to 5)
3. Work experience (scale of 1 to 10)
4. Education (scale of 1 to 10)
5. Skills (scale of 1 to 10)
6. Languages (scale of 1 to 10)
CV: """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=core_prompt + text,
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].text.strip()

def evaluate_ml(text):
    core_prompt = """Analyze the given letter and provide feedback on the following aspects using keywords:
1. Motivation level (scale of 1 to 10)
2. Overall sentiment (positive, negative, neutral)
3. Tone (can have up to 3 words)
4. Grammar and language usage (errors or improvements in 1 short sentence)
"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text + core_prompt,
        temperature=0.3,
        max_tokens=200
    )
    
    return response.choices[0].text.strip()