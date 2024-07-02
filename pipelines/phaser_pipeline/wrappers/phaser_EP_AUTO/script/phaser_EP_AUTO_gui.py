from __future__ import print_function
"""
    pipelines/phaser_pipeline/wrappers/phaser_MR/script/phaser_MR_gui.py
    Copyright (C) 2014 Newcastle University
    Author: Martin Noble
    
    """

from qtgui.CCP4TaskWidget import CTaskWidget
from PySide6 import QtCore


#-------------------------------------------------------------------
class phaser_EP_AUTO_gui(CTaskWidget):
    #-------------------------------------------------------------------
    
    # Subclass CTaskWidget to give specific task window
    TASKNAME = 'phaser_EP_AUTO'
    TASKVERSION = 0.1
    TASKMODULE='None'
    TASKTITLE='SAD phasing from heavy atom sites - PHASER'
    DESCRIPTION = '''Complete a heavy atom model and calculate phases'''
    WHATNEXT=['coot_rebuild','parrot', ['buccaneer_build_refine_mr','$CCP4I2/pipelines/buccaneer_build_refine_mr/script/bucref_after_experimental.params.xml']]

    def __init__(self,parent):
        CTaskWidget.__init__(self,parent)

    def setDefaultParameters(self):
        self.getWavelength()
        # Reimplement in tasks to set initial parameters
        # read ccp4/src/phaser/source/phaser/defaults for defaults
        pass
        
    def drawContents(self):

        self.setProgramHelpFile('phaser')
        self.drawPhaserFrontPage()
        self.drawPhaserKeywordsFolder()
    
    def drawPhaserKeywordsFolder(self):
        #From here on, GUI is autogenerated from the keywords container
        self.openFolder(folderFunction='keywords', title='Keywords')
        self.openSubFrame()
        self.autoGenerate(container=self.container.keywords,selection={'excludeParameters' : ['TITL','ROOT']})
        self.closeSubFrame()
    

    def drawPhaserFrontPage(self):
        self.openFolder(folderFunction='inputData')
        
        self.createLine( ['subtitle', 'Experimental data','tip','Phaser uses this for maximum likelihood and to suggest number of copies in the asymmetric unit' ])
        self.openSubFrame(frame=True)
        self.createLine ( ['label', '\n '])
        self.createLine ( [ 'widget', 'F_SIGF' ] )
        self.container.inputData.F_SIGF.dataChanged.connect( self.getWavelength)
        if self.container.inputData.F_SIGF.isSet(): self.getWavelength()
        self.createLine (['label','Resolution range','stretch','widget','RESOLUTION_LOW','widget','RESOLUTION_HIGH','label','Wavelength','widget','WAVELENGTH'])
        self.closeSubFrame()
        
        self.createLine( ['subtitle', 'Known sites, phasing model, or phases','tip','known sites will be used as start point for competing the heavy atom model. Partial model or map will be used to start to find sites.' ])
        self.openSubFrame(frame=True)
        self.createLine(['label','Provide sites, partial model or phases as:','widget','PARTIALMODELORMAP'])
        self.container.inputData.PARTIALMODELORMAP.dataChanged.connect(self.handlePARTIALMODELORMAP)
        self.handlePARTIALMODELORMAP()
        self.createLine ( [ 'widget','-guiLabel','Partial protein model', 'XYZIN_PARTIAL' ], toggle=['PARTIALMODELORMAP','open',['MODEL']])
        self.createLine ( [ 'widget','-guiLabel','Partial protein model', 'MAPCOEFF_PARTIAL' ], toggle=['PARTIALMODELORMAP','open',['MAP']])
        self.createLine ( [ 'widget','-guiLabel','Partial HA model', '-browseDb','True','XYZIN_HA' ], toggle=['PARTIALMODELORMAP','open',['NONE']] )
        self.closeSubFrame()
        
        self.createLine( ['subtitle', 'Composition','tip','Phaser uses this for maximum likelihood and to suggest number of copies in the asymmetric unit' ])
        self.openSubFrame(frame=True)
        self.setMenuText('COMP_BY',{ 'DEFAULT':'Use protein average solvent content',
                         'MW':'Provide an estimate of the molecular weight of protein and nucleic acid in ASU',
                         'ASU':'Provide a full specification of the ASU content by sequence'
                         })
        self.createLine ( ['tip','Phaser uses this for maximum likelihood and to suggest number of copies in the asymmetric unit','label', 'For estimating asymmetric unit contents:','widget','COMP_BY'])
        self.container.inputData.COMP_BY.dataChanged.connect(self.handleCOMP_BY)
        self.handleCOMP_BY()
        self.createLine ( ['label', '\n '], toggle=['COMP_BY','open',['DEFAULT']])
         
        self.createLine ( [ 'widget', 'ASUFILE' ], toggle=['COMP_BY','open',['ASU']])
        self.createLine ( [ 'label','Molecular weight (Da) of protein in the ASU','stretch','widget', 'ASU_PROTEIN_MW' ], toggle=['COMP_BY','open',['MW']])
        self.createLine ( [ 'label','Molecular weight (Da) of nucleic acid','stretch','widget', 'ASU_NUCLEICACID_MW' ], toggle=['COMP_BY','open',['MW']])
        self.closeSubFrame()
        
        self.createLine ( [ 'label','Cycles of heavy atom model completion','widget', 'LLGC_CYCLES' ] )
        self.createLine(['label','Search for pure anomalous scatterers','widget','PURE_ANOMALOUS'])
        self.createLine(['widget','-title','Elements to search for','ELEMENTS'])

    @QtCore.Slot()
    def getWavelength(self):
        if self.container.inputData.F_SIGF.isSet():
            wavelengths = self.container.inputData.F_SIGF.fileContent.getListOfWavelengths()
            if len(wavelengths)>0:
                try:
                    self.container.inputData.WAVELENGTH = round(wavelengths[-1],3)
                except:
                    print('Unaceptable wavelength set attempted:',wavelengths[-1])
            #updateViewFromModel may only work in "editor" rather than "viewer" mode of the widget
            try: self.getWidget('WAVELENGTH').updateViewFromModel()
            except: pass

    @QtCore.Slot()
    def handleCOMP_BY(self):
        self.container.inputData.ASUFILE.setQualifiers({'allowUndefined':(str(self.container.inputData.COMP_BY) != "ASU")})            
        self.validate()
        

    @QtCore.Slot()
    def handlePARTIALMODELORMAP(self):
        implications = {'MAP':{'needed':False,'attributeName':'MAPCOEFF_PARTIAL'},
        'MODEL':{'needed':False,'attributeName':'XYZIN_PARTIAL'},
        'NONE':{'needed':False,'attributeName':'XYZIN_HA'}}
        for key in implications:
            needed = self.container.inputData.PARTIALMODELORMAP.__str__() == key
            attrName = implications[key]['attributeName']
            print(key, attrName)
            attribute = getattr(self.container.inputData, attrName)
            attribute.setQualifiers({'mustExist' : needed , 'allowUndefined' : (not needed) } )
            widget = self.getWidget(attrName)
            if widget is not None: widget.validate()

