

def read_file(path):
    with open(path, 'r') as fd:
        return fd.readlines()

def list_to_string(li):
    s = ""
    for i in li:
        if type(i) is list:
            s += list_to_string(i)
            continue
        s += i
    return s
