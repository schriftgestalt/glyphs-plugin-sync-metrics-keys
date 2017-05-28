# encoding: utf-8

###########################################################################################################
#
#
#	Sync Metrics Keys
#
#   A simple Plugin for Glyphs App to keep referenced side bearings in sync
#   Install > View > Show Sync Metrics Keys
#
#   (c) Johannes "kontur" Neumeier 2017
#
#
###########################################################################################################


from GlyphsApp.plugins import *
import re

class MetricsAutoUpdate(ReporterPlugin):


    def settings(self):
        # setting the visible name, displayed as "Show Sync Metrics Key"
        # semantically, using the ReporterPlugin for this functionablity is incorrect,
        # but it allows for easy toggling
        self.menuName = 'Sync Metrics Keys'


    def start(self):
        # no logging in production version
        self.logging = False


    # use local debugging flag to enable or disable verbose output
    def log(self, message):
        if self.logging:
            self.logToConsole(message)
        

    def updateMetrics(self, glyph):
        self.log("updateMetrics")
        
        # keeping the current glyph in sync with any linked metrics keys
        self.syncGlyphMetrics(glyph)

        # check if the current glyph is a metrics key in other glyphs, and if so, update them

        # TODO note that this is not recursive; if h references n, but b references h, 
        # editing n will not update b, because it does not reference n directly
        linkedGlyphs = self.findGlyphsWithMetricsKey(glyph)
        if len(linkedGlyphs) > 0:
            for linkedGlyph in linkedGlyphs:
                self.syncGlyphMetrics(linkedGlyph)


    # shortcut for syncing the metrics in all layers in a glyph
    def syncGlyphMetrics(self, glyph):
        self.log("syncGlyphMetrics")
        self.log("syncing glyph %s" % str(glyph.name))
        try:
            for layer in glyph.layers:
                self.log("layer name %s" % str(layer.name))
                layer.syncMetrics()

        except Exception as e:
            self.log("Error: %s" % str(e))


    # not differentiating here between left or right
    # if either side is a reference, return it for processing
    def findGlyphsWithMetricsKey(self, key):
        self.log("findGlyphsWithMetricsKey")
        referencedGlyphs = []
        try:
            for glyph in Glyphs.font.glyphs:
                self.log("Check %s linked %s (metric keys: %s, %s)?" % (glyph.name, key.name, glyph.leftMetricsKey, glyph.rightMetricsKey))

                if (glyph.name is key.name):
                    # skip checking sidebearing keys for the glyph of same name, obviously
                    continue

                # looking for a reference to the key in the glyph's metrics keys us a regular
                # expression that looks for the key only when next to non-alphabetic character
                # i.e. when used in formulas, like =n-20 or =|n, but will not match when the
                # key has other alphabetic characters next to it, like not matching key n in value ntilde
                # adding re.MULTILINE will match the $ end of line before the "non-alphabetic", which
                # isn't satisfied by "end of line/string" otherwise
                regex = "[^a-zA-Z](" + re.escape(key.name) + ")$|[^a-zA-Z]"
                pattern = re.compile(regex, re.MULTILINE)

                # also match if the key and the reference simply are equal (no equations used)
                # LSB
                if glyph.leftMetricsKey is not None:
                    if pattern.search(glyph.leftMetricsKey) is not None or glyph.leftMetricsKey == key.name:
                        self.log("LSB links")
                        referencedGlyphs.append(glyph)

                #RSB
                if glyph.rightMetricsKey is not None:
                    if pattern.search(glyph.rightMetricsKey) is not None or glyph.rightMetricsKey == key.name:
                        self.log("RSB links")
                        referencedGlyphs.append(glyph)

        except Exception as e:
            self.log("Error: %s" % str(e))

        self.log(referencedGlyphs)

        return referencedGlyphs


    def foreground(self, layer):
        self.updateMetrics(layer.parent)