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
