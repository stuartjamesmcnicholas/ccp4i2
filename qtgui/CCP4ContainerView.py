
"""
     CCP4ContainerView.py: CCP4 GUI Project
     Copyright (C) 2011 University of York

     This library is free software: you can redistribute it and/or
     modify it under the terms of the GNU Lesser General Public License
     version 3, modified in accordance with the provisions of the 
     license to address the requirements of UK law.
 
     You should have received a copy of the modified GNU Lesser General 
     Public License along with this library.  If not, copies may be 
     downloaded from http://www.ccp4.ac.uk/ccp4license.php
     
     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU Lesser General Public License for more details.
"""

"""
     Liz Potterton Jan 2011 - CContainerView - autogenerated GUI
"""


from PySide2 import QtGui, QtWidgets,QtCore
from core.CCP4ErrorHandling import *
from core.CCP4Config import DEVELOPER
from core.CCP4Modules import  WEBBROWSER,PROJECTSMANAGER


#-----------------------------------------------------------------
class CContainerView(QtWidgets.QFrame):
#-----------------------------------------------------------------

  WIDTH = 600

  SEPERATOR_TEXT = { 'inputData' : 'Input data',
                   'outputData' : 'Output data',
                   'controlParameters' : 'Control parameters' }

  ERROR_CODES = { 101 : { 'description' : 'Attempting to set invalid container'  },
                  102 : { 'severity' : SEVERITY_WARNING,
                        'description' : 'Attempting to set container without data order information'},
                  103 : { 'description' : 'Unrecognised error attempting to create widget for:' },
                  104 : { 'description' : 'Error attempting to update widget from model for:' },
                  105 : {'description' : 'Internal error handing file - no task container' },
                  106 : { 'description' : 'Error attempting to update model from widget for:' },
              }

  def __init__(self,parent=None,charWidth=10,container=None,projectId=None,jobId=None,folderAttributes=None):
    QtWidgets.QFrame.__init__(self,parent)
    self._showOutputData = False
    self._container = container
    self._projectId = projectId
    self._jobId = jobId
    from qtgui import CCP4TaskWidget
    if folderAttributes is None:
      self.folderAttributes = CCP4TaskWidget.CFolderAttributes()
    else:
      self.folderAttributes =folderAttributes
    self.grid = QtWidgets.QVBoxLayout()
    #layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
    self.charWidth = charWidth
    self.vLayout = None
    self.tabWidget = None
    self.lastRow=-1

    self.setStyleSheet('QFrame [isValid="false"] { border: 1px solid red; }')
    
    #self.draw()

  def taskName(self):
    header = self._container.getHeader()
    if header is not None:
      return str(header.pluginName)
    else:
      return None

  def title(self):
    name = self._container.objectName()
    if name in ['inputData','controlParameters']:
      return ['Input','Control parameters'][['inputData','controlParameters'].index(name)]
    else:
      return name

  def isEditor(self):
    return False

  def setProjectId(self,projectId):
    self._projectId = projectId

  def projectId(self):
    return self._projectId

  def jobId(self):
    return self._jobId

  def jobNumber(self):
    if self._jobId is None:
      return None
    else:
      return PROJECTSMANAGER().db().getJobInfo(self._jobId,mode='jobnumber')

  def setJobId(self,jobId):
    self._jobId = jobId

  def setMessage(self,text=None,parameter=None):
    pass
  
  def getContainer(self):
    return self._container
  
  def setContainer(self,value):
    self._container = value
    
  container = property(getContainer,setContainer)
    

  def setFollowJobId(self,jobId,force=True):
    self._container.guiAdmin.followFrom = jobId
    widget = self.getWidget('followFrom')
    if widget is not None:
      widget.updateInputFiles(jobId,self._projectId,force)
      widget.updateViewFromModel()

  def getWidget(self,name):
    w = self.findChild(QtWidgets.QWidget,name)
    #print 'CContainerView.getWidget',name,w
    return w

  def setDefaultParameters(self):
    pass

  def setDefaultFiles(self):
    pass
  
  def draw(self):
    from core import CCP4Container,CCP4Data,CCP4File
    from qtgui import CCP4Widgets
    myException = CException()
    from core import CCP4DataManager
    #print 'CContainerView.draw',self._container

    # Beware screwing up dataOrder
    keyList = []
    keyList.extend(self._container.dataOrder())
    if self._container.objectName() == 'inputData':
      if self.folderAttributes.attribute(attribute='editable',folderFunction='inputData'):
        keyList.insert(0,'followFrom')
      keyList.insert(0,'jobTitle')
    for name in keyList:
      if name in ['jobTitle','followFrom']:
        model=self._container.parent().guiAdmin.__getattr__(name)
      else:
        model=getattr(self._container,name)
      if isinstance(model,CCP4Container.CContainer):
        if (self._showOutputData or model.objectName() != 'outputData') and not model.objectName() in ['guiAdmin']:
          if self.tabWidget is None:
            self.tabWidget = QtWidgets.QTabWidget(self)
          tab = CContainerView(self,charWidth=self.charWidth,container=model,projectId=self.projectId(),jobId=self.jobId(),folderAttributes=self.folderAttributes)
          tab.draw()
          self.tabWidget.addTab(tab,tab.title())
      else:
        widget = None
        qualifiers = {}
        if not self.folderAttributes.attribute(attribute='editable',folderFunction=model.objectName()):
          qualifiers['editable']=False
        qualifiers.update(model.qualifiers())
        if DEVELOPER():
           widget = CCP4DataManager.DATAMANAGER().widget(model=model,parentWidget=self,name=name,qualifiers=qualifiers)
        else:
          try:
            widget = CCP4DataManager.DATAMANAGER().widget(model=model,parentWidget=self,name=name,qualifiers=qualifiers)
          except CException as e:
            myException.extend(e)
          except:
            myException.append(self.__class__,103,'Data object: '+name)
        
        #print 'CContainerViewer.draw',name,model.__class__,widget,qualifiers
        if widget is not None:
          widget.setObjectName(name)
          self.lastRow = self.lastRow+1
          if isinstance(model,CCP4Data.CList):
            line_layout = QtWidgets.QVBoxLayout()
          else:
            line_layout = QtWidgets.QHBoxLayout()
          line_layout.setSpacing(0)
          line_layout.setContentsMargins(0,0,0,0)
          if not isinstance(model,(CCP4File.CDataFile,CCP4Data.CFollowFromJob)):
            if isinstance(model,CCP4Data.CList):
              line_layout = QtWidgets.QVBoxLayout()
            else:
              line_layout = QtWidgets.QHBoxLayout()
            line_layout.setSpacing(0)
            line_layout.setContentsMargins(0,0,0,0)
            labelText = qualifiers.get('guiLabel',None)
            if labelText is None or labelText is NotImplemented: labelText = name
            label = QtWidgets.QLabel(labelText,self)
            label.setMinimumWidth(100)
            if isinstance(model,CCP4Data.CBoolean):
              line_layout.addWidget(widget)
              line_layout.addWidget(label)
            else:
              widget.setMaximumWidth(CContainerView.WIDTH-116)
              widget.setMinimumWidth(CContainerView.WIDTH-116)
              line_layout.addWidget(label)
              line_layout.addWidget(widget)
            charWidth =  model.qualifiers('charWidth')
            if charWidth is not NotImplemented and charWidth>0:
              line_layout.addStretch(0.5)
            else:
               line_layout.addStretch(5)
            if self.vLayout is None:
              self.vLayout = QtWidgets.QVBoxLayout()
              self.vLayout.setSpacing(0)
              self.vLayout.setContentsMargins(0,0,0,0)
            self.vLayout.addLayout(line_layout)
          else:
            #widget.setMaximumWidth(CContainerView.WIDTH-16)
            widget.setMinimumWidth(CContainerView.WIDTH-16)
            if hasattr(self,'vLayout') and self.vLayout is not None:
              self.vLayout.addWidget(widget)
          widget.updateViewFromModel()
    if self.vLayout is not None: self.vLayout.addStretch(1)
    if self.vLayout is not None: self.grid.addLayout(self.vLayout)
    if self.tabWidget is not None: self.grid.addWidget(self.tabWidget)
    self.setLayout(self.grid)
 
    return myException

  def visibleFolder(self):
    return str(self.tabWidget.tabText(self.tabWidget.currentIndex()))

  def setVisibleFolder(self,title=None,index=None):
    if index is None:
      for ii in range(self.tabWidget.count()):
        if title == str(self.tabWidget.tabText(ii)):
          index = ii
          break
    if index is not None:
      self.tabWidget.setCurrentIndex(index)

    
  def updateViewFromModel(self):
    rv = CErrorReport()
    from qtgui import CCP4Widgets
    widgetList = self.findChildren(CCP4Widgets.CViewWidget)
    for widget in widgetList:
      try:
        widget.updateViewFromModel()
      except:
        rv.append(self.__class__,104,str(widget.objectName()))
    return rv

  def updateModelFromView(self,textOnly=False):
    rv = CErrorReport()
    from qtgui import CCP4Widgets
    widgetList = self.findChildren(CCP4Widgets.CViewWidget)
    #print 'CContainerView.updateModelFromView',widgetList
    for widget in widgetList:
      try:
        if textOnly:
          widget.updateModelFromText()
        else:
          widget.updateModelFromView()
      except:
        rv.append(self.__class__,106,str(widget.objectName()))
    return rv

  def saveData(self,fileName,projectName=None,jobNumber=None):
    #print 'CTaskViewer.saveData',fileName
    container = self.container()
    if container is None:
      e = CException(self.__class__,105,fileName)
      e.warningMessage()
      return

    from core import CCP4File
    f = CCP4File.CI2XmlDataFile(fullPath=fileName)
    cHeader =  self.container().getHeader()
    if cHeader is not None:  f.header.set(cHeader)
    f.header.setCurrent()
    f.header.function.set('PARAMS')
    if projectName is not None: f.header.project.set(projectName)
    if jobNumber is not None: f.header.jobId.set(jobNumber)
    
    bodyEtree = self.container().getEtree()
    f.saveFile(bodyEtree=bodyEtree)
 
  def validate(self):
    pass
  
  
  def isValid(self):
    from qtgui import CCP4Widgets
    widgetList = self.findChildren(CCP4Widgets.CViewWidget)
    invalidList = []
    for widget in widgetList:
      if widget.isValid is not None and not widget.isValid:
        if getattr(widget,'model',None) is not None:
          #print 'CTaskWidget.isValid',widget.model.objectName(),widget.isValid
          invalidList.append(widget.model.objectName())
        else:
          invalidList.append(str(widget))
    return invalidList

  def fix(self):
    # Dummy method to be reimplemented in sub-class
    # Called after user clicks run button and before validate()
    # Probably should be used mostly to ensure that if there are
    # possible alternate input files then only one has a set value
    # (this is to prevent unused files being recorded in database)

    return CErrorReport()
  
  def saveToXml(self,fileName=None,jobInfo={}):
    self.updateModelFromView()
    from core import CCP4File
    if fileName is None:
        fileName = PROJECTSMANAGER().makeFileName(jobId=self._jobId,mode='JOB_INPUT')

    jobInfo = {}
    if self._jobId is not None:
      try:
        jobInfo =  PROJECTSMANAGER().db().getJobInfo(jobId=self._jobId,mode=['taskname','jobnumber','projectname','status','projectid'])
      except:
        pass
      
    f = CCP4File.CI2XmlDataFile(fullPath=fileName)
    cHeader =  self.container.getHeader()
    if cHeader is not None:  f.header.set(cHeader)
    f.header.setCurrent()
    f.header.function.set('PARAMS')
    f.header.jobId.set(self._jobId)
    f.header.projectId.set(self._projectId)
    if jobInfo.get('jobnumber',None) is not None: f.header.jobNumber.set(jobInfo['jobnumber'])
    if jobInfo.get('projectname',None) is not None: f.header.projectName.set(jobInfo['projectname'])

    bodyEtree = self._container.getEtree()       
    from lxml import etree
    f.saveFile(bodyEtree=bodyEtree)
    #print 'CContainerView.saveToXml DONE',fileName,jobInfo
    
  def resetJobCombos(self):
    from qtgui import CCP4Widgets
    #print 'CTabTaskWidget.resetJobCombos'
    widgetList = self.findChildren(CCP4Widgets.CDataFileView)
    for widget in widgetList:
      widget.loadJobCombo()
      widget.updateJobCombo()
      widget.updateModelFromView()

  def taskValidity(self):
    return CErrorReport()

  def setMessage(self,text='',parameter=None):
    return
    if text is None: text = ''
    self.message.setText(text)
    self.messageStack.append([parameter,text])
    #print 'setMessage',text,parameter,self.messageStack
    
  def unsetMessage(self,parameter=None):
    return
    if len(self.messageStack)==0: return
    if self.messageStack[-1][0] == parameter:
      del self.messageStack[-1]
    else:
      delFrom = None
      for ii in range(len(self.messageStack)-2,-1,-1):
        if self.messageStack[ii][0] == parameter:
          delFrom = ii
      if delFrom is not None:
        #print 'unsetMessage deleting multi levels of stack',self.messageStack,delFrom
        del self.messageStack[delFrom:-1]

    #print 'unsetMessage',parameter,self.messageStack
    if len(self.messageStack)>0:
        self.message.setText(self.messageStack[-1][1])

  def updateMessage(self,text='',parameter=None):
    return
    for ii in range(len(self.messageStack)):
      if self.messageStack[ii][0] == parameter:
        if text is None: text = ''
        self.messageStack[ii][1] = text
    if len(self.messageStack)>0:
      self.message.setText(self.messageStack[-1][1])
    #print 'updateMessage',text,parameter,self.messageStack
