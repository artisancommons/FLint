

def read_file(path):
    try:
        with open(path, 'r') as fd:
            return fd.readlines()
    except:
        print(f"failed to read: {path}")
        return [f"Failed to read: {path}"]

def list_to_string(li):
    s = ""
    for i in li:
        if type(i) is list:
            s += list_to_string(i)
            continue
        s += i
    return s
