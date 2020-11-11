from PySide2 import QtCore, QtWidgets, QtGui
import os, subprocess
import numpy as np
from . import grade_csv_uploader

class CanvasUploader(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        #TODO fix this to actually create self.canvas
        self.fetchCanvasUtil("path", "token")

        #init trackers, updating this makes it simpler to pass this data to upload
        self.courseDict = None
        self.currentCourse = None
        self.currentAssignment = None
        self.assignmentReady = False
        self.fileReady = False
        
        self.layout = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel()

        self.containerView = QtWidgets.QTreeView()
        self.showCourses() #change later to fetch REAL courses from canvas
        
        self.containerView.clicked[QtCore.QModelIndex].connect(self.handleSelection)

        self.uploadContainer = QtWidgets.QGridLayout()
        self.csvLabel = QtWidgets.QLabel("Select CSV to Upload")
        self.csvLabel.setMaximumHeight(50)
        self.csvPathField = QtWidgets.QLineEdit()
        self.csvSelect = QtWidgets.QPushButton("Browse")
        self.csvSelect.setFixedWidth(100)
        self.csvSelect.clicked.connect(self.uploadFilePicker)

        self.modeLabel = QtWidgets.QLabel("Upload CSV as:")
        self.modeLayout = QtWidgets.QVBoxLayout()
        self.modeSelectGroup = QtWidgets.QButtonGroup()
        self.modeSelectGroup.setExclusive(True)
        self.modeSelectRubric = QtWidgets.QCheckBox("Structured Rubric")
        self.modeSelectTests = QtWidgets.QCheckBox("Test Suite Results")
        self.modeSelectGroup.addButton(self.modeSelectRubric)
        self.modeSelectGroup.addButton(self.modeSelectTests)
        self.modeLayout.addWidget(self.modeSelectRubric)
        self.modeLayout.addWidget(self.modeSelectTests)
        self.modeLayout.setContentsMargins(10,10,10,10)

        self.uploadButton = QtWidgets.QPushButton("Upload")
        self.uploadButton.setFixedWidth(100)
        self.uploadButton.setFixedHeight(50)
        self.uploadButton.clicked.connect(self.handleUpload)
        self.uploadButton.setEnabled(False)

        self.uploadContainer.addWidget(self.csvLabel,0,0)
        self.uploadContainer.addWidget(self.csvPathField,1,0)
        self.uploadContainer.setAlignment(self.csvPathField, QtCore.Qt.AlignTop)
        self.uploadContainer.addWidget(self.csvSelect,1,1)
        self.uploadContainer.setAlignment(self.csvSelect, QtCore.Qt.AlignTop)
        self.uploadContainer.addWidget(self.modeLabel,0,2)
        self.uploadContainer.addLayout(self.modeLayout,1,2)
        self.uploadContainer.setAlignment(self.modeLayout, QtCore.Qt.AlignTop)
        self.uploadContainer.addWidget(self.uploadButton,1,3)
        self.layout.setAlignment(self.uploadContainer, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.containerView)
        self.layout.addLayout(self.uploadContainer)
        self.setLayout(self.layout)

    def approveUpload(self):
        if self.fileReady and self.assignmentReady:
            self.uploadButton.setEnabled(True)
        else:
            self.uploadButton.setEnabled(False)
    def uploadFilePicker(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setWindowTitle("Select File to Upload")
        dialog.setNameFilter("CSV (*.csv)")

        if dialog.exec_():
            self.uploadPath = dialog.selectedFiles()[0]
            self.csvPathField.setText(self.uploadPath)
            self.fileReady = True
        self.approveUpload()

    def handleSelection(self, index):
        item = self.activeModel.itemFromIndex(index)
        if item.text().find("<-") != -1:
            #go back to the courses page
            
            self.currentCourse = None
            self.currentAssignment = None
            self.showCourses()
            self.assignmentReady = False
        elif item.text().find("->") != -1:
            #go down a level
            courseNameIndex = self.activeModel.itemFromIndex(index.siblingAtColumn(0))
            
            self.currentCourse = courseNameIndex.text()
            self.showAssignments(courseNameIndex)
        elif self.mode == "assignments":
            self.currentAssignment = self.activeModel.itemFromIndex(index.siblingAtColumn(0)).text()
            self.assignmentReady = True
        elif self.mode == "courses":
            self.currentCourse = self.activeModel.itemFromIndex(index.siblingAtColumn(0)).text()
        print("current course: " + str(self.currentCourse))
        print("current assignment: " + str(self.currentAssignment))
        self.approveUpload()

    def handleUpload(self):
        #TODO invoke Tyler or Matt's code depending on whether self.modeSelectTests or self.modeSelectRubric is active
        if self.modeSelectTests.checkState() == QtCore.Qt.Checked:
            #test results mode, call matty's code
            print("test suite mode!")
        elif self.modeSelectRubric.checkState() == QtCore.Qt.Checked:
            #rubric mode, call tyler's code
            print("rubric mode!")
        else:
            #neither was selected, create a warning dialog and do nothing
            dialog = QtWidgets.QMessageBox()
            dialog.setText('Select either "Structured Rubric" or "Test Suite Results " mode in order to upload.')
            dialog.setWindowTitle('Select an Upload Mode!')
            dialog.exec_()
        print("upload {}".format(self.uploadPath))
        pass

    def fetchCanvasUtil(self, dotenvpath, token_type):
        self.tokenName = "TEST"
        self.canvas = None
        #self.canvas = grade_csv_uploader.CanvasUtil(canvas_url, dotenv_path, token_type)
        pass

    def fetchCourseList(self):
        #courses = self.canvas.get_courses_this_semester() # dictionary with keys:course name, values:course id
        courses = {}
        courses["Course 1"] = 12361234
        courses["Course 2"] = 16234123
        courses["Course 3"] = 61234213

        self.courseDict = courses

    def showCourses(self):
        self.mode = "courses"
        self.title.setText("Courses for " + self.tokenName)
        coursesModel = QtGui.QStandardItemModel()
        coursesModel.setHorizontalHeaderLabels(["Course Name", "Course ID", " "])

        if not self.courseDict:
            self.fetchCourseList()     

        for course in self.courseDict.keys():
            courseName = QtGui.QStandardItem(course)
            courseName.setEditable(False)
            courseId = QtGui.QStandardItem(str(self.courseDict[course]))
            courseId.setEditable(False)
            expandCourse = QtGui.QStandardItem("Expand ->")
            expandCourse.setEditable(False)
            coursesModel.appendRow([courseName, courseId, expandCourse])
        
        self.coursesActive = True
        self.activeModel = coursesModel
        self.containerView.setModel(self.activeModel)
        for i in range(0,3):
            self.containerView.resizeColumnToContents(i)

    def showAssignments(self, course):
        self.mode = "assignments"
        self.title.setText("Assignments for " + course.text())
        assignmentsModel = QtGui.QStandardItemModel()
        assignmentsModel.setHorizontalHeaderLabels(["Assignment Name", "Assignment ID", "Graded"])

        
        assignments = {}
        assignments["Assignment 1"] = [61981981, True]
        assignments["Assignment 2"] = [98139123, False]
        assignments["Assignment 3"] = [98716230, True]

        backSelect = QtGui.QStandardItem("<- Return to Courses")
        backSelect.setEditable(False)   
        assignmentsModel.appendRow([backSelect])

        for assignment in assignments.keys():
            assignmentName = QtGui.QStandardItem(assignment)
            assignmentName.setEditable(False)
            assignmentId = QtGui.QStandardItem(str(assignments[assignment][0]))
            assignmentId.setEditable(False)
            assignmentGraded = QtGui.QStandardItem(str(assignments[assignment][1]))
            assignmentGraded.setEditable(False)
            assignmentsModel.appendRow([assignmentName, assignmentId, assignmentGraded])

        self.coursesActive = False
        self.activeModel = assignmentsModel
        self.containerView.setModel(self.activeModel)
        for i in range(0,3):
            self.containerView.resizeColumnToContents(i)




   
