import string
import random

def URLWithAuthentication(url, id, password):
    if(url.endswith("/")):
       url = url[:-1]
    splitted = url.split("//")
    return f'{splitted[0]}//{id}:{password}@{splitted[1]}'

def serializeParams(params):
    # return 'key1=value1&key2=value2...'
    return ';'.join(list(map(lambda item: item[0]+"="+item[1], params.items())))

def string_generator(size=10, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))