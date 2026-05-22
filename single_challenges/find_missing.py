
# Online Python - IDE, Editor, Compiler, Interpreter


def find_missing(a: list):
    
    all_elements = set(range(1, len(a) +2 ))
    print(all_elements)
    c = all_elements - set(a)
    return c.pop()
    
x = find_missing([1,4,2, 3])
print(x)
