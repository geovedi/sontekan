
def djbhash(a): 
    h = 5381L 
    for i in a: 
        t = (h * 33) & 0xffffffffL 
        h = t ^ i 
    return h 
