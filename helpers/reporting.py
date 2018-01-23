'''
Created on 23 Jan 2018

@author: baecks
'''

from bpy.types import Operator

class Reporter():
    def __init__(self, addon_object):
        self.addon_object = addon_object

    def _report(self, tp, msg):
        self.addon_object.report(tp, msg)
        print (msg)
        
    def info(self, msg):
        self._report({'INFO'}, msg)
        
    def error(self, msg):
        self._report({'ERROR'}, msg)

class ReportingOperator(Operator):
    def __init__(self):
        super(ReportingOperator, self).__init__()
        self._reporter = Reporter(self)
        
    def info(self, msg):
        self._reporter.info(msg)
        
    def error(self, msg):
        self._reporter.error(msg)