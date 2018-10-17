#!/usr/bin/env python

from xml.sax.saxutils import escape

from gpxUtil import utf8


class Xml(object):

    def ee(self, element):
        s = "</%s>" % element
        return s

    def ele(self, element, content, attrs=None, end=True, only_when_value=False, cdata=False):
        sa = ""

        if content is None:
            if only_when_value and end:
                return ""

            content = ""
        elif cdata:
            content = self.cdata(utf8(content))
        else:
            content = escape(utf8(content))

        if attrs:
            for a, v in attrs:
                sa += ' %s="%s"' % (utf8(a), utf8(v))

            s = "<%s%s>%s" % (element, sa, content)
        else:
            s =  "<%s>%s" % (element, content)

        if end:
            s += "</%s>" % element

        return s

    def cdata(self, cdata):
        return "<![CDATA[%s]]>" % cdata
    
    
if __name__ == "__main__":
    import sys
    print("%s: I don't do anything standalone" % sys.argv[0])


