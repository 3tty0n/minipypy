from minipypy.objects.baseobject import *

class StdObjSpace(object):

    def __init__(self):
        setup_prebuilt()

    def newint(self, intval):
        if within_prebuilt_index(intval):
            return W_IntObject.PREBUILT[intval]
        return W_IntObject.from_int(intval)

    def newlong(self, longval):
        if within_prebuilt_index(longval):
            return W_LongObject.PREBUILT[longval]
        return W_LongObject.from_int(intval)

    def newstr(self, strval):
        return W_StrObject.from_str(strval)
