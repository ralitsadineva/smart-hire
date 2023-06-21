def convert_to_dict(response):
    response_string = response #.strip('{}') #.choices[0].text.strip()
    response_dict = {}

    for line in response_string.split('\n'):
        line = line.strip().strip(',')
        
        if line == '':
            continue
        
        key, value = line.split(':', 1)
        
        key = key.strip().capitalize()
        value = value.strip().capitalize()

        if '/' in value:
            value = value.split('/')[0].strip()
        if value.isdigit():
            value = int(value)
        
        response_dict[key] = value
    
    return response_dict
