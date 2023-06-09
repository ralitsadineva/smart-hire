import json

def get_google_client_id():
    client_secret = json.load(open('client_secret.json'))
    print(client_secret['web'])
    print(client_secret['web']['client_id'])
    return client_secret['web']['client_id']

if __name__ == '__main__':
    get_google_client_id()