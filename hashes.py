
def djbhash(a): 
    h = 5381L 
    for i in a: 
        t = (h * 33) & 0xffffffffL 
        h = t ^ i 
    return h 

def fnvhash(a):
    h = 2166136261
    for i in a:
        t = (h * 16777619) & 0xffffffffL
        h = t ^ i
    return h
