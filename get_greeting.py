import random
from datetime import datetime

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
