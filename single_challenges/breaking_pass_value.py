"""

Modified Python integer object in memory
ctypes is Python's foreign function library that provides C-compatible data types and allows direct memory manipulation. Here's what each part does:

ctypes.memmove(dest, src, size) — Copies size bytes from source to destination memory addresses (like C's memmove):

id(x) + 24 — The destination: memory address of the integer object plus 24-byte offset. This offset points to the ob_digit field in Python's internal PyLongObject structure, which stores the actual integer value.

ctypes.byref(ctypes.c_long(new_value)) — The source: creates a reference to a C long integer containing the new value.

8 — Copies 8 bytes (the size of a 64-bit long).

What this accomplishes: The code directly overwrites the integer's value in memory, bypassing Python's immutability guarantee. This breaks the fundamental assumption that integers are immutable—the same object reference (id(x)) keeps the same address but its value changes from 1000 to 9999.

This is a dangerous low-level hack demonstrating Python's memory model. Don't use this in production code—it violates encapsulation, is platform/version-dependent, and can cause crashes or security issues.

n  ──────────────────────────────────────┐
x (parameter copy) ──────────────────────┤
                                          ▼
                               ┌─────────────────────┐
                               │  PyLongObject @mem  │
                               ├──────────┬──────────┤
                               │ refcount │  ob_type │  offsets 0, 8
                               ├──────────┴──────────┤
                               │      ob_size        │  offset 16
                               ├─────────────────────┤
                               │  ob_digit = 1000    │  offset 24  ← we write here
                               └─────────────────────┘

x and n are different names, but point to the exact same object in memory (id() proves it)
Python copied the reference, not the object
By mutating the object's memory directly with ctypes, both x and n see the change —
because they're looking at the same address

"""
import ctypes

def mutate_int(x, new_value):
    print(f"  id(x) inside function: {id(x)}")      # same address as caller's n
    print(f"  value before: {x}")

    # Write directly to the ob_digit field of the PyLongObject in memory
    ctypes.memmove(id(x) + 24, ctypes.byref(ctypes.c_long(new_value)), 8)

    print(f"  value after:  {x}")

n = 1000  # must be > 256 to avoid intern cache
print(f"Before → n={n},  id: {id(n)}")

mutate_int(n, 9999)

print(f"After  → n={n}, id: {id(n)}")  # same address, mutated value



"""
Python uses pass by object reference for all types (mutable and immutable). However,
 with immutable types, it appears to behave like pass-by-value.

Here's the distinction:

Pass by object reference — Python passes a reference (memory address) to the object, 
not a copy of the value.

Why immutables seem like pass-by-value:

You cannot modify immutable objects in place (integers, strings, tuples are immutable)
If you try to "change" them inside a function, you're actually 
creating a new object and rebinding the local variable
This rebinding only affects the function's local scope, 
not the caller's variable

def change_int(x):
    x = 9999  # Creates NEW object, rebinds local x
    
n = 1000
change_int(n)
print(n)  # Still 1000 — x rebinding didn't affect caller's n

Rebinding means reassigning a variable to point to a different object in memory.

In Python, variables are just names that reference objects.
When you do x = 9999, you're not modifying the existing object—you're making x point to a new object:
Example:

def change_int(x):
    print(f"id(x) at start: {id(x)}")  # points to 1000's object
    x = 9999                            # NOW x points to a DIFFERENT object
    print(f"id(x) after rebind: {id(x)}")  # different address!

n = 1000
print(f"id(n) before: {id(n)}")
change_int(n)
print(f"id(n) after: {id(n)}")  # still same address as before—unchanged!

First n points to integer object at address, say, 0x7f1234
Function change_int receives a reference to that same object
Inside the function, x = 9999 rebinds x to a different object at a new address
The original object n points to is untouched
When the function ends, the rebinding is lost—it only affected the local variable x



But with mutables, you see object reference behavior:

def mutate_list(lst):
    lst.append(999)  # Modifies object IN PLACE
    
my_list = [1, 2, 3]
mutate_list(my_list)
print(my_list)  # [1, 2, 3, 999] — the object itself was modified

The ctypes code is a hack that breaks this rule by directly 
mutating an immutable object in memory
something that's not normally possible in Python.

"""