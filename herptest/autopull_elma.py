from PySide2 import QtCore, QtWidgets, QtGui
import os, subprocess
import numpy as np
from . import canvas_interface

class AutopullElma(canvas_interface.AbstractCanvasInterface):
    def __init__(self):
        super().__init__()

    def createControls(self):
        #this gets called by the createUI method of the parent class
        self.controls = QtWidgets.QHBoxLayout()

        self.downloadBox = QtWidgets.QGroupBox("Download Assignment Submissions")
        downloadGrid = QtWidgets.QGridLayout()

        self.downloadDestLabel = QtWidgets.QLabel("Download Location:")
        self.downloadDest = QtWidgets.QLineEdit()
        self.downloadDest.setText(os.getcwd())
        self.downloadDestSelect = QtWidgets.QPushButton("Browse")
        self.downloadDestSelect.clicked.connect(self.downloadFilePicker)
        self.downloadDestSelect.setFixedWidth(100)

        downloadGrid.addWidget(self.downloadDestLabel, 0,0)
        downloadGrid.addWidget(self.downloadDestSelect, 0,1)
        downloadGrid.addWidget(self.downloadDest, 1,0, 1,2) #rowspan 1 and column span 2

        downloadGrid.addWidget(QtWidgets.QLabel(), 2,0, 1,2)#rowspan 1 and column span 2, spacing

        self.downloadAssignments = QtWidgets.QPushButton("Download Submissions for Selected Assignment")
        self.downloadAssignments.clicked.connect(self.handleDownload)
        self.downloadAssignments.setEnabled(False)
        downloadGrid.addWidget(self.downloadAssignments, 3,0, 1,2) #rowspan 1 and column span 2

        self.downloadStatus = QtWidgets.QLabel("Status: Select an assignment")
        downloadGrid.addWidget(self.downloadStatus, 4,0,1,2) #rowspan 1 and column span 2

        self.elmaBox = QtWidgets.QGroupBox("Run ELMA on Submissions")
        elmaGrid = QtWidgets.QGridLayout()

        self.elmaSourceLabel = QtWidgets.QLabel("ELMA Source File:")
        self.elmaSource = QtWidgets.QLineEdit()
        self.elmaSource.setText(os.getcwd() + "/submissions.zip")
        self.elmaSourceSelect = QtWidgets.QPushButton("Browse")
        self.elmaSourceSelect.clicked.connect(self.elmaSourceFilePicker)
        self.elmaSourceSelect.setFixedWidth(100)

        elmaGrid.addWidget(self.elmaSourceLabel, 0,0)
        elmaGrid.addWidget(self.elmaSourceSelect, 0,1)
        elmaGrid.addWidget(self.elmaSource, 1,0, 1,2) #rowspan 1 and column span 2

        self.elmaDestLabel = QtWidgets.QLabel("ELMA Destination:")
        self.elmaDest = QtWidgets.QLineEdit()
        self.elmaDest.setText(os.getcwd() + "/Projects")
        self.elmaDestSelect = QtWidgets.QPushButton("Browse")
        self.elmaDestSelect.clicked.connect(self.elmaDestFilePicker)
        self.elmaDestSelect.setFixedWidth(100)

        elmaGrid.addWidget(self.elmaDestLabel, 3,0)
        elmaGrid.addWidget(self.elmaDestSelect, 3,1)
        elmaGrid.addWidget(self.elmaDest, 4,0, 1,2) #rowspan 1 and column span 2

        elmaGrid.addWidget(QtWidgets.QLabel(), 5,0, 1,2)#rowspan 1 and column span 2, spacing

        self.runELMA = QtWidgets.QPushButton("Run ELMA on the Selected ZIP Archive")
        self.runELMA.clicked.connect(self.handleELMA)
        elmaGrid.addWidget(self.runELMA, 6,0, 1,2) #rowspan 1 and column span 2

        self.elmaStatus = QtWidgets.QLabel("Status: Waiting to run...")
        elmaGrid.addWidget(self.elmaStatus, 7,0,1,2) #rowspan 1 and column span 2

        self.downloadBox.setLayout(downloadGrid)
        self.elmaBox.setLayout(elmaGrid)
        self.controls.addWidget(self.downloadBox)
        self.controls.addWidget(self.elmaBox)
        #use the layout tracked by the parent class, NOT the .layout() tracked by QT
        self.layout.addLayout(self.controls)



    def onSelect(self):
        #called in the handleSelect method of the parent, we need to invoke approveUpload()
        self.approveUpload()

    def approveUpload(self):
        print("approveUpload from elma")
        if self.assignmentReady and self.downloadDest.text() != "" :
            self.downloadAssignments.setEnabled(True)
            self.downloadStatus.setText("Status: Ready to download")
            self.downloadStatus.setStyleSheet("color: black")
        else:
            self.downloadAssignments.setEnabled(False)
            self.downloadStatus.setText("Status: Select an assignment")
            self.downloadStatus.setStyleSheet("color: black")


    def downloadFilePicker(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly)
        dialog.setWindowTitle("Select Assignments Download Location:")

        if dialog.exec_():
            self.downloadDest.setText(dialog.selectedFiles()[0])

    def elmaSourceFilePicker(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setWindowTitle("Select ELMA Source File:")

        if dialog.exec_():
            self.elmaSource.setText(dialog.selectedFiles()[0])

    def elmaDestFilePicker(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly)
        dialog.setWindowTitle("Select ELMA Output Location:")

        if dialog.exec_():
            self.elmaDest.setText(dialog.selectedFiles()[0])
        
    def handleDownload(self):
        #use the canvasWrapper attribute of the parent class
        self.downloadStatus.setText("Status: Downloading submissions.zip")
        self.downloadStatus.setStyleSheet("color: black")
        self.downloadStatus.repaint()
        try:
            self.canvasWrapper.download_submissions(self.currentCourse, self.currentAssignment, self.downloadDest.text())
            self.elmaSource.setText(self.downloadDest.text() + "/submissions.zip")
            self.downloadStatus.setText("Status: Download complete")
            self.downloadStatus.setStyleSheet("color: black")
        except:
            print("inside except")
            self.downloadStatus.setText("Status: Error during download")
            self.downloadStatus.setStyleSheet("color: red")
            self.downloadStatus.repaint()

    def handleELMA(self):
        self.elmaStatus.setText("Status: Running ELMA")
        process = subprocess.Popen(['elma', self.elmaSource.text(), self.elmaDest.text()], stdout=subprocess.PIPE)
        
        return_code = None
        while True:
            return_code = process.poll()
            if return_code is not None:
                #print('RETURN CODE', return_code)
                break
        if return_code != 0:
            self.elmaStatus.setText("Status: ELMA failed")
            self.elmaStatus.setStyleSheet("color: red")
        else:
            self.elmaStatus.setText("Status: Successfully ran ELMA")
            self.elmaStatus.setStyleSheet("color: black")

