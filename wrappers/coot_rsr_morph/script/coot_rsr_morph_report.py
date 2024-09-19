from report.CCP4ReportParser import *
import sys

class coot_rsr_morph_report(Report):
    # Specify which gui task and/or pluginscript this applies to
    TASKNAME = 'coot_rsr_morph'
    RUNNING = False
    def __init__(self,xmlnode=None,jobInfo={},jobStatus=None,**kw):
        Report. __init__(self,xmlnode=xmlnode,jobInfo=jobInfo,**kw)
        clearingDiv = self.addDiv(style="clear:both;")
        summaryFold = self.addFold(label="Log File", initiallyOpen=False)
        logNodes = self.xmlnode.findall('Log')

        jobDirectory = jobInfo['fileroot']
        with open(os.path.join(jobDirectory,"stdout.txt")) as f:
            t = f.read()
            summaryDiv = summaryFold.addPre(text=t)
