from __future__ import print_function
"""
    pipelines/phaser_pipeline/wrappers/phaser_MR/script/phaser_MR_gui.py
    Copyright (C) 2014 Newcastle University
    Author: Martin Noble
    
    """

from qtgui.CCP4TaskWidget import CTaskWidget
from PySide6 import QtCore

#-------------------------------------------------------------------
class phaser_EP_LLG_gui(CTaskWidget):
    #-------------------------------------------------------------------
    
    # Subclass CTaskWidget to give specific task window
    TASKNAME = 'phaser_EP_LLG'
    TASKVERSION = 0.1
    TASKMODULE='expt_data_utility'
    TASKTITLE='Anomalous map from coordinates - PHASER'
    DESCRIPTION = '''Calculate anomalous LLG map phased by coordinates to highlight anomalous scatterers (Phaser)'''

    def __init__(self,*args,**kws):
        super(phaser_EP_LLG_gui,self).__init__(*args,**kws)

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
        
        self.openSubFrame()
        self.createLine ( [ 'widget', 'F_SIGF' ] )
        self.container.inputData.F_SIGF.dataChanged.connect(self.getWavelength)

        self.createLine ( [ 'widget','-guiLabel','Partial model', 'XYZIN_PARTIAL' ] )
        self.createLine (['label','Resolution range','stretch','widget','RESOLUTION_LOW','widget','RESOLUTION_HIGH'])
        self.closeSubFrame()

        self.createLine ( [ 'subtitle', 'Composition', 'Phaser needs guidance about the contents of the asymmetric unit' ] )
        self.openSubFrame(frame=True)
        self.setMenuText('COMP_BY',{ 'DEFAULT':'Use protein average solvent content',
                         'MW':'Provide an estimate of the molecular weight of protein and nucleic acid in ASU',
                         'ASU':'Provide a full specification of the ASU content by sequence'
                         })
        self.createLine ( ['label', 'For estimating asymmetric unit contents:','widget','COMP_BY'])
        self.createLine ( ['label', '\n '], toggle=['COMP_BY','open',['MW']])
        
        self.createLine ( [ 'widget', '-title','Contents of asymmetric unit  - click "Show list" if more than one type of chain is present', 'ASU_COMPONENTS' ], toggle=['COMP_BY','open',['ASU']])
        self.createLine ( [ 'widget', 'ASUFILE' ], toggle=['COMP_BY','open',['ASU']])
        self.createLine ( [ 'label','Molecular weight (Da) of protein in the ASU','stretch','widget', 'ASU_PROTEIN_MW' ], toggle=['COMP_BY','open',['MW']])
        self.createLine ( [ 'label','Molecular weight (Da) of nucleic acid','stretch','widget', 'ASU_NUCLEICACID_MW' ], toggle=['COMP_BY','open',['MW']])
        self.closeSubFrame()
        self.createLine ( [ 'label','Wavelength','widget', 'WAVELENGTH' ] )
    
    @QtCore.Slot()
    def getWavelength(self):
        if self.container.inputData.F_SIGF.isSet():
            wavelengths = self.container.inputData.F_SIGF.fileContent.getListOfWavelengths()
            try:
                self.container.inputData.WAVELENGTH = round(wavelengths[-1],3)
                self.getWidget('WAVELENGTH').updateViewFromModel()
            except:
                print('phaser_RP_LLG_gui - WAVELENGTH widget  updateViewFromModel failed')

    def isValid(self):
        #Here override logic of whether this is a valid task to allow for CSeqDataFile from the
        #CASUComponentList being required ONLY IF COMP_BY has the value "ASU"
        invalidElements = CTaskWidget.isValid(self)
        
        if not self.container.inputData.XYZIN_PARTIAL.isSet() and not self.container.inputData.XYZIN_HA.isSet():
            invalidElements.append(self.container.inputData.XYZIN_PARTIAL)
            invalidElements.append(self.container.inputData.XYZIN_HA)
        from core import CCP4ModelData, CCP4XtalData
        widgLib = {"COMP_BY":"Not set yet"}
        self.getParams(widgLib)
        if widgLib["COMP_BY"] != "ASU":
            invalidElements = [invalidElement for invalidElement in invalidElements if (type(invalidElement) != CCP4XtalData.CAsuComponent and type(invalidElement) != CCP4ModelData.CSeqDataFile)]
        return invalidElements

