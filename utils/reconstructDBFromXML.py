from __future__ import print_function

import sys
import os
import fnmatch
import datetime
if sys.version_info < (3,0):
    from StringIO import StringIO
else:
    from io import StringIO
from collections import OrderedDict
from operator import itemgetter

from distutils.version import LooseVersion

from dateutil import parser
from dateutil.tz import tzlocal
from lxml import etree
from xml.etree import ElementTree as ET

"""
This is a script which attempts to construct an XML file such as is created by export (or backupDB) from input_params.xml/params.xml/stdout.txt files.

Ug, creation time needs to take timezone into account. Hm.

TODO:

  * <jobTable>
      - preceedingjobid
      - sort by jobnumber, and then first usage is way more likely to be correct. (But not necessarily!) Should use first out occurrence before any input.

  *  <fileTable/>
      - Jobs without params.xml, e.g. ASUCONTENTFILE.xml (/Users/stuart/CCP4I2_PROJECTS/CASU2/CCP4_JOBS/job_99/) 
      - Many missing, can't just be above, surely?
      - should not have 'number' attribute'
  *  <fileuseTable/>
     - filter out non-complete jobs?
  *  <importfileTable/>
  *  <exportfileTable/>
  *  <xdataTable/>
  *  <commentTable/>
  *  <projectcommentTable/>
  *  <fileassociationmemberTable/>
  *  <fileassociationTable/>
  *  <projecttagTable/>
  *  <tagTable/>

Potential anomolies:

fasolt:ccp4i2-devel-clean stuart$ grep -c jobkeyvalue reconstruct.xml DATABASE.db.xml 
reconstruct.xml:50
DATABASE.db.xml:125
fasolt:ccp4i2-devel-clean stuart$ grep -c 'job jobid'  reconstruct.xml DATABASE.db.xml 
reconstruct.xml:259
DATABASE.db.xml:259
fasolt:ccp4i2-devel-clean stuart$ grep -c 'file fileid'  reconstruct.xml DATABASE.db.xml 
reconstruct.xml:553
DATABASE.db.xml:577
fasolt:ccp4i2-devel-clean stuart$ grep -c 'fileuse fileid'  reconstruct.xml DATABASE.db.xml 
reconstruct.xml:269
DATABASE.db.xml:209

"""

timeZoneName = datetime.datetime.now(tzlocal()).tzname().split()[0]

CCP4NS = "http://www.ccp4.ac.uk/ccp4ns"

LISTCLASSES = [ "CList", "CSeqDataFileList", "CPdbDataFileList", "CEnsembleList", "CResidueRangeList", "CAsuContentSeqList", "CRefmacRigidGroupList", "CAltSpaceGroupList", "CUnmergedDataFileList", "CImportUnmergedList", "CImageFileList", "CXia2ImageSelectionList", "CColumnTypeList", "CColumnGroupList", "CAsuComponentList", "CMiniMtzDataFileList", "CMergeMiniMtzList", "CRunBatchRangeList", "CDatasetList" ]

FILETYPE_ALIAS = {'CImportUnmerged' : 'UnmergedDataFile'}

FILETYPES_CLASS = ['DataFile', 'SeqDataFile', 'PdbDataFile', '', 'MtzDataFile', 'MtzDataFile',
                   'UnmergedDataFile', 'MapDataFile', 'DictDataFile', 'TLSDataFile',
                   'FreeRDataFile', 'ObsDataFile', 'PhsDataFile', 'MapCoeffsDataFile', '',
                   'SeqAlignDataFile', 'MiniMtzDataFile', 'CootHistoryDataFile', 'RefmacRestraintsDataFile',
                   'SceneDataFile', 'ShelxFADataFile', 'PhaserSolDataFile', 'MDLMolDataFile',
                   'ImosflmXmlDataFile', 'ImageFile', 'GenericReflDataFile', 'HhpredDataFile',
                   'BlastDataFile', 'EnsemblePdbDataFile', 'AsuDataFile', 'DialsJsonFile', 'DialsPickleFile']

KEYTYPELIST =  [ (0,'Unknown','Key type unknown'),
                    (1,'RFactor','R Factor'),
                    (2,'RFree','Free R Factor'),
                    (3,'completeness','model completeness'),
                    (4, 'spaceGroup','space group'),
                    (5, 'highResLimit', 'high resolution limit'),
                    (6, 'rMeas', 'Rmeas data consistency'),
                    (7,'FOM','figure of merit of phases'),
                    (8,'CFOM','correlation FOM'),
                    (9,'Hand1Score','Hand 1 score'),
                    (10,'Hand2Score','Hand 2 score'),
                    (11,'CC','correlation coefficient between Fo and Fc'),
                    (12,'nAtoms','number of atoms in model'),
                    (13,'nResidues','number of residues in model'),
                    (14,'phaseError','phase error'),
                    (15,'weightedPhaseError','weighted phase error'),
                    (16,'reflectionCorrelation','reflection correlation'),
                    (17,'RMSxyz','RMS displacement'), ]


def datetime_to_float(d):
    epoch = datetime.datetime.utcfromtimestamp(0)
    epoch = parser.parse("12:00 1/Jan/1970 "+timeZoneName)
    total_seconds =  (d - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return total_seconds

def generate_xml_from_project_directory(project_dir):
    projectRoot = ""
    lastJobNumber = 1
    
    params_files = []
    for root, dirn, files in os.walk(project_dir):
            sn = os.path.split(root)
            for items in fnmatch.filter(files, "params.xml"):
                    fxml = os.path.join(root,items)
                    statinfo = os.stat(fxml)
                    if statinfo.st_size == 0:
                        print("Skipping",fxml)
                        continue
                    params_files.append(fxml)
                    #print sn
                    sn2 = os.path.split(sn[0])
                    if len(sn)>0 and sn2[1] == "CCP4_JOBS":
                        if sn[1].startswith("job_"):
                            jobNo = int(sn[1][len("job_"):])
                            if jobNo > lastJobNumber:
                                lastJobNumber = jobNo
            for items in fnmatch.filter(files, "input_params.xml"):
                    pxml = os.path.join(root,"params.xml")
                    ipxml = os.path.join(root,items)
                    if not pxml in params_files:
                        statinfo = os.stat(ipxml)
                        if statinfo.st_size == 0:
                            print("Skipping",ipxml)
                            continue
                        params_files.append(ipxml)
                        sn2 = os.path.split(sn[0])
                        if len(sn)>0 and sn2[1] == "CCP4_JOBS":
                            if sn[1].startswith("job_"):
                                jobNo = int(sn[1][len("job_"):])
                                if jobNo > lastJobNumber:
                                    lastJobNumber = jobNo
            if len(sn)>0 and sn[1] == "CCP4_JOBS":
                projectRoot = os.path.dirname(root)
    
    lastJobNumber = str(lastJobNumber)
    projectName = ""
    hostName = ""
    userId = ""
    ccp4iVersion = ""
    OS = ""
    projectId = ""
    
    endOfTime = datetime.datetime.max
    endOfTimeStr = datetime.datetime.strftime(endOfTime,"%Y-%m-%d %H:%M")#9999-12-31 23:59:59.999999
    endOfTime = parser.parse(endOfTimeStr + " " + timeZoneName)
    creationTime = endOfTime
    
    eleTree = ET.parse(StringIO('<ccp4:ccp4i2 xmlns:ccp4="'+CCP4NS+'"></ccp4:ccp4i2>'))
    root = eleTree.getroot()
    ccp4i2_header = ET.SubElement(root,"ccp4i2_header")
    ccp4i2_body = ET.SubElement(root,"ccp4i2_body")
    jobTable_el = ET.SubElement(ccp4i2_body,"jobTable")
    fileTable_el = ET.SubElement(ccp4i2_body,"fileTable")
    fileUseTable_el = ET.SubElement(ccp4i2_body,"fileuseTable")
    
    jobs = []
    
    def parse_from_unicode(unicode_str):
        utf8_parser = ET.XMLParser(encoding='utf-8')
        s = unicode_str.encode('utf-8')
        return ET.fromstring(s, parser=utf8_parser)
    
    for fn in params_files:
        with open(fn) as f:
            t = f.read()
            #print t
            if sys.version_info < (3,0):
                try:
                    xmlparser = ET.XMLParser()
                    tree = ET.fromstring(t, xmlparser)
                except:
                    print("Failed to process file",fn)
            else:
                tree = parse_from_unicode(t)
            #print tree.findall("ccp4i2_header")[0].findall("jobId")
            if len(tree.findall("ccp4i2_header")[0].findall("creationTime"))>0:
                dt = tree.findall("ccp4i2_header")[0].findall("creationTime")[0].text
                dt += " "+timeZoneName
                t = parser.parse(dt)
                #print "Date",dt,t
                if t<creationTime:
                    creationTime = t
            if len(tree.findall("ccp4i2_header")[0].findall("projectName"))>0:
                if projectName == "":
                    if  tree.findall("ccp4i2_header")[0].findall("projectName")[0].text != None and len(tree.findall("ccp4i2_header")[0].findall("projectName")[0].text.strip())>0:
                        projectName = tree.findall("ccp4i2_header")[0].findall("projectName")[0].text
                elif tree.findall("ccp4i2_header")[0].findall("projectName")[0].text != projectName:
                    print("Problem, project name changed",tree.findall("ccp4i2_header")[0].findall("projectName")[0].text,projectName)
                    print("Keeping old name",projectName)
            if len(tree.findall("ccp4i2_header")[0].findall("projectId"))>0:
                if projectId == "":
                    if tree.findall("ccp4i2_header")[0].findall("projectId")[0].text != None and len(tree.findall("ccp4i2_header")[0].findall("projectId")[0].text.strip())>0:
                        projectId = tree.findall("ccp4i2_header")[0].findall("projectId")[0].text
                elif tree.findall("ccp4i2_header")[0].findall("projectId")[0].text != projectId:
                    print("Problem, project id changed",tree.findall("ccp4i2_header")[0].findall("projectId")[0].text,projectId)
                    print("Keeping old id",projectId)
            if len(tree.findall("ccp4i2_header")[0].findall("hostName"))>0 and len(tree.findall("ccp4i2_header")[0].findall("hostName")[0].text)>0:
                hostName = tree.findall("ccp4i2_header")[0].findall("hostName")[0].text
            if len(tree.findall("ccp4i2_header")[0].findall("userId"))>0 and len(tree.findall("ccp4i2_header")[0].findall("userId")[0].text)>0:
                userId = tree.findall("ccp4i2_header")[0].findall("userId")[0].text
            if len(tree.findall("ccp4i2_header")[0].findall("ccp4iVersion"))>0 and len(tree.findall("ccp4i2_header")[0].findall("ccp4iVersion")[0].text)>0:
                ccp4iVersion = tree.findall("ccp4i2_header")[0].findall("ccp4iVersion")[0].text
            if len(tree.findall("ccp4i2_header")[0].findall("OS"))>0 and len(tree.findall("ccp4i2_header")[0].findall("OS")[0].text)>0:
                OS = tree.findall("ccp4i2_header")[0].findall("OS")[0].text
    
            if len(tree.findall("ccp4i2_header")[0].findall("jobId"))>0 and len(tree.findall("ccp4i2_header")[0].findall("jobId")[0].text)>0:
                if len(tree.findall("ccp4i2_header")[0].findall("jobNumber"))>0 and len(tree.findall("ccp4i2_header")[0].findall("jobNumber")[0].text)>0:
                    if len(tree.findall("ccp4i2_header")[0].findall("pluginName"))>0 and len(tree.findall("ccp4i2_header")[0].findall("pluginName")[0].text)>0:
                        jobId = tree.findall("ccp4i2_header")[0].findall("jobId")[0].text
                        jobNumber = tree.findall("ccp4i2_header")[0].findall("jobNumber")[0].text
                        pluginName = tree.findall("ccp4i2_header")[0].findall("pluginName")[0].text
                        attrib = {}
                        attrib["jobid"] = jobId
                        attrib["jobnumber"] = jobNumber
                        if len(tree.findall("ccp4i2_header")[0].findall("creationTime"))>0 and len(tree.findall("ccp4i2_header")[0].findall("creationTime")[0].text)>0:
                            dt = tree.findall("ccp4i2_header")[0].findall("creationTime")[0].text
                            dt += " "+timeZoneName
                            t = parser.parse(dt)
                            strfloattime = str(datetime_to_float(t))
                            attrib["creationtime"] = strfloattime
                        attrib["useragent"] = "1" # We have no way of knowing and I cannot think it matters
                        if len(tree.findall("ccp4i2_header")[0].findall("pluginTitle"))>0 and len(tree.findall("ccp4i2_header")[0].findall("pluginTitle")[0].text)>0:
                            pluginTitle = tree.findall("ccp4i2_header")[0].findall("pluginTitle")[0].text
                            attrib["jobtitle"] = pluginTitle
                        attrib["projectid"] = projectId
                        attrib["taskname"] = pluginName
                        parentXML = os.path.join(os.path.dirname(os.path.dirname(fn)),"params.xml")
                        if os.path.exists(parentXML):
                            with open(parentXML) as f2:
                                t2 = f2.read()
                                if sys.version_info < (3,0):
                                    xmlparser2 = ET.XMLParser()
                                    tree2 = ET.fromstring(t2, xmlparser2)
                                else:
                                    tree2 = parse_from_unicode(t2)
                                if len(tree2.findall("ccp4i2_header")[0].findall("jobId"))>0 and len(tree2.findall("ccp4i2_header")[0].findall("jobId")[0].text)>0:
                                    jobId2 = tree2.findall("ccp4i2_header")[0].findall("jobId")[0].text
                                    attrib["parentjobid"] = jobId2
                        #Hmm, no good. Not all jobs have a diagnostic.xml, only top level jobs. If a top-level has finished, then all sub-jobs must be!
                        try:
                            with open(os.path.join(os.path.dirname(fn),"diagnostic.xml")) as fdiag:
                                tdiag = fdiag.read()
                                if sys.version_info < (3,0):
                                    treediag = ET.fromstring(tdiag, xmlparser)
                                else:
                                    treediag = parse_from_unicode(tdiag)
                                if len(treediag.findall("ccp4i2_body")[0].findall("errorReport"))>0:
                                    attrib["status"] = "5"
                                else:
                                    attrib["status"] = "6" #IT may be running of course, but we skip that possibility and leave user to deal with.
                                attrib["finishtime"] = str(os.path.getmtime(os.path.join(os.path.dirname(fn),"diagnostic.xml")))
                        except IOError:
                            attrib["status"] = "1"
                        jobs.append(attrib)
    
    #TODO - We need to construct fileuse from file stuff as well
    
    files = []
    fileuses = []
    wrapper_cache = {}
    jkv = []
    
    
    def getPluginDefXmlInt(pluginName):
        for wrap_root, wrap_dirn, wrap_files in os.walk(os.environ["CCP4I2"]):
            for items in fnmatch.filter(wrap_files, pluginName+".def.xml"):
                pluginDefXml = os.path.join(wrap_root,items)
        with open(pluginDefXml) as f:
            t = f.read()
            if sys.version_info < (3,0):
                xmlparser = ET.XMLParser()
                tree = ET.fromstring(t, xmlparser)
            else:
                tree = parse_from_unicode(t)
        return tree
    
    def getPluginDefXml(pluginName,wrapper_cache):
    
        pluginDefXml = None
        if pluginName in wrapper_cache:
            pluginDefXml = wrapper_cache[pluginName]
        else:
            pluginDefXml = getPluginDefXmlInt(pluginName)
            wrapper_cache[pluginName] = pluginDefXml
        return pluginDefXml
    
    def getTypeId(pluginDefXml,jobparamname,inout):
        """
        typeid 29 is set to 1, since this is what export seems to do, although that seems a bit iffy to me.
        """
        if len(pluginDefXml.findall("ccp4i2_body")[0])>0:
            for cont in pluginDefXml.findall("ccp4i2_body")[0].findall("container"):
                if "id" in cont.attrib:
                    if cont.attrib["id"] == inout:
                        for param in cont.findall("content"):
                            if "id" in param.attrib:
                                if param.attrib["id"] == jobparamname:
                                    if len(param.findall("className"))>0:
                                        className = param.findall("className")[0].text
                                        if className in LISTCLASSES:
                                            if len(param.findall("subItem"))>0:
                                                subItem = param.findall("subItem")[0]
                                                if len(subItem.findall("className"))>0:
                                                    className2 = subItem.findall("className")[0].text
                                                if len(className2) > 1:
                                                    if className2 in FILETYPE_ALIAS:
                                                        className2 = FILETYPE_ALIAS[className2]
                                                    try:
                                                        typeid =  FILETYPES_CLASS.index(className2.lstrip("C"))
                                                        if (jobparamname == "SEQIN" or jobparamname == "AWA_SEQIN") and typeid == 29:
                                                            typeid = 1
                                                        return typeid
                                                    except:
                                                        return 0
                                        if len(className) > 1:
                                            if className in FILETYPE_ALIAS:
                                                className = FILETYPE_ALIAS[className2]
                                            try:
                                                typeid =  FILETYPES_CLASS.index(className.lstrip("C"))
                                                if (jobparamname == "SEQIN" or jobparamname == "AWA_SEQIN") and typeid == 29:
                                                    typeid = 1
                                                return typeid
                                            except:
                                                return 0
        if jobparamname == "SEQIN":
            return 1
    
        #Final catchall.
        return 0
    
    
    for fn in params_files:
        with open(fn) as f:
            t = f.read()
            if sys.version_info < (3,0):
                xmlparser = ET.XMLParser()
                tree = ET.fromstring(t, xmlparser)
            else:
                tree = parse_from_unicode(t)
            if len(tree.findall("ccp4i2_header")[0].findall("jobId"))>0 and len(tree.findall("ccp4i2_header")[0].findall("jobId")[0].text)>0:
                if len(tree.findall("ccp4i2_header")[0].findall("jobNumber"))>0 and len(tree.findall("ccp4i2_header")[0].findall("jobNumber")[0].text)>0:
                    if len(tree.findall("ccp4i2_header")[0].findall("pluginName"))>0 and len(tree.findall("ccp4i2_header")[0].findall("pluginName")[0].text)>0:
                        jobId = tree.findall("ccp4i2_header")[0].findall("jobId")[0].text
                        jobNumber = tree.findall("ccp4i2_header")[0].findall("jobNumber")[0].text
                        pluginName = tree.findall("ccp4i2_header")[0].findall("pluginName")[0].text
                        if len(tree.findall("ccp4i2_body")[0].findall("outputData"))>0:
                            inputData_el = tree.findall("ccp4i2_body")[0].findall("outputData")[0]
                            inps = inputData_el.iterdescendants()
                            for inp in inps:
                                if len(inp.findall("dbFileId"))>0 and len(inp.findall("baseName"))>0:
                                    fileid =  inp.findall("dbFileId")[0].text
                                    filename = inp.findall("baseName")[0].text
                                    jobparamname = inp.tag
                                    parent = inp.find("..")
                                    while parent.tag != "outputData":
                                        jobparamname = parent.tag
                                        parent = parent.find("..")
                                    attrib = OrderedDict()
                                    attrib["fileid"] = fileid
                                    attrib["filename"] = filename
                                    attrib["jobid"] = jobId
                                    attrib["number"] = jobNumber
                                    attrib["inout"] = "0"
                                    attrib["roleid"] = "0"
                                    attrib["jobparamname"] = jobparamname
                                    pluginDefXml  = getPluginDefXml(pluginName,wrapper_cache)
                                    if pluginDefXml is None:
                                        print("Not found def.xml for", pluginName,". Cannot determine typeid for",jobparamname)
                                    else:
                                        typeid = getTypeId(pluginDefXml,jobparamname,"outputData")
                                        attrib["filetypeid"] = str(typeid)
                                    if len(inp.findall("annotation"))>0:
                                        attrib["annotation"] = inp.findall("annotation")[0].text
                                    if len(inp.findall("subType"))>0:
                                        attrib["filesubtype"] = inp.findall("subType")[0].text
                                    if len(inp.findall("contentFlag"))>0:
                                        attrib["filecontent"] = inp.findall("contentFlag")[0].text
                                    if len(inp.findall("relPath"))>0:
                                        relPath = inp.findall("relPath")[0].text
                                        if relPath == "CCP4_IMPORTED_FILES":
                                            attrib["pathflag"] = "2"
                                        else:
                                            attrib["pathflag"] = "1"
                                    files.append(attrib)
    
    for fn in params_files:
        with open(fn) as f:
            t = f.read()
            if sys.version_info < (3,0):
                xmlparser = ET.XMLParser()
                tree = ET.fromstring(t, xmlparser)
            else:
                tree = parse_from_unicode(t)
            if len(tree.findall("ccp4i2_header")[0].findall("jobId"))>0 and len(tree.findall("ccp4i2_header")[0].findall("jobId")[0].text)>0:
                if len(tree.findall("ccp4i2_header")[0].findall("jobNumber"))>0 and len(tree.findall("ccp4i2_header")[0].findall("jobNumber")[0].text)>0:
                    if len(tree.findall("ccp4i2_header")[0].findall("pluginName"))>0 and len(tree.findall("ccp4i2_header")[0].findall("pluginName")[0].text)>0:
                        jobId = tree.findall("ccp4i2_header")[0].findall("jobId")[0].text
                        jobNumber = tree.findall("ccp4i2_header")[0].findall("jobNumber")[0].text
                        pluginName = tree.findall("ccp4i2_header")[0].findall("pluginName")[0].text
                        if len(tree.findall("ccp4i2_body")[0].findall("inputData"))>0:
                            inputData_el = tree.findall("ccp4i2_body")[0].findall("inputData")[0]
                            for inp in inputData_el.iterdescendants():
                                if len(inp.findall("dbFileId"))>0 and len(inp.findall("baseName"))>0:
                                    fileid =  inp.findall("dbFileId")[0].text
                                    filename = inp.findall("baseName")[0].text
                                    jobparamname = inp.tag
                                    parent = inp.find("..")
                                    while parent.tag != "inputData":
                                        jobparamname = parent.tag
                                        parent = parent.find("..")
                                    #file_el = ET.SubElement(fileTable_el,"file")
                                    attrib = OrderedDict()
                                    attrib["fileid"] = fileid
                                    attrib["filename"] = filename
                                    attrib["jobid"] = jobId
                                    attrib["number"] = jobNumber
                                    attrib["inout"] = "1"
                                    attrib["jobparamname"] = jobparamname
                                    pluginDefXml  = getPluginDefXml(pluginName,wrapper_cache)
                                    if pluginDefXml is None:
                                        print("Not found def.xml for", pluginName,". Cannot determine typeid for",jobparamname)
                                    else:
                                        typeid = getTypeId(pluginDefXml,jobparamname,"inputData")
                                        attrib["filetypeid"] = str(typeid)
    
                                    if len(inp.findall("annotation"))>0:
                                        attrib["annotation"] = inp.findall("annotation")[0].text
                                    if len(inp.findall("subType"))>0:
                                        attrib["filesubtype"] = inp.findall("subType")[0].text
                                    if len(inp.findall("contentFlag"))>0:
                                        attrib["filecontent"] = inp.findall("contentFlag")[0].text
                                    if len(inp.findall("relPath"))>0:
                                        relPath = inp.findall("relPath")[0].text
                                        if relPath == "CCP4_IMPORTED_FILES":
                                            attrib["pathflag"] = "2"
                                        else:
                                            attrib["pathflag"] = "1"
                                    files.append(attrib)
                                    if(os.path.basename(os.path.dirname(os.path.dirname(fn)))) == "CCP4_JOBS":
                                        #FIXME - I think only for completed jobs! So we need to search job tree and then filter.
                                        attribuse = {}
                                        for k,v in attrib.items():
                                            if k == "fileid" or k == "jobid" or k == "jobparamname":
                                                attribuse[k] = v
                                            attribuse["roleid"] = "1"
                                        fileuses.append(attribuse)
                        fnout = os.path.join(os.path.dirname(fn),"stdout.txt")
                        if os.path.exists(fnout):
                            with open(fnout) as f:
                                tls = f.readlines()
                                for l in reversed(tls):
                                    if l.strip().startswith("Saving key:value pairs"):
                                        vals = eval(l.strip().lstrip("Saving key:value pairs"))
                                        jkv.append((jobId, vals))
                                        break
    
    if projectName == "" or projectId == "":
        return root
    
    files = sorted(files, key=itemgetter('inout'), reverse=True)
    files = sorted(files, key=lambda k: LooseVersion(k['number']))
    jobs = sorted(jobs, key=lambda k: LooseVersion(k['jobnumber']))
    
    uniqueuse = []
    fileuse2 = []
    
    for x in fileuses:
        if not (x["fileid"],x["jobid"]) in uniqueuse:
            uniqueuse.append((x["fileid"],x["jobid"]))
            fileuse2.append(x)
    
    fileuses = fileuse2
    
    currentids = []
    
    for j in jobs:
        job_el = ET.SubElement(jobTable_el,"job")
        for k,v in j.items():
            job_el.attrib[k] = v

    #Now we are in a position to fix statuses of sub jobs.
    for j in jobTable_el:
        if len(j.attrib["jobnumber"].split(".")) > 1:
            topJobNum = j.attrib["jobnumber"].split(".")[0]
            for k in jobTable_el:
                if len(k.attrib["jobnumber"].split(".")) == 1 and k.attrib["jobnumber"].split(".")[0] == topJobNum:
                    if k.attrib["status"] == "6":
                        j.attrib["status"] = "6"

    for f in fileuses:
        file_el = ET.Element("fileuse")
        file_el.attrib["fileid"] = f["fileid"]
        file_el.attrib["jobid"] = f["jobid"]
        file_el.attrib["roleid"] = f["roleid"]
        file_el.attrib["jobparamname"] = f["jobparamname"]
        fileUseTable_el.append(file_el)
    
    for f in files:
        file_el = ET.Element("file")
        for k,v in f.items():
            if v is not None:
                if not k in ("number","inout"):
                    if k == "fileid" and v in currentids:
                        break
                    file_el.attrib[k] = v
                    if k == "fileid":
                        currentids.append(v)
        if len(file_el.attrib)>0:
            fileTable_el.append(file_el)
    
    
    #sys.exit()
    
    #print projectName
    #print hostName
    #print userId
    #print ccp4iVersion
    #print projectId
    #print creationTime
    #print OS
    
    fn = ET.SubElement(ccp4i2_header,"function")
    fn.text = "PROJECTDATABASE"
    projectName_el = ET.SubElement(ccp4i2_header,"projectName")
    projectName_el.text = projectName
    hostName_el = ET.SubElement(ccp4i2_header,"hostName")
    hostName_el.text = hostName
    userId_el = ET.SubElement(ccp4i2_header,"userId")
    userId_el.text = userId
    ccp4iVersion_el = ET.SubElement(ccp4i2_header,"ccp4iVersion")
    ccp4iVersion_el.text = ccp4iVersion
    projectId_el = ET.SubElement(ccp4i2_header,"projectId")
    projectId_el.text = projectId
    creationTime_el = ET.SubElement(ccp4i2_header,"creationTime")
    creationTime_el.text = datetime.datetime.strftime(creationTime,"%H:%M %d/%b/%y")
    OS_el = ET.SubElement(ccp4i2_header,"OS")
    OS_el.text = OS
    
    databaseTable_el = ET.SubElement(ccp4i2_body,"databaseTable") #Ug.
    
    projectTable_el = ET.SubElement(ccp4i2_body,"projectTable")
    project_el = ET.SubElement(projectTable_el,"project")
    project_el.attrib["projectid"] = projectId
    project_el.attrib["projectname"] = projectName
    project_el.attrib["projectcreated"] = str(datetime_to_float(creationTime))
    project_el.attrib["lastjobnumber"] = lastJobNumber
    project_el.attrib["projectdirectory"] = projectRoot
    project_el.attrib["username"] = userId
    
    importfileTable_el = ET.SubElement(ccp4i2_body,"importfileTable")
    exportfileTable_el = ET.SubElement(ccp4i2_body,"exportfileTable")
    xdataTable_el = ET.SubElement(ccp4i2_body,"xdataTable")
    commentTable_el = ET.SubElement(ccp4i2_body,"commentTable")
    projectcommentTable_el = ET.SubElement(ccp4i2_body,"projectcommentTable")
    jobkeyvalueTable_el = ET.SubElement(ccp4i2_body,"jobkeyvalueTable")
    jobkeycharvalueTable_el = ET.SubElement(ccp4i2_body,"jobkeycharvalueTable")
    fileassociationmemberTable_el = ET.SubElement(ccp4i2_body,"fileassociationmemberTable")
    fileassociationTable_el = ET.SubElement(ccp4i2_body,"fileassociationTable")
    projecttagTable_el = ET.SubElement(ccp4i2_body,"projecttagTable")
    tagTable_el = ET.SubElement(ccp4i2_body,"tagTable")
    
    for kv in jkv:
        jobid = kv[0]
        for k,v in kv[1].items():
           if type(v) == float or type(v) == int:
               kve = ET.SubElement(jobkeyvalueTable_el,"jobkeyvalue")
               kve.attrib["jobid"] = jobid
               kve.attrib["keytypeid"] = str([x[1] for x in KEYTYPELIST].index(k))
               kve.attrib["value"] = str(v)
           else:
               pass # We'll add if to jobkeycharvalueTable later
    
    for kv in jkv:
        jobid = kv[0]
        for k,v in kv[1].items():
           if type(v) == float or type(v) == int:
               pass
           else:
               kve = ET.SubElement(jobkeycharvalueTable_el,"jobkeycharvalue")
               kve.attrib["jobid"] = jobid
               kve.attrib["keytypeid"] = str([x[1] for x in KEYTYPELIST].index(k))
               kve.attrib["value"] = v
    
    return root

if __name__ == "__main__":
    project_tree = generate_xml_from_project_directory(sys.argv[1])
    ET.indent(project_tree)
    print(ET.tostring(project_tree).decode())
