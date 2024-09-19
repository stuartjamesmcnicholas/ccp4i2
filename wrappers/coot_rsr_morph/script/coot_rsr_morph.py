from __future__ import print_function

import pathlib
import sys,os
from xml.etree import ElementTree as ET

from core import CCP4File
from core.CCP4ModelData import CPdbDataFile
from core.CCP4PluginScript import CPluginScript

import ctypes
import chapi
import gemmi

class coot_rsr_morph(CPluginScript):

    TASKMODULE = "refinement"
    TASKTITLE = "Real space refinement morphing with coot api"
    TASKNAME = "coot_rsr_morph"
    TASKVERSION = 202409171000
    WHATNEXT = ["prosmart_refmac"]
    ASYNCHRONOUS = True
    TIMEOUT_PERIOD = 9999999.9
    MAINTAINER = "stuart.mcnicholas@york.ac.uk"

    def chapi_rsr_morph(self):

        #TODO set_use_rama_plot_restraints ???

        sys.stdout.flush()
        sys.stderr.flush()
        outFormat = "cif" if self.container.inputData.XYZIN.isMMCIF() else "pdb"
        oldFullPath = pathlib.Path(str(self.container.outputData.XYZOUT.fullPath))
        if outFormat == "cif":
            self.container.outputData.XYZOUT.setFullPath(str(oldFullPath.with_suffix('.cif')))
            self.container.outputData.XYZOUT.contentFlag.set(CPdbDataFile.CONTENT_FLAG_MMCIF)

        pdb_path = str(self.container.inputData.XYZIN.fullPath)
        mtz_path = str(self.container.inputData.FPHIIN.fullPath)
        out_path = os.path.normpath(str(self.container.outputData.XYZOUT))
        if sys.platform.startswith("win"):
            out_path = out_path.replace("\\","\\\\")
        local_radius = self.container.controlParameters.LOCAL_RADIUS
        gm_alpha = self.container.controlParameters.GM_ALPHA
        blur_b_factor = self.container.controlParameters.BLUR_B_FACTOR

        mc = chapi.molecules_container_py(True)
        mc.set_use_gemmi(True)
        imol = mc.read_pdb(str(self.container.inputData.XYZIN.fullPath))
        gemmiStructure = gemmi.read_structure(str(self.container.inputData.XYZIN.fullPath))
        imap = mc.read_mtz(str(self.container.inputData.FPHIIN.fullPath),"F","PHI","",False,False)
        mc.generate_self_restraints(imol, local_radius)

        mc.set_refinement_geman_mcclure_alpha(gm_alpha)

        imap_blurred = mc.sharpen_blur_map(imap, blur_b_factor, False)
        mc.set_imol_refinement_map(imap_blurred)

        chains = mc.get_chains_in_model(imol)
        for model in gemmiStructure:
            for chain in model:
                firstResidue, lastResidue = chain[0].seqid.num,chain[-1].seqid.num
                mc.refine_residue_range(imol,chain.name,firstResidue, lastResidue,4000)

        mc.write_coordinates(imol,out_path)
        
        libc = ctypes.CDLL(None)
        if sys.platform == "darwin":
            c_stdout = ctypes.c_void_p.in_dll(libc, '__stdoutp')
            libc.fflush(c_stdout)
        elif sys.platform.startwith("linux"):
            c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
            libc.fflush(c_stdout)

        return CPluginScript.SUCCEEDED

    def process(self, command=None, handler=None, **kw):

        self.chapi_rsr_morph()

        status = CPluginScript.FAILED
        if os.path.exists(self.container.outputData.XYZOUT.__str__()):
            status = CPluginScript.SUCCEEDED
        print(
            "coot_rsr_morph.handleFinish",
            self.container.outputData.XYZOUT,
            os.path.exists(self.container.outputData.XYZOUT.__str__()),
        )
        # Create a trivial xml output file
        root = ET.Element("coot_rsr_morph")
        self.container.outputData.XYZOUT.subType = 1
        xml_file = CCP4File.CXmlDataFile(fullPath=self.makeFileName("PROGRAMXML"))
        xml_file.saveFile(root)
        self.reportStatus(status)
        return status
