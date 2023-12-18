from __future__ import print_function

import sys
#from lxml import etree
from xml.etree import ElementTree as ET
from report.CCP4ReportParser import *

from wrappers.refmac_i2.script import refmac_report
from wrappers.validate_protein.script import validate_protein_report
import base64

class prosmart_refmac_report(Report):
    # Specify which gui task and/or pluginscript this applies to
    TASKNAME = 'prosmart_refmac'
    RUNNING = True
    SEPARATEDATA=True

    def __init__(self,*args,**kw):
        super(prosmart_refmac_report,self).__init__(*args,**kw)
        #print 'prosmart_refmac_report',self,self.jobStatus
        self.outputXml = self.jobStatus is not None and self.jobStatus.lower().count('running')
        if self.jobStatus is not None and not self.jobStatus.lower().count('running'): self.outputXml = False
        if self.jobStatus is not None and self.jobStatus.lower() == 'nooutput': return
        if self.jobStatus is not None and self.jobStatus.lower() == 'unsatisfactory':
            self.drawUnsatisfactory(self)
        else:
            self.drawContents()

    def drawUnsatisfactory(self, parent=None):
        #Currently, the only "unsatisfactory" outcome is dur to ligand encountered whicl "make ligand exit" active
        if parent is None: parent=self
        parent.addDiv(style='clear:both;')
        parent.addText(text='Refmac died because it encountered a ligand not present in the monomer libraries it has read (i.e. the default CCP4 libraries plus any library you provided through the GUI). To continue, you have a number of options.')
        #parent.append('<br/>')
        #parent.addText(text='1) Review and accept the ligand dictionary autogenerated by refmac: if the following sketch , and the data presented by viewing the file "Pictures of ligand prepared by refmac" (see below)  suggest that the ligand has been appropriately characterised, then you can use the autogenerated library in a subsequent refmac job')
        parent.append('<br/>')
        parent.addText(text='1) Use the make ligand pipeline to generate an acedrg description of your ligand.  For now, the resulting ligand will need to be rebuilt into your model through Coot, since atom names may not match those in the original PDB file')
        parent.append('<br/>')
        parent.addText(text='2) View the input PDB file in Coot, and use COOT  to generate a ligand geometry dictionary.  This is a neat way to work and keep atom names consistent with the starting point.  Ligands generated through the coot ligand builder will be captured into the ccp4i2 database and can be exported from there on the coot task report page.')
        try:
            if len(self.xmlnode.findall('svg')) > 0:
                sketchDiv = parent.addDiv(style="width:350px; height:350px; border:1px solid black;")
                sketchDiv.append(ET.tostring(self.xmlnode.findall('.//svg')[0]))
        except:
            pass

    def drawContents(self):
        xmlnode = self.xmlnode
        self.addDiv(style='clear:both;')
        #Found ligands
        xmlPath = './/LIGANDS'
        xmlNodes = xmlnode.findall(xmlPath)
        if len(xmlNodes)>0:
          clearingDiv = self.addDiv(style="clear:both;")
          ligandFold = self.addFold(label='New ligand(s) found',brief='Ligand')
          text = '<span style="font-size:110%">Geometry restaints for the following novel ligands have been added to the project ligand geometry file:'
          ligandNodes = xmlNodes[0].findall('ligand')
          for lig in ligandNodes:
            text = text + ' ' + str(lig.text)
          ligandFold.append(text + '</span>')

        #PROSMART results (if any)
        xmlPath = './/PROSMART'
        xmlNodes = xmlnode.findall(xmlPath)
        if len(xmlNodes)>0:
            clearingDiv = self.addDiv(style="clear:both;")
            prosmartFold = self.addFold(label='Prosmart results',brief='Prosmart')
            prosmartFold.append('<span style="font-size:110%">HTML Results will be displayed in browser </span>')
            prosmartFold.append('<a href="job_1/ProSMART_Results.html">Open Results</a>')

        #ERRORLINES if any
        errorLineNodes = xmlnode.findall('.//ErrorLine')
        if len(errorLineNodes)>0:
            errorFold = self.addFold(label='Refmac reported errors', initiallyOpen=True,brief='Errors')
            errorFoldDiv = errorFold.addDiv()
            for errorLineNode in errorLineNodes:
                errorFoldDiv.addText(text = errorLineNode.text)
                errorFoldDiv.append('<br/>')

        #Raid the refmac report of finished jobs
        summaryFold = self.addFold(label='Refinement', initiallyOpen=True,brief='Refinement')
        clearingDiv = self.addDiv(style="clear:both;")
        try:
            weightText = self.xmlnode.findall('.//WeightUsed')[-1].text
            self.addPre(outputXml=self.outputXml, internalId="WeightUsed", text="Current weight applied to X-ray term is "+weightText,style="font-size:125%;")
        except:
            weightText = ""

        refmacReport = None
        refmacReportNode0 = None
        try:
            refmacReportNode0 =xmlnode.findall('.//RefmacWeight/REFMAC')[0]
        except:
            try:
                # probably never get here....
                refmacReportNode0 = xmlnode.findall('.//RefmacPostCootInProgress')[0]
            except:
                try:
                    refmacReportNode0 = xmlnode.findall('.//RefmacInProgress')[0]
                except:
                    pass
        if refmacReportNode0 is not None:
            refmacReport = refmac_report.refmac_report(xmlnode=refmacReportNode0, jobStatus='nooutput', jobInfo=self.jobInfo)

        topElementsDiv = summaryFold.addDiv(style='width:800px; height:270px;overflow:auto;')
        if refmacReport is not None and not self.jobStatus.lower().count('running'):
            refmacReport.addScrollableDownloadableTable1(parent=topElementsDiv)
        else:
            self.addProgressTable(topElementsDiv, xmlnode)

        self.addProgressGraph(topElementsDiv, xmlnode)

        try:
            cootAddWatersNode = xmlnode.findall('.//CootAddWaters')[0]
            clearingDiv = self.addDiv(style="clear:both;")
            self.addText(text = cootAddWatersNode.text)
            clearingDiv = self.addDiv(style="clear:both;")
        except:
            pass

        if refmacReport is not None: refmacReport.addTwinningAnalysis(self)

        refmacWeights = xmlnode.findall('.//RefmacWeight')
        if len(refmacWeights) > 1:
            self.addByWeightResults(self, xmlnode)

        if not self.jobStatus.lower().count('running'):
            clearingDiv = self.addDiv(style="clear:both;")
            refmacReport.addTables(parent=self)
            if self.jobStatus.lower() != 'subjob':
                objectMap = {}
                #Use DICTOUT or DICTIN if they have been harvested to define monomer geometry in pictures
                if self.jobInfo['filenames'].get('DICTOUT', None) is not None:
                    objectMap['DICT'] = 'DICTOUT'
                elif self.jobInfo['filenames'].get('DICT', None) is not None:
                    objectMap['DICT'] = 'DICT'
                refmacReport.addRefinementPictures(jobInfo=self.jobInfo, parent=self, objectNameMap=objectMap)
            refmacReport.addSymmetryAnalysis(self)
            refmacReport.addOutlierAnalysis(self)
            refmacReport.addSmartieGraphs(self)
            self.addDiv(style="clear:both;")

            try:
               validateReport = None
               validateReportNode = xmlnode.findall(".//Validation")[0]
               if validateReportNode is not None:
                  validateReport = validate_protein_report.validate_protein_report(xmlnode=validateReportNode, jobStatus='nooutput', jobInfo=self.jobInfo)

               if validateReport is not None:
                  try:
                     if len(validateReportNode.findall ( ".//Iris" ))>0 and validateReportNode.findall ( ".//Iris" )[0].text != "" :
                        irisFold = self.addFold ( label="Iris report", initiallyOpen=False, brief='Iris' )
                        validateReport.add_iris_panel(parent=irisFold)
                  except:
                     self.addText("Warning - Iris report failed")
                        
                  try:
                     if len(validateReportNode.findall ( ".//B_factors" ))>0 and validateReportNode.findall ( ".//B_factors" )[0].text != "" :
                        baverageFold = self.addFold ( label="B-factor analysis", initiallyOpen=False )
                        validateReport.add_b_factors(parent=baverageFold)
                  except:
                     self.addText("Warning - B-factor analysis failed")

                  try:
                     if len(validateReportNode.findall ( ".//Molprobity" ))>0 and validateReportNode.findall ( ".//Molprobity" )[0].text != "" :
                        molprobityFold = self.addFold ( label="MolProbity analysis", initiallyOpen=False )
                        validateReport.add_molprobity(parent=molprobityFold)
                  except:
                     self.addText("Warning - MolProbity analysis failed")

                  try:
                     if len(validateReportNode.findall ( ".//Ramachandran" ))>0 and validateReportNode.findall ( ".//Ramachandran" )[0].text != "" :
                        ramachandranFold = self.addFold ( label="Ramachandran plots", initiallyOpen=False )
                        validateReport.add_ramachandran(parent=ramachandranFold)
                  except:
                     self.addText("Warning - Ramachandran plot generation failed")           
                  
            except:
               traceback.print_exc()
            clearingDiv = self.addDiv(style="clear:both;")

            try:
                molprobityOutputNode = xmlnode.findall('.//Molprobity/Output')[0]
                molprobityFold = self.addFold(label='Molprobity analysis', initiallyOpen=False,brief='Molprobity')
                molprobityFold.addPre(text = molprobityOutputNode.text)
                clearingDiv = self.addDiv(style="clear:both;")
            except:
                pass

        refmacReport2 = None
        try:
            if self.jobStatus.lower().count('running'):
                refmacReportNode1 = xmlnode.findall('.//RefmacPostCootInProgress')[0]
            else:
                refmacReportNode1 = xmlnode.findall('.//refmacPostCoot/REFMAC')[0]
            RFactorNodes2 = refmacReportNode1.findall('.//Overall_stats/stats_vs_cycle/new_cycle/r_factor')

            if refmacReportNode1 is not None:
                summaryFold2 = self.addFold(label='Refinement after Running Coot Add waters', initiallyOpen=True,brief='After Coot scripts')
                clearingDiv2 = self.addDiv(style="clear:both;")
                refmacReport2 = refmac_report.refmac_report(xmlnode=refmacReportNode1, jobStatus='nooutput', jobInfo=self.jobInfo)
                topElementsDiv2 = summaryFold2.addDiv(style='width:800px; height:270px;overflow:auto;')
                if refmacReport2 is not None and not self.jobStatus.lower().count('running'):
                    refmacReport2.addScrollableDownloadableTable1(parent=topElementsDiv2,internalId='Table1PostCoot')
                else:
                    self.addProgressTable(topElementsDiv2, xmlnode,internalId='Table1PostCootRunning')
                if self.jobStatus.lower().count('running'):
                    self.addProgressGraph(topElementsDiv2, refmacReportNode1,internalId="SummaryGraphPostCoot",tag="RefmacPostCootInProgress")
                else:
                    self.addProgressGraph(topElementsDiv2, refmacReportNode1,internalId="SummaryGraphPostCoot",tag="refmacPostCoot/REFMAC")
                    # Could also add other graphs.
                    """
                    refmacReport2.addSmartieGraphs(self,internalIdPrefix='postCoot')
                    """
        except:
             pass

        linkNodes = xmlnode.findall('.//Links/Link')
        if len(linkNodes)>0:
            linkFold = self.addFold(label='Link information', initiallyOpen=True,brief='Links')
            linkDiv = linkFold.addDiv(style='border:0px solid black; width:700px; overflow:auto;')
            preText = "Status     Link   Mon1  At1  alt1  ch1   res1  Mon2  At2  alt2  Ch2   Res2   distM   distI\n"
            for link in linkNodes:
                print(link)
                preText += link.text + "\n"
            pre = linkDiv.addPre()
            pre.text = preText

        verdictNodes = xmlnode.findall('.//Verdict')
        if len(verdictNodes)>0:
            from lxml.html.clean import Cleaner
            
            cleaner = Cleaner(page_structure=True,
                   meta=True,
                   embedded=True,
                   links=True,
                   style=True,
                   processing_instructions=True,
                   inline_style=True,
                   scripts=True,
                   javascript=True,
                   comments=True,
                   frames=True,
                   forms=True,
                   annoying_tags=True,
                   remove_unknown_tags=True,
                   safe_attrs_only=True,
                   safe_attrs=frozenset(['src','color', 'href', 'title', 'class', 'name', 'id']),
                   remove_tags=('span', 'font', 'div','br')
                   )
            
            verdictFold = self.addFold(label='Verdict', initiallyOpen=True,brief='Verdict')

            topDiv = verdictFold.addDiv(style='border:0px solid blue; width:700px; overflow:auto;')
            verdictDiv = topDiv.addDiv(style='border:0px solid black; height:130px; width:200px; position: relative; float: left;')
            verdictWidgetDiv = verdictDiv.addDiv(style='border:0px solid red; height:100px; width:200px; position: absolute;top: 0;')
            verdictScoreDiv = verdictDiv.addDiv(style='border:0px solid green; height:30px; width:200px; position: absolute;bottom: 0;')
            verdictWidgetDiv.append('<canvas id="myScoreWidgetCanvas" width="150" height="100"></canvas>')
            verdictScoreDiv.addText(text="Verdict score: %.2f" % float(verdictNodes[0].findall("verdict_score")[0].text))
            verdictFold.append('<script>var score_widget = new scoreWidget("myScoreWidgetCanvas",'+str(float(verdictNodes[0].findall("verdict_score")[0].text)/100.)+');</script>')
            messageDiv = topDiv.addDiv(style='border:0px solid magenta; width:400px; float: left;')
            messageDiv.append(cleaner.clean_html(base64.b64decode(verdictNodes[0].findall("verdict_message")[0].text)))

            RFreeNode = xmlnode.findall('.//RefmacWeight/REFMAC/Overall_stats/stats_vs_cycle/new_cycle[last()]/r_free')
            final_rfree = 'NA'
            if len(RFreeNode)>0: final_rfree = RFreeNode[0].text
            ClashNode = xmlnode.findall('.//Validation/Molprobity/Summary/Clashscore')
            final_clash = 'NA'
            if len(ClashNode)>0: final_clash = ClashNode[0].text

            bottomLineDiv = verdictFold.addDiv(style='border:0px solid black; width:700px; overflow:auto;')
            bottomLineDiv.append(cleaner.clean_html(base64.b64decode(verdictNodes[0].findall("bottomline")[0].text)))
            tableText = "<table>\n"
            tableText += "<tr><td>R-Free:</td><td>"+final_rfree+"</td><td>(mean in resolution bin: "+verdictNodes[0].findall("meanRfree")[0].text+")</td></tr>\n"
            tableText += "<tr><td>Clashscore:</td><td>"+final_clash+"</td><td>(median in resolution bin: "+verdictNodes[0].findall("medianClash")[0].text+")</td></tr>\n"
            tableText += "<tr><td>Ramachandran outliers:</td><td>"+verdictNodes[0].findall("ramaOutliers")[0].text+" %</td></tr>\n"
            tableText += "</table>\n"
            bottomLineDiv.append(tableText)
            
            verdict_suggestion_values = {}
            verdict_suggestion_values["NCYCLES"] = "Number of cycles:"
            verdict_suggestion_values["NTLSCYCLES"] = "Number of TLS cycles:"
            verdict_suggestion_values["WEIGHT"] = "Fix geometry weight to:"
            verdict_suggestion_values["JELLY_DIST"] = "Jelly body restraint max distance:"
            verdict_suggestion_values["JELLY_SIGMA"] = "Jelly body restraint sigma:"

            verdict_suggestion_opt = {}
            verdict_suggestion_opt["TLSMODE"] = {"AUTO":"Use automatic TLS parameterisation."}
            verdict_suggestion_opt["B_REFINEMENT_MODE"] = {"ISOT":"Use isotropic B-factors.","ANIS":"Use anisotropic B-factors","OVER":"Use overall B-factor","MIXED":"Mixed isotropic/anisotropic B-factors"}
            verdict_suggestion_opt["USE_NCS"] = {"True":"Use NCS restraints.","False":"Disable NCS restraints."}
            verdict_suggestion_opt["USE_JELLY"] = {"True":"Use jelly body restraints.","False":"Disable jelly body restraints."}
            verdict_suggestion_opt["BFACSETUSE"] = {"True":"Reset atomic B-factors.","False":"Do not reset atomic B-factors."}
            verdict_suggestion_opt["WEIGHT_OPT"] = {"AUTO":"Use automatic geometry weight optimisation."}
            verdict_suggestion_opt["HYDR_USE"] = {"True":"Generate and use riding hydrogens.","False":"Do not use riding hydrogens."}
            
            if len(verdictNodes[0].findall("suggestedParameters")[0]) > 0:
                suggestedDiv = verdictFold.addDiv(style='border:0px solid black; width:700px; overflow:auto;')
                suggestedDiv.append("<p>It is suggested that you rerun with the following suggested parameters:</p>")
                tableText = "<table>\n"
                for child in verdictNodes[0].findall("suggestedParameters")[0]:
                   if child.tag in verdict_suggestion_values:
                      tableText += "<tr><td>"+verdict_suggestion_values[child.tag]+"</td><td>"+child.text+"</td></tr>\n"
                   elif child.tag in verdict_suggestion_opt:
                      if child.text in verdict_suggestion_opt[child.tag]:
                         tableText += "<tr><td>"+verdict_suggestion_opt[child.tag][child.text]+"</td><td></td></tr>\n"
                tableText += "</table>\n"
                suggestedDiv.append(tableText)
                suggestedDiv.append('<p><b>You can do this by clicking the <i>"Re-run with suggested parameters"</i> button at the bottom of this report.</b></p>')

        self.showWarnings()

    def addProgressGraph(self, parent, xmlnode,internalId="SummaryGraph",tag="RefmacInProgress"):
        if len(self.xmlnode.findall(tag))>0:
            progressGraph = parent.addFlotGraph(title="Running refmac",select=tag+"/Cycle",style="height:250px; width:400px;float:left;border:0px;",outputXml=self.outputXml,internalId=internalId)
            progressGraph.addData(title="Cycle",    select="number")
            progressGraph.addData(title="R_Factor", select="r_factor")
            progressGraph.addData(title="R_Free",  select="r_free")
            plot = progressGraph.addPlotObject()
            plot.append('title','Running refmac R-factors')
            plot.append('plottype','xy')
            plot.append('yrange', rightaxis='false')
            plot.append( 'xlabel', 'Cycle' )
            plot.append( 'xintegral', 'true' )
            plot.append( 'ylabel', 'R-factor' )
            plot.append( 'rylabel', 'Geometry' )
            for coordinate, colour in [(2,'blue'),(3,'green')]:
                plotLine = plot.append('plotline',xcol=1,ycol=coordinate,rightaxis='false',colour=colour)

            rmsBonds = self.xmlnode.findall('.//'+tag+'/Cycle/rmsBonds')
            if len(rmsBonds)> 0:
                plot.append('yrange', rightaxis='true')
                cycleNodes = self.xmlnode.findall('.//'+tag+'/Cycle')
                data = []
                for cycleNode in cycleNodes:
                    try: data.append(cycleNode.findall('rmsBonds')[0].text)
                    except: data.append(None)
                progressGraph.addData(title="rmsBonds",  data=data)
                plotLine = plot.append('plotline',xcol=1,ycol=4,rightaxis='true',colour='red')

    def addProgressTable(self, parent, xmlnode,internalId='SummaryTable'):
        if internalId=='Table1PostCootRunning':
            tag = "RefmacPostCootInProgress"
        else:
            tag = "RefmacInProgress"
        progressTableDiv = parent.addDiv(style='border:0px solid black; height:250px; width:260px; float:left; margin-top:1px; margin-right:0px;overflow:auto;')
        if len(xmlnode.findall("RefmacInProgress"))>0:
            xmlPath = './/'+tag+'/Cycle'
            xmlNodes = xmlnode.findall(xmlPath)
            nCycles = len(xmlNodes)
            print("addProgressTable nCycles",nCycles)
            if nCycles>0:
                nodeData = {'number':['-']*nCycles,'Rfactor':['-']*nCycles,'Rfree':['-']*nCycles,'rmsBonds':['-']*nCycles}
                cycleNodes = self.xmlnode.findall('.//'+tag+'/Cycle')
                for iCycleNode, cycleNode in enumerate(cycleNodes):
                    try: nodeData['number'][int(cycleNode.findall('number')[0].text)] = cycleNode.findall('number')[0].text
                    except: pass
                    try: nodeData['Rfactor'][int(cycleNode.findall('number')[0].text)] = cycleNode.findall('r_factor')[0].text
                    except: pass
                    try: nodeData['Rfree'][int(cycleNode.findall('number')[0].text)] = cycleNode.findall('r_free')[0].text
                    except: pass
                    try: nodeData['rmsBonds'][int(cycleNode.findall('number')[0].text)] = cycleNode.findall('rmsBonds')[0].text
                    except: pass

                # Get indices of nodes to include in the current table
                offset = 1
                if nodeData['Rfactor'][nCycles-1] == '-': offset = 2
                nodeSelect = [0, nCycles-offset-1, nCycles-offset]
                if nCycles-offset <= 0: nodeSelect = [0]
                if nCycles-offset == 1: nodeSelect = [0, 1]
                print("nodeSelect",nodeSelect)

#                selectString = "//RefmacOptimiseWeight/"+tag+"/Cycle[1]"
#                for i in range(2,nCycles):
#                    selectString += " | //RefmacOptimiseWeight/"+tag+"/Cycle[%d]" % i
                progressTable = progressTableDiv.addTable(style="height:250px; width:260px;float:left;", outputXml=self.outputXml, internalId=internalId)
#                progressTable.addData(title="Cycle", select="number")
#                progressTable.addData(title="R-factor", select="r_factor")
#                progressTable.addData(title="R-free",   select="r_free",   expr="x if float(x)>=0.0 else '-'")
                print("number",[nodeData['number'][i] for i in nodeSelect])
                print("Rfactors",[nodeData['Rfactor'][i] for i in nodeSelect])
                print("Rfree",[nodeData['Rfree'][i] for i in nodeSelect])
                print("rmsBonds",[nodeData['rmsBonds'][i] for i in nodeSelect])
                progressTable.addData(title="Cycle", data=[nodeData['number'][i] for i in nodeSelect])
                progressTable.addData(title="R-factor", data=[nodeData['Rfactor'][i] for i in nodeSelect])
                rfree_data = [nodeData['Rfree'][i] for i in nodeSelect]
                rmsBond_data = [nodeData['rmsBonds'][i] for i in nodeSelect]
                if not rfree_data.count('-') == len(rfree_data):
                   progressTable.addData(title="R-free",   expr="x if float(x)>=0.0 else '-'", data=rfree_data)
                if not rmsBond_data.count('-') == len(rmsBond_data):
                   progressTable.addData(title="Bond RMSD",   expr="x if float(x)>=0.0 else '-'", data=rmsBond_data)

#                rmsBonds = self.xmlnode.findall('.//'+tag+'/Cycle/rmsBonds')
#                if len(rmsBonds)> 0:
#                    cycleNodes = self.xmlnode.findall('.//'+tag+'/Cycle')
#                    data = []
#                    for iCycleNode, cycleNode in enumerate(cycleNodes):
#                        if iCycleNode == 0 or iCycleNode == nCycles-2 or iCycleNode == nCycles-1:
#                            try: data.append(cycleNode.findall('rmsBonds')[0].text)
#                            except: data.append('-')
#                    progressTable.addData(title="RMS Deviation", subtitle="Bond", data=data)

    def addByWeightResults(self, parent, xmlnode):
        if parent is None: parent = self
        if True:# FIXME len(self.xmlnode.findall("./RefmacOptimiseWeight"))>0:
            #I *do not know* why This is needed
            clearingDiv = parent.addDiv(style="clear:both;")
            byWeightsFold = parent.addFold(label="Results by weight",initiallyOpen=True,brief='By weight')

            #Sort refmacweight nodes in order of increasing weight parameter
            refmacWeightNodes = list(self.xmlnode.findall(".//RefmacWeight"))
            sortedRefmacNodes = sorted(refmacWeightNodes, key=lambda residue: float(residue.findall("weight")[-1].text))
            rootNode = self.xmlnode
            #Remove unsorted nodes and put in sorted ones
            for refmacWeightNode in refmacWeightNodes:
                rootNode.remove(refmacWeightNode)
            for sortedRefmacNode in sortedRefmacNodes:
                rootNode.append(sortedRefmacNode)

            endpointSummaryTable = byWeightsFold.addTable(select=".//RefmacWeight",style="width:260px;height:250px; float:left;")
            endpointSummaryTable.addData(title="Weight", select="weight")
            endpointSummaryTable.addData(title="R-factor", select="REFMAC/Overall_stats/stats_vs_cycle/new_cycle[last()]/r_factor")
            endpointSummaryTable.addData(title="R-free",   select="REFMAC/Overall_stats/stats_vs_cycle/new_cycle[last()]/r_free",   expr="x if float(x)>=0.0 else '-'")
            endpointSummaryTable.addData(title="RMS Deviations", subtitle="Bond", select="REFMAC/Overall_stats/stats_vs_cycle/new_cycle[last()]/rmsBOND", expr="x if float(x)>=0.0 else '-'")
            endpointSummaryTable.addData(title="RMS Deviations", subtitle="Angles", select="REFMAC/Overall_stats/stats_vs_cycle/new_cycle[last()]/rmsANGLE", expr="x if float(x)>=0.0 else '-'")

            byWeightGraph = byWeightsFold.addFlotGraph(title='Stats by weight ', select="RefmacWeight/REFMAC/Overall_stats/stats_vs_cycle/new_cycle[last()]",style="width:400px;height:250px;float:left;")
            byWeightGraph.addData(title="Weight",    select=".//RefmacWeight/weight")
            byWeightGraph.addData(title="R_Factor", select="r_factor")
            byWeightGraph.addData(title="R_Free",  select="r_free")
            byWeightGraph.addData(title="RMS_Bondsx100", select="rmsBOND", expr="str(float(x)*100.)")
            byWeightGraph.addData(title="RMS_Angles",  select="rmsANGLE")

            plot = byWeightGraph.addPlotObject()
            plot.append('title','R Factors as a function of weight matrix term')
            plot.append('plottype','xy')
            for coordinate, colour in [(2,'blue'),(3,'red')]:
                #print coordinate, colour
                plotLine = plot.append('plotline',xcol=1,ycol=coordinate)
                plotLine.append('colour',colour)

            plot = byWeightGraph.addPlotObject()
            plot.append('title','Geometry as a function of weight matrix term')
            plot.append('plottype','xy')
            for coordinate, colour in [(4,'blue'),(5,'red')]:
                plotLine = plot.append('plotline',xcol=1,ycol=coordinate)
                plotLine.append('colour',colour)

            clearingFold = byWeightsFold.addDiv(style="width:760px; clear:both;")

            graphsByWeightFold = byWeightsFold.addFold(label='Details for each weight',brief='Details')
            refmacWeightNodes = xmlnode.findall('./RefmacWeight')
            for refmacWeightNode in refmacWeightNodes:
                self.addOutputForWeight(refmacWeightNode=refmacWeightNode, parent=graphsByWeightFold)

    def addOutputForWeight(self, refmacWeightNode=None, parent=None):
        if parent is None: parent = self
        if refmacWeightNode is None: refmacWeightNode = self.xmlnode
        if len(refmacWeightNode.findall('./REFMAC'))>0:
            refmacReportNode = refmacWeightNode.findall('./REFMAC')[0]
            refmacReport = refmac_report.refmac_report(xmlnode=refmacReportNode, jobStatus='nooutput')
        if refmacReport is not None:
            refmacReport.addSummary(parent = parent)

def test(xmlFile=None,jobId=None,reportFile=None):
    import sys,os
    try:
        text = open( xmlFile ).read()
        xmlnode = ET.fromstring( text, PARSER() )
    except:
        print('FAILED loading XML file:', kw['xmlFile'])
    if reportFile is None and xmlFile is not None:
        reportFile = os.path.join(os.path.split(xmlFile)[0],'report.html')
    r = prosmart_refmac_report(xmlFile=xmlFile,jobId=jobId, xmlnode=xmlnode)
    r.as_html_file(reportFile)

if __name__ == "__main__":
    import sys
    prosmart_refmac_report(xmlFile=sys.argv[1],jobId=sys.argv[2])
