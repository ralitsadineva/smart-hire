import random
from datetime import datetime
from constants import LOGIN_TYPE_PASSWORD

def memoize(func):
    cache = {}
    
    def wrapper():
        if 'result' not in cache:
            cache['result'] = func()
        return cache['result']
    
    return wrapper

def get_name(user):
    if user[5]==LOGIN_TYPE_PASSWORD:
        return user[2]
    else:
        return user[1].split('@')[0]

def get_greeting():
    greetings = ["Hello", "Welcome back"]
    current_hour = datetime.now().hour

    if 0<= current_hour < 12:
        greetings.append("Good morning")
    elif 12 <= current_hour < 18:
        greetings.append("Good afternoon")
    else:
        greetings.append("Good evening")

    return random.choice(greetings)

def check_empty(str):
    if str == '':
        return None
    return str

def convert_to_dict(response):
    response_dict = {}

    for line in response.split('\n'):
        line = line.strip().strip(',')
        
        if line == '':
            continue
        
        try:
            key, value = line.split(':', 1)
        except ValueError:
            continue
        
        key = key.strip().capitalize()
        value = value.strip().capitalize()

        if '/' in value:
            value = value.split('/')[0].strip()
        if value.isdigit():
            value = int(value)
        
        response_dict[key] = value
    
    return response_dict

def convert_to_dict_extracted(response):
    response_dict = {}

    for line in response.split('\n'):
        line = line.strip().strip(',')
        
        if line == '':
            continue
        
        try:
            key, value = line.split(':', 1)
        except ValueError:
            continue
        
        key = key.strip().capitalize()
        value = value.strip()

        if value.isdigit():
            value = int(value)
        
        response_dict[key] = value
    
    return response_dict

def convert_pros_cons(response):
    split_response = [item for item in response.split('\n\n') if item.strip()]

    pros = split_response[0].split('\n', 1)[1]
    cons = split_response[1].split('\n', 1)[1]
    return pros, cons
