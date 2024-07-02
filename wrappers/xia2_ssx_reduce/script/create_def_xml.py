#
#  Copyright (C) 2024 UKRI/STFC Rutherford Appleton Laboratory, UK.
#
#  Author: David Waterman, Martin Maly
#  Acknowledgements: based on ideas and code by Nat Echols and Martin Noble.
#

"""Create xia2_ssx_reduce.def.xml from PHIL parameters"""

import sys
import os
from lxml import etree

# Nasty trick required to import PhilTaskCreator when running with ccp4-python
this_dir = os.path.dirname(os.path.realpath(__file__))
ccp4i2_dir = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
sys.path.append(ccp4i2_dir)
from utils.phil_handlers import PhilTaskCreator


class Xia2SsxReduceTaskCreator(PhilTaskCreator):
    def __init__(self, debug=False):

        from xia2.cli.ssx_reduce import phil_scope

        PhilTaskCreator.__init__(self, phil_scope, debug)
        self.fmt_dic["PLUGINNAME"] = "xia2_ssx_reduce"

        self.inputDataXML = etree.fromstring(
            """
<container id="inputData">
  <content id="SEARCH_ROOT_DIR">
    <className>CDataFile</className>
    <qualifiers>
      <mustExist>True</mustExist>
      <allowUndefined>True</allowUndefined>
      <isDirectory>True</isDirectory>
      <guiLabel>Root directory</guiLabel>
      <toolTip>Start search from this directory</toolTip>
    </qualifiers>
  </content>

  <content id="DIALS_INTEGRATED">
    <className>CList</className>
    <qualifiers>
      <guiLabel>DIALS .refl</guiLabel>
      <toolTip>Must have an associated .expt file</toolTip>
      <listMinLength>2</listMinLength>
    </qualifiers>
    <subItem>
      <className>CDataFile</className>
      <qualifiers>
        <saveToDb>False</saveToDb>
        <mustExist>True</mustExist>
        <allowUndefined>True</allowUndefined>
        <isDirectory>False</isDirectory>
        <guiLabel>Bar</guiLabel>
        <toolTip>Foo</toolTip>
      </qualifiers>
    </subItem>
  </content>

  <content id="XIA2_RUN">
    <className>CList</className>
    <qualifiers>
        <guiLabel>Previous xia2 run directories</guiLabel>
        <listMinLength>2</listMinLength>
    </qualifiers>
    <subItem>
      <className>CDataFile</className>
      <qualifiers>
        <mustExist>True</mustExist>
        <allowUndefined>True</allowUndefined>
        <isDirectory>True</isDirectory>
        <guiLabel>Path to a previous xia2 run directory (containing a DataFiles sub-directory)</guiLabel>
        <toolTip>Integration files will be automatically extracted from a previous xia2 run</toolTip>
      </qualifiers>
    </subItem>
  </content>

  <qualifiers/>
</container>
"""
        )

        self.outputDataXML = etree.fromstring(
            """
<container id="outputData">
  <content id="HKLOUT">
    <className>CList</className>
    <qualifiers/>
    <subItem>
      <className>CObsDataFile</className>
      <qualifiers>
        <default/>
        <contentFlag>
          <min>0</min>
        </contentFlag>
        <subType>
          <menuText>observed data,derived data,reference data</menuText>
          <onlyEnumerators>True</onlyEnumerators>
          <enumerators>1,2,3</enumerators>
          <default>1</default>
        </subType>
      </qualifiers>
    </subItem>
  </content>
  <content id="PERFORMANCE">
    <className>CDataReductionCCPerformance</className>
    <qualifiers/>
  </content>
  <qualifiers/>
</container>
"""
        )

    def __call__(self):
        self._remove_elements_by_id(
            self.phil_tree,
            [
                "input__experiments",
                "input__reflections",
                "input__directory",
                "input__processed_directory",
                "input__validate",
                "batch_size",
                "scaling__model",
            ],
        )

        if self.debug:
            print(etree.tostring(self.phil_tree, pretty_print=True))

        super(Xia2SsxReduceTaskCreator, self).__call__()


if __name__ == "__main__":

    x2mtc = Xia2SsxReduceTaskCreator()
    x2mtc()