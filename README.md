This is a Python 3.8 script to load specified receipt data and output it to the screen.

Using command line:
arg1 - json file location (local or web)
arg2 - order of output specified with keys of the input data (default - 'aczebdfg')

Class methods
__init__(arg) - constructs the object from arg data and calculates outputs. type of arg can be local or web JSON location or Python dictionary structure
set_print_order(order) - sets the order of output on the object. order can contain any character that is present in the list of keys of the input data
to_string() - returns the full formatted string
