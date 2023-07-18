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

def pros_cons(cv, pos):
    core_prompt = f"""You work in HR. You have the CV of a candidate who has applied for a job at your company. Given the CV and the position's title and decription, write a list of up to 3 pros and cons of hiring the candidate (if any). The position they have applied for is {pos[2]}. The description of the position is {pos[3]}. The candidate's CV is {cv}"""

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=core_prompt,
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].text.strip()

def response_positive(cand, pos):
    core_prompt = f"""You work in HR. You are writing an email to a candidate who has applied for a job at your company. The candidate has been selected for the next round of interviews. You want to inform the candidate about this and ask them to choose a time slot for the interview. The candidate's name is {cand[2]} {cand[3]} and the position they have applied for is {pos[2]}. The description of the position is {pos[3]}. Write the email without subject."""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[
            {"role": "system", "content": core_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def response_negative(cand, pos, cons):
    core_prompt = f"""You work in HR. You are writing an email to a candidate who has applied for a job at your company. The candidate has been rejected. You want to inform the candidate about this and thank them for their time. The candidate's name is {cand[2]} {cand[3]} and the position they have applied for is {pos[2]}. The description of the position is {pos[3]}. {f'You may subtly and softly inform them of the reasons for the rejection, without stating them directly. The reasons are the following: {cons} ' if cons is not None else ''}Write the email without subject."""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[
            {"role": "system", "content": core_prompt}
        ]
    )

    return response.choices[0].message.content.strip()
