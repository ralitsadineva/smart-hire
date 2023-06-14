import json

def get_google_client_id():
    client_secret = json.load(open('client_secret.json'))
    return client_secret['web']['client_id']

if __name__ == '__main__':
    print(get_google_client_id())
