VERSION = (0, 1)
__version__ = ".".join(map(str, VERSION[0:3])) + "".join(map(str, VERSION[3:]))


from fields import *
