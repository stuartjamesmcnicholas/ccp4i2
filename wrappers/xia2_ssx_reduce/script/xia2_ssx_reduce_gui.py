#
#  Copyright (C) 2024 UKRI/STFC Rutherford Appleton Laboratory, UK.
#
#  Author: Martin Maly, David Waterman
#

from PySide2 import QtCore, QtWidgets
from qtgui.CCP4TaskWidget import CTaskWidget
from core import CCP4Container
import qtgui
from .find_expt_refl import find_expt_refl


class FindIntegratedWorker(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, path, preference):
        self._path = path
        self._preference = preference
        super(FindIntegratedWorker, self).__init__()

    def run(self):
        self.results = find_expt_refl(self._path, self._preference)
        self.finished.emit()


class xia2_ssx_reduce_gui(CTaskWidget):

    # Subclass CTaskWidget to give specific task window
    TASKTITLE = "Reduction of serial datasets using xia2.ssx_reduce"
    DESCRIPTION = "Select integrated data from xia2.ssx or dials.stills_process"
    TASKNAME = "xia2_ssx_reduce"
    # TASKMODULE = "test"
    TASKMODULE = "data_reduction"
    TASKVERSION = 0.0
    RANK = 1
    SHORTTASKTITLE = "xia2.ssx_reduce"
    TASKVERSION = 0.1

    def drawContents(self):

        # Input data
        self.openFolder(folderFunction="inputData")

        self.createLine(
            [
                "tip",
                "Select a directory in which to search for xia2.ssx integrated files",
                "subtitle",
                "Search for xia2.ssx integrated files",
            ]
        )
        self.createLine(
            [
                'label', 'Search for',
                'widget',
                '-guiMode',
                'radio',
                'SEARCH_PREFERENCE',
                'label', 'files',
            ]
        )
        self.connectDataChanged('SEARCH_PREFERENCE', self.updateScaleMerge)
        self.createLine(
            [
                "widget",
                "-title",
                "Search for xia2.ssx integrated files",
                "SEARCH_ROOT_DIR",
            ]
        )
        self.createLine(
            [
                "widget",
                "-title",
                "integrated.refl or scaled.refl files (each must have an associated .expt file)",
                "DIALS_INTEGRATED",
            ]
        )
        # self.createLine(['tip', 'Reference structure or data', 'widget', 'reference'])

        self.closeSubFrame()

        # Basic parameters
        self.createLine(
            ["tip", "Subset of xia2.ssx_reduce control parameters", "subtitle", "Basic parameters"]
        )
        self.autoGenerate(
            self.container.controlParameters,
            selection={"includeParameters": ["d_min"]},
        )
        self.autoGenerate(
            self.container.controlParameters,
            selection={"includeParameters": ["reference"]},
        )
        #self.simpleAutoGenerate(container=self.container.controlParameters)
        #self.simpleAutoGenerateInputFiles(container=self.container.inputFiles)

        # Advanced parameters in a separate folder
        self.openFolder(folderFunction="controlParameters", title="Advanced parameters")
        self.createLine(['label', 'Batch size', 'widget', 'reduction_batch_size'])
        self.createLine(['label', 'Partiality threshold', 'widget', 'partiality_threshold'])
        # self.createLine(['label', 'I/sigma threshold', 'widget', 'filtering__mean_i_over_sigma_threshold']) # not in DIALS stable release yet
        self.createLine(['label', 'Tolerance for lattice symmetry analysis', 'widget', 'symmetry__lattice_symmetry_max_delta'])
        self.createLine(['label', 'Workflow: ', 'widget', '-guiMode', 'radio', 'workflow__steps' ] )
        self.createLine(['label', 'Keep anomalous pairs separate during scaling', 'widget', 'scaling__anomalous'], toggle=['workflow__steps', 'open', ['scale+merge']])
        self.createLine(['label', 'High resolution cutoff for dials.cosym', 'widget', 'dials_cosym_phil_d_min'])
        self.createLine(['label', 'Number of processors for multiprocessing', 'widget', 'multiprocessing__nproc'])
        self.openSubFrame(frame=[True])
        self.createLine(['advice', 'Clustering'])
        self.createLine(['label', 'Clustering threshold', 'widget', 'clustering__threshold'])
        self.createLine(['label', 'Absolute angle tolerance', 'widget', 'clustering__absolute_angle_tolerance'])
        self.createLine(['label', 'Absolute length tolerance', 'widget', 'clustering__absolute_length_tolerance'])
        self.createLine(['label', 'Central unit cell', 'widget', 'clustering__central_unit_cell'])
        self.closeSubFrame()
        # self.openSubFrame(frame=[True])
        # self.createLine(['advice', 'Grouping'])
        # self.createLine(['label', 'Grouping .yml file', 'widget', 'grouping'])
        self.createLine(['label', 'Dose series - number of repeated measurements at each point', 'widget', 'dose_series_repeat'])
        # self.closeSubFrame()
        self.openSubFrame(frame=[True])
        self.createLine(['advice', 'Reference model options (if used)'])
        self.createLine(['label', 'Average solvent density k_sol', 'widget', 'reference_model__k_sol'])
        self.createLine(['label', 'Average solvent B-factor b_sol', 'widget', 'reference_model__b_sol'])
        self.closeSubFrame()

        # Advanced parameters in a separate folder - autogenerated
        # self.openFolder(
        #     folderFunction="controlParameters",
        #     title="Advanced parameters",
        #     drawFolder=self.drawAdvanced,
        # )

        self.connectDataChanged("SEARCH_ROOT_DIR", self.handleSearchRootDir)

        return

    def updateScaleMerge(self):
        if self.container.inputData.SEARCH_PREFERENCE == 'scaled':
            self.container.controlParameters.workflow.workflow__steps.set('merge')
        elif self.container.inputData.SEARCH_PREFERENCE == 'integrated':
            self.container.controlParameters.workflow.workflow__steps.set('scale+merge')

    @QtCore.Slot()
    def handleSearchRootDir(self):

        self.getWidget("SEARCH_ROOT_DIR").setEnabled(False)
        self.getWidget("DIALS_INTEGRATED").setEnabled(False)
        # Set up a thread that is owned by the application instance, to avoid
        # crashes due to thread object going out of scope
        self.find_integrated_thread = QtCore.QThread(
            parent=QtWidgets.QApplication.instance()
        )
        self.find_integrated_worker = FindIntegratedWorker(
            str(self.container.inputData.SEARCH_ROOT_DIR),
            str(self.container.inputData.SEARCH_PREFERENCE)
        )
        self.find_integrated_worker.moveToThread(self.find_integrated_thread)
        self.find_integrated_thread.started.connect(self.find_integrated_worker.run)
        self.find_integrated_worker.finished.connect(self.handleSearchRootDirFinished)
        self.find_integrated_worker.finished.connect(self.find_integrated_thread.quit)
        self.find_integrated_thread.finished.connect(
            self.find_integrated_thread.deleteLater
        )
        self.find_integrated_thread.start()

    @QtCore.Slot()
    def handleSearchRootDirFinished(self):

        dials_integrated = self.getWidget("DIALS_INTEGRATED")
        self.getWidget("SEARCH_ROOT_DIR").setEnabled(True)
        dials_integrated.setEnabled(True)
        results = self.find_integrated_worker.results
        self.container.inputData.DIALS_INTEGRATED.unSet()
        self.container.inputData.DIALS_INTEGRATED.set([r + ".refl" for r in results])

        dials_integrated.updateViewFromModel()

        # Attempt to set input as valid to get rid of red highlights
        # (does not currently work)
        dials_integrated.validate()
        for i in range(dials_integrated.getNofLines()):
            dials_integrated.setValidity(i)

        # Update the widget to redraw
        dials_integrated.updateViewFromModel()
        dials_integrated.validate()
        # I do not know why this is necessary, but it seems to be.
        childer = dials_integrated.parent().findChildren(QtWidgets.QWidget)
        for child in childer:
            if type(child) is qtgui.CCP4Widgets.CListViewListWidget:
                if hasattr(child.parent(), "isValid"):
                    if child.parent().isValid:
                        child.setStyleSheet("QFrame { background-color:white}")
                    else:
                        child.setStyleSheet(
                            'QFrame [isValid="false"] { background: qlineargradient( x1:0.15 y1:0, x2:1 y2:0, stop:0 transparent, stop:1 #f55); border:0px; }'
                        )
        self.validate()

    # def drawAdvanced(self):
    #     self.nestedAutoGenerate(
    #         container=self.container.controlParameters, expertLevel=["0", "1", "2", "3"]
    #     )

    # def simpleAutoGenerate(self, container):
    #     """Autogenerate a specific selection of basic parameters"""

    #     self.autoGenerate(
    #         container,
    #         selection={"includeParameters": ["d_min"]},
    #     )
    #     self.autoGenerate(
    #         container,
    #         selection={"includeParameters": ["reference"]},
    #     )

    # def simpleAutoGenerateInputFiles(self, container):
    #     """Autogenerate a specific selection of basic parameters"""
    #     self.autoGenerate(
    #         container,
    #         selection={"includeParameters": ["reference"]},
    #     )


    def nestedAutoGenerate(self, container, expertLevel=["0"]):
        """Autogenerate a GUI from nested containers using only elements at
        the specified expertLevels"""

        dataOrder = container.dataOrder()
        contents = [getattr(container, name) for name in dataOrder]

        # Filter by expertLevel
        expert = [
            c.qualifiers("guiDefinition").get("expertLevel", "0") for c in contents
        ]
        dataOrder = [d for d, e in zip(dataOrder, expert) if e in expertLevel]
        contents = [c for c, e in zip(contents, expert) if e in expertLevel]

        # If this container has any content other than nested containers,
        # autogenerate that content
        data = [
            name
            for name, model in zip(dataOrder, contents)
            if not isinstance(model, CCP4Container.CContainer)
        ]
        subcontainers = [
            model for model in contents if isinstance(model, CCP4Container.CContainer)
        ]
        if data:
            # only open a sub-frame if there is a label available
            make_subframe = container.qualifiers("guiLabel") is not NotImplemented
            if make_subframe:
                self.openSubFrame(frame=True)
            self.autoGenerate(container, selection={"includeParameters": data})
            for c in subcontainers:
                self.nestedAutoGenerate(c, expertLevel=expertLevel)
            if make_subframe:
                self.closeSubFrame()
        else:
            # just drill down without opening a sub frame
            for c in subcontainers:
                self.nestedAutoGenerate(c, expertLevel=expertLevel)
        return