import os
import urllib2
import ufoLib

# Extract documentation strings from the UFO specification site

import urllib2

url = "http://unifiedfontobject.org/versions/ufo2/fontinfo.html"
docsite = urllib2.urlopen(url)
text = docsite.read()

usableLines = None
for line in text.splitlines():
    if line.strip() == "<h2>Converting fontinfo.plist in UFO 1 to fontinfo.plist in UFO 2</h2>":
        break
    if line.strip() == "<h2>Specification</h2>":
        usableLines = []
    if usableLines is None:
        continue
    usableLines.append(line)

attributeDocumentation = dict.fromkeys(ufoLib.fontInfoAttributesVersion2)

unencodes = {
    "&#8217;" : "'",
    "&#8220;" : '"',
    "&#8221;" : '"',
    "&#8211;" : "-",
    "<em>" : "",
    "</em>" : "",
    "<span class=\"caps\">" : "",
    "</span>" : "",
    "<strong>" : "",
    "</strong>" : "",
}

listening = False
currentAttr = []
for line in usableLines:
    if line == "<tr>":
        listening = True
        continue
    if line == "</tr>":
        listening = False
        if len(currentAttr) == 3:
            attr, typ, doc = currentAttr
            if attr in attributeDocumentation:
                assert attributeDocumentation[attr] is None
                attributeDocumentation[attr] = "%s This should be a %s. Setting this will post an *Info.Changed* notification." % (doc, typ)
        currentAttr = []
    if listening:
        if line.startswith("<td>"):
            line = line.replace("<td>", "").replace("</td>", "")
            for before, after in unencodes.items():
                line = line.replace(before, after)
            line = line.replace('"', '\\"')
            currentAttr.append(line)

assert None not in attributeDocumentation.values()

# print the code

print "# this file was generated by %s." % os.path.basename(__file__)
print "# this file should not be edited by hand."
print

print "from warnings import warn"
print "from robofab import ufoLib"
print "from defcon.objects.base import BaseObject"
print
print

print "class Info(BaseObject):"

doc = """
    \"\"\"
    This object represents info values.

    **This object posts the following notifications:**

    ============  ====
    Name          Note
    ============  ====
    Info.Changed  Posted when the *dirty* attribute is set.
    ============  ====

    **Note:** The documentation strings here were automatically generated
    from the `UFO specification <http://unifiedfontobject.org/filestructure/fontinfo.html>`_.
    \"\"\"
"""
print doc

print "    _notificationName = \"Info.Changed\""
print

print "    def __init__(self):"
print "        super(Info, self).__init__()"

for attr in sorted(ufoLib.fontInfoAttributesVersion2):
    print "        self._%s = None" % attr
print

print "    # ----------"
print "    # Properties"
print "    # ----------"
print

defaults = dict(
    postscriptBlueValues=[],
    postscriptOtherBlues=[],
    postscriptFamilyBlues=[],
    postscriptFamilyOtherBlues=[],
    postscriptStemSnapH=[],
    postscriptStemSnapV=[],
)

for attr in sorted(ufoLib.fontInfoAttributesVersion2):
    print "    def _get_%s(self):" % attr
    if attr in defaults:
        print "        if self._%s is None:" % attr
        print "            return %s" % repr(defaults[attr])
        print "        return self._%s" % attr
    else:
        print "        return self._%s" % attr
    print
    print "    def _set_%s(self, value):" % attr
    print "        if value is None:"
    print "            self._%s = None" % attr
    print "        else:"
    print "            valid = ufoLib.validateFontInfoVersion2ValueForAttribute(\"%s\", value)" % attr
    print "            if not valid:"
    print ("                raise ValueError(\"Invalid value (___) for attribute %s.\" %% repr(value))" % (attr)).replace("___", "%s")
    print "            else:"
    print "                self._%s = value" % attr
    print "        self.dirty = True"
    print
    print "    %s = property(_get_%s, _set_%s, doc=\"%s\")" % (attr, attr, attr, attributeDocumentation[attr])
    print

print "    # ---------------------"
print "    # Deprecated Attributes"
print "    # ---------------------"
print

for attr in sorted(ufoLib.deprecatedFontInfoAttributesVersion2):
    print "    def _get_%s(self):" % attr
    print "        newAttr, n = ufoLib.convertFontInfoValueForAttributeFromVersion1ToVersion2(\"%s\", None)" % attr
    print "        warn(\"The attribute %s has been deprecated.\")" % attr
    print "        return getattr(self, newAttr)"
    print
    print "    def _set_%s(self, value):" % attr
    print "        newAttr, newValue = ufoLib.convertFontInfoValueForAttributeFromVersion1ToVersion2(\"%s\", value)" % attr
    print "        warn(\"The attribute %s has been deprecated.\")" % attr
    print "        setattr(self, newAttr, newValue)"
    print
    print "    %s = property(_get_%s, _set_%s)" % (attr, attr, attr)
    print

