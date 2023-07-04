def get_api_key():
    with open('opaikey.txt', 'r') as key:
        return key.read().strip() 
