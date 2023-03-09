########################################################################################################################
# Telemetry Data Program Made by Stephane Simard
# Started June 15th 2022
########################################################################################################################

from datetime import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication

from PyQt5.QtGui import QPolygon, QPolygonF, QColor, QPen, QFont, QPainter, QFontMetrics, QConicalGradient, \
    QRadialGradient, QFontDatabase

from PyQt5.QtCore import Qt, QTime, QTimer, QPoint, QPointF, QRect, QSize, QObject, pyqtSignal

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import sys
import os
from os import walk

from pathlib import Path
import shutil
from qt_material import apply_stylesheet
import pandas as pd
import numpy as np
import math
import tempfile, shutil, os
import os.path
from os import path
from distutils.dir_util import copy_tree

# from Testing5 import *

########################################################################################################################
# Initializing Temp Save File
########################################################################################################################

temp_dir = tempfile.gettempdir()

temp_path = os.path.join(temp_dir, "SAA Temp Save")

########################################################################################################################
#Old Method

# path = "C:\\Users\\steph\\OneDrive\\Documents\\SAA Wing\\Coding\\Can Bus Data Reading"
# Path(path).mkdir(parents=True, exist_ok=True)
#
# os.chdir(path)
# NewFolder = "Temporary Saves"
# os.makedirs(NewFolder, exist_ok=True)
#
# path2 = "C:\\Users\\steph\\OneDrive\\Documents\\SAA Wing\\Coding\\Can Bus Data Reading\\Temporary Saves"
# os.chdir(path2)

########################################################################################################################
# Global Variables
########################################################################################################################

IDList = ("ID 00d0", "ID 00d1", "ID 00d3", "ID 00d4", "ID 0140", "ID 0141", "ID 0360", "ID 0361")

ID00d0 = ("Steering Angle",
          "Latitudinal Acceleration",
          "Longitudinal Acceleration",
          "Combined Acceleration")

ID00d1 = ("OverAll Speed",
          "Brake Pressure")

ID00d3 = ("Traction Control State",)

ID00d4 = ("Front Left Wheel Speed",
          "Front Right Wheel Speed",
          "Back Left Wheel Speed",
          "Back Right Wheel Speed",
          "Rear Wheels Speed",
          "Front Wheels Speed",
          "4 Wheel Average Speed")

ID0140 = ("RPM",
          "Clutch Position",
          "Throttle Position (Pedal)",
          "Throttle Position (Drive By Wire)")


ID0141 = ("Engine Load",)

ID0360 = ("Oil Temperature",
          "Coolant Temperature",
          "Cruise Control State",
          "Cruise Control Speed")

ID0361 = ("Gear Indicator",)

# IDs = {
#     "ID 00d0": ("Steering Angle", "Latitudinal Acceleration", "Longitudinal Acceleration", "Combined Acceleration"),
#     "ID 00d1": ("OverAll Speed", "Brake Pressure"),
#     "ID 00d3": ("Traction Control State",),
#     "ID 00d4": ("Front Left Wheel Speed", "Front Right Wheel Speed", "Back Left Wheel Speed", "Back Right Wheel Speed", "Rear Wheels Speed", "Front Wheels Speed", "4 Wheel Average Speed"),
#     "ID 0140": ("RPM", "Clutch Position", "Throttle Position (Pedal)", "Throttle Position (Drive By Wire)"),
#     "ID 0141": ("Engine Load",),
#     "ID 0360": ("Oil Temperature", "Coolant Temperature", "Cruise Control State", "Cruise Control Speed"),
#     "ID 0361": ("Gear Indicator",)
# }
#
# count = 0

########################################################################################################################
# Deleting The Temporary file at the beginning of every run
########################################################################################################################

for filename in os.listdir(temp_dir):
    try:
        if os.path.isfile(temp_path) or os.path.islink(temp_path):
            os.unlink(temp_path)
            Path(temp_path).mkdir(parents=True, exist_ok=True)
        elif os.path.isdir(temp_path):
            shutil.rmtree(temp_path)
            Path(temp_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (temp_path, e))

########################################################################################################################
# Main Function
########################################################################################################################

class MainWidget(QMainWindow):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.activateWindow()
        self.raise_()
        self.setupGraph()

        self.dockcheck = 0
        self.graphcheck = 0

        self.setWindowTitle("Drag and Drop Test")
        self.resize(1200, 800)

        self.setAcceptDrops(True)

        # apply_stylesheet(self, theme='dark_cyan.xml')

        # self.showMaximized()

        self.LBLDragAndDrop = QLabel("Drag And Drop Files Here")
        self.LBLDragAndDrop.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        if self.graphcheck == 0:
            self.setCentralWidget(self.LBLDragAndDrop)

        self.treeview = QTreeView()
        self.treeview.setAnimated(True)

        print(temp_path)

        self.fileModel = QFileSystemModel()

        file_exists = os.path.exists(temp_path)
        print(file_exists)

        self.fileModel.setRootPath(temp_path)
        self.indexRoot = self.fileModel.setRootPath(temp_path)
        self.treeview.setModel(self.fileModel)
        self.treeview.setRootIndex(self.fileModel.index(temp_path))
        self.treeview.setColumnWidth(0, 250)

        self.treeview.doubleClicked.connect(self.onSelectionChanged)

        self.BtnCreateGraph = QPushButton('Create Graph')

        self.BtnCreateGraph.clicked.connect(self.BtnCreateGraph_clicked)

        #self.treeview.doubleClicked.connect(self.openDialog)

        ################################################################################################################
        # Events
        ################################################################################################################

        # self.BTNCreateGraph.clicked.connect(self.createGraph)

        # self.BTNCancel.clicked.connect(self.close)

    ####################################################################################################################
    # Drag And Drop Coding
    ####################################################################################################################

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                filename = os.path.basename(path)
                dest_path = os.path.join(self.fileModel.rootPath(), filename)
                QFile.copy(path, dest_path)
            elif os.path.isdir(path):
                dirname = os.path.basename(path)
                dest_path = os.path.join(self.fileModel.rootPath(), dirname)
                shutil.copytree(path, dest_path)

        if self.dockcheck == 0:
            self.setupTreeView()

    def setupTreeView(self):
        # self.groupboxDock = QtWidgets.QGroupBox("Size Changer")
        self.docklayoutH1 = QHBoxLayout()
        self.docklayoutH2 = QHBoxLayout()
        self.docklayoutV1 = QVBoxLayout()
        self.docklayoutV2 = QVBoxLayout()
        self.docklayoutTotal = QVBoxLayout()

        self.testbutton = QPushButton("Save")
        self.testbutton2 = QPushButton("Cancel")
        self.SizeSlider = QSlider(Qt.Horizontal)
        self.lcdSize = QLCDNumber(self)

        self.mywid = QWidget()
        # self.docklayoutH1.addWidget(self.SizeSlider)
        # self.docklayoutH1.addWidget(self.lcdSize)
        self.docklayoutH1.addWidget(self.BtnCreateGraph)
        self.docklayoutH2.addWidget(self.testbutton)
        self.docklayoutH2.addWidget(self.testbutton2)

        self.docklayoutV1.addLayout(self.docklayoutH1)
        # self.groupboxDock.setLayout(self.docklayoutV1)
        # self.groupboxDock.setMaximumHeight(100)
        # self.docklayoutV2.addWidget(self.groupboxDock)

        self.docklayoutV2.addWidget(self.treeview)
        self.docklayoutV2.addLayout(self.docklayoutH2)

        self.docklayoutTotal.addLayout(self.docklayoutV1)
        self.docklayoutTotal.addLayout(self.docklayoutV2)

        # self.mywid.setLayout(self.docklayoutV2)
        self.mywid.setLayout(self.docklayoutTotal)

        self.dock = QDockWidget("Dockable", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.dock.setWidget(self.mywid)

        # self.dock.setWidget(self.treeview)
        self.dock.setFloating(False)
        self.dockcheck == 1

    ####################################################################################################################
    # Create Graph Button Clicked
    ####################################################################################################################

    def BtnCreateGraph_clicked(self):
        self.createGraphCheck = 1
        self.editDialog = CreateGraph()
        self.editDialog.signEmit.connect(self.createGraph)
        self.editDialog.signEmitClose.connect(self.close)
        self.editDialog.exec_()

    ####################################################################################################################
    # Double Clicked QDialog Box Selection
    ####################################################################################################################

    def onSelectionChanged(self, index):
        self.selectionPath = self.sender().model().filePath(index)

        self.selectionFilename = (self.selectionPath.split("/")[-1])

        self.createGraphCheck = 0

        id_dialog_map = {
            "ID 00d0": Dialog00d0,
            "ID 00d1": Dialog00d1,
            "ID 00d3": Dialog00d3,
            "ID 00d4": Dialog00d4,
            "ID 0140": Dialog0140,
            "ID 0141": Dialog0141,
            "ID 0360": Dialog0360,
            "ID 0361": Dialog0361
        }

        # Get the dialog class based on the selected filename
        dialog_class = id_dialog_map.get(self.selectionFilename)

        # If a valid dialog class was found, create and execute the dialog
        if dialog_class:
            self.editDialog = dialog_class()
            self.editDialog.signEmit.connect(self.createGraph)
            self.editDialog.signEmitClose.connect(self.close)
            self.editDialog.exec_()

    ####################################################################################################################
    # Creating Graphs
    ####################################################################################################################

    def createGraph(self, value, selection, path):
        self.graphcheck = 1

        if self.graphcheck == 1:
            self.setCentralWidget(self.scroll_area)

        ################################################################################################################
        # Checks which dialog box is creating the graph
        ################################################################################################################

        if self.createGraphCheck == 1:
            self.selectionPath = path
            self.selectionFilename = selection
            self.createGraphCheck = 0
        else:
            self.selectionPath = self.selectionPath
            self.selectionFilename = self.selectionFilename

        ################################################################################################################
        # ID 00D0 Creating Graph
        ################################################################################################################

        if self.selectionFilename == "ID 00d0":
            self.df00d0 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df00d0.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
            self.df00d0.dropna(inplace=True)

            self.SA = np.array([], dtype=float)
            self.LatAcc = np.array([], dtype=float)
            self.LonAcc = np.array([], dtype=float)
            self.ComAcc = np.array([], dtype=float)
            self.Time00d0 = np.array([], dtype=float)
            self.Timestamp00d0 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df00d0['Timestamp']:
                self.Time00d0 = np.append(self.Time00d0,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp00d0 = np.append(self.Timestamp00d0, float(item))

            ############################################################################################################
            # Steering Angle Graph
            ############################################################################################################

            if value == "Steering Angle":

                SA_ = (((self.df00d0['B1']) + (self.df00d0['B0'])).apply(int, base=16) * 0.1)

                for item in SA_:
                    if item > 6000:
                        self.SA = np.append(self.SA, round((item - 6553.6), 1))
                    else:
                        self.SA = np.append(self.SA, round(item))

                self.y_axislabel = (value + " (Degree)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.SA

            ############################################################################################################
            # Latitudinal Acceleration Graph
            ############################################################################################################

            elif value == "Latitudinal Acceleration":

                LA_ = ((self.df00d0['B6']).apply(int, base=16)) * 0.2

                for item in LA_:
                    if item > 25:
                        self.LatAcc = np.append(self.LatAcc, item - 51)
                    else:
                        self.LatAcc = np.append(self.LatAcc, item)

                self.y_axislabel = (value + " (G)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.LatAcc

            ############################################################################################################
            # Longitudinal Acceleration Graph
            ############################################################################################################

            elif value == "Longitudinal Acceleration":

                LO_ = ((self.df00d0['B7']).apply(int, base=16)) * 0.02 # 0.1 usually
                print(LO_)

                for item in LO_:
                    if item > 2.55: # 12.75
                        self.LonAcc = np.append(self.LonAcc, item - 5.1) # 25.5
                    else:
                        self.LonAcc = np.append(self.LonAcc, item)

                self.y_axislabel = (value + " (G)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.LonAcc

            ############################################################################################################
            # Combined Acceleration Graph
            ############################################################################################################

            elif value == "Combined Acceleration":

                LA_ = ((self.df00d0['B6']).apply(int, base=16)) * 0.2

                for item in LA_:
                    if item > 25:
                        self.LatAcc = np.append(self.LatAcc, item - 51)
                    else:
                        self.LatAcc = np.append(self.LatAcc, item)

                LO_ = ((self.df00d0['B7']).apply(int, base=16)) * 0.1

                for item in LO_:
                    if item > 12.75:
                        self.LonAcc = np.append(self.LonAcc, item - 25.5)
                    else:
                        self.LonAcc = np.append(self.LonAcc, item)

                self.ComAcc = np.append(self.ComAcc, math.sqrt(self.LatAcc ** 2 + self.LonAcc ** 2))

                self.y_axislabel = (value + " (G)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.ComAcc

            self.plot(x=self.Timestamp00d0, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 00D1 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 00d1":
            self.df00d1 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df00d1.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3"]
            self.df00d1.dropna(inplace=True)

            self.Speed = np.array([], dtype=float)
            self.BP = np.array([], dtype=float)
            self.Time00d1 = np.array([], dtype=float)
            self.Timestamp00d1 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df00d1['Timestamp']:
                self.Time00d1 = np.append(self.Time00d1,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp00d1 = np.append(self.Timestamp00d1, float(item))

            ############################################################################################################
            # Speed Graph
            ############################################################################################################

            if value == "OverAll Speed":

                self.Speed = np.append(self.Speed, round(
                    ((self.df00d1['B1'] + self.df00d1['B0']).apply(int, base=16) * 0.015694 * 4), 1))

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.Speed

            ############################################################################################################
            # Brake Pressure Graph
            ############################################################################################################

            elif value == "Brake Pressure":
                self.BP = (self.df00d1['B2'].apply(int, base=16) / 77) * 100

                self.y_axislabel = (value + " (%)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.BP

            self.plot(x=self.Timestamp00d1, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 00D3 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 00d3":
            self.df00d3 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df00d3.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6"]
            self.df00d3.dropna(inplace=True)

            self.TRC = np.array([], dtype=float)
            self.Time00d3 = np.array([], dtype=float)
            self.Timestamp00d3 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df00d3['Timestamp']:
                self.Time00d3 = np.append(self.Time00d3,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp00d3 = np.append(self.Timestamp00d3, float(item))

            ############################################################################################################
            # Traction Control Graph
            ############################################################################################################

            if value == "Traction Control State":
                TRC = (self.df00d3['B0'] + self.df00d3['B1']).apply(int, base=16)

                for item in TRC:
                    if item == 2062:
                        self.TRC = np.append(self.TRC, 1)
                        self.legendValue = ("Sport Mode Engaged")

                    elif item == 10254:
                        self.TRC = np.append(self.TRC, 2)
                        self.legendValue = ("Sport Mode Engaged and Traction Control Off")

                    elif item == 2006:
                        self.TRC = np.append(self.TRC, 3)
                        self.legendValue = ("Drag Mode Engaged")

                    elif item == 8206:
                        self.TRC = np.append(self.TRC, 4)
                        self.legendValue = ("Drift Mode Engaged")

                    elif item == 6:
                        self.TRC = np.append(self.TRC, 0)
                        self.legendValue = ("Traction Control On")

                self.y_axislabel = (value + " (Mode)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.TRC

            self.plot(x=self.Timestamp00d3, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 00D4 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 00d4":
            self.df00d4 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df00d4.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
            self.df00d4.dropna(inplace=True)

            self.FL = np.array([], dtype=float)
            self.FR = np.array([], dtype=float)
            self.BL = np.array([], dtype=float)
            self.BR = np.array([], dtype=float)
            self.FW = np.array([], dtype=float)
            self.RW = np.array([], dtype=float)
            self.AllAvg = np.array([], dtype=float)
            self.Time00d4 = np.array([], dtype=float)
            self.Timestamp00d4 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df00d4['Timestamp']:
                self.Time00d4 = np.append(self.Time00d4,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp00d4 = np.append(self.Timestamp00d4, float(item))

            ############################################################################################################
            # Front Left Wheel Speed Graph
            ############################################################################################################

            if value == "Front Left Wheel Speed":
                self.FL = np.append(self.FL, ((self.df00d4['B1'] + self.df00d4['B0']).apply(int, base=16)) * 0.05747)

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.FL

            ############################################################################################################
            # Front Right Wheel Speed Graph
            ############################################################################################################

            elif value == "Front Right Wheel Speed":

                self.FR = np.append(self.FR, ((self.df00d4['B3'] + self.df00d4['B2']).apply(int, base=16)) * 0.05747)

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.FR

            ############################################################################################################
            # Back Left Wheel Speed Graph
            ############################################################################################################

            elif value == "Back Left Wheel Speed":
                self.BL = np.append(self.BL, ((self.df00d4['B5'] + self.df00d4['B4']).apply(int, base=16)) * 0.05747)

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.BL

            ############################################################################################################
            # Back Right Wheel Speed Graph
            ############################################################################################################

            elif value == "Back Right Wheel Speed":
                self.BR = np.append(self.BR, ((self.df00d4['B7'] + self.df00d4['B6']).apply(int, base=16)) * 0.05747)

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.BR

            ############################################################################################################
            # Back Wheel Speed Graph
            ############################################################################################################

            elif value == "Rear Wheels Speed":
                self.BL = np.append(self.BL, ((self.df00d4['B5'] + self.df00d4['B4']).apply(int, base=16)) * 0.05747)
                self.BR = np.append(self.BR, ((self.df00d4['B7'] + self.df00d4['B6']).apply(int, base=16)) * 0.05747)
                self.RW = np.append(self.RW, round(((self.BL + self.BR) / 2), 1))

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.RW

            ############################################################################################################
            # Front Wheel Speed Graph
            ############################################################################################################

            elif value == "Front Wheels Speed":
                self.FL = np.append(self.FL, ((self.df00d4['B1'] + self.df00d4['B0']).apply(int, base=16)) * 0.05747)
                self.FR = np.append(self.FR, ((self.df00d4['B3'] + self.df00d4['B2']).apply(int, base=16)) * 0.05747)
                self.FW = np.append(self.FW, round(((self.FL + self.FR) / 2), 1))

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.FW

            ############################################################################################################
            # Average Of All Wheel Speeds Graph
            ############################################################################################################

            elif value == "4 Wheel Average Speed":
                self.FL = np.append(self.FL, ((self.df00d4['B1'] + self.df00d4['B0']).apply(int, base=16)) * 0.05747)
                self.FR = np.append(self.FR, ((self.df00d4['B3'] + self.df00d4['B2']).apply(int, base=16)) * 0.05747)
                self.BL = np.append(self.BL, ((self.df00d4['B5'] + self.df00d4['B4']).apply(int, base=16)) * 0.05747)
                self.BR = np.append(self.BR, ((self.df00d4['B7'] + self.df00d4['B6']).apply(int, base=16)) * 0.05747)
                self.Avg = (((self.FL + self.FR + self.BL + self.BR) / 4))
                self.AllAvg = np.append(self.AllAvg, self.Avg)

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.AllAvg

            self.plot(x=self.Timestamp00d4, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 0140 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 0140":
            self.df0140 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df0140.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
            self.df0140.dropna(inplace=True)

            self.RPM = np.array([], dtype=float)
            self.CP = np.array([], dtype=float)
            self.TP = np.array([], dtype=float)
            self.TPD = np.array([], dtype=float)
            self.Time0140 = np.array([], dtype=float)
            self.Timestamp0140 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df0140['Timestamp']:
                self.Time0140 = np.append(self.Time0140,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp0140 = np.append(self.Timestamp0140, float(item))

            ############################################################################################################
            # RPM Graph
            ############################################################################################################

            if value == "RPM":
                rpm2 = self.df0140['B3'].apply(int, base=16).apply(bin).str[2:].str[-5:].apply(int, base=2)
                rpm1 = self.df0140['B2'].apply(int, base=16)

                self.RPM = np.append(self.RPM, (rpm2 * 256 + rpm1))

                self.y_axislabel = (value + " (RPM)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.RPM

            ############################################################################################################
            # Clutch Position Graph
            ############################################################################################################

            elif value == "Clutch Position":
                CP = self.df0140['B1'].apply(int, base=16)

                for item in CP:
                    if item >= 128 and item <= 143:
                        self.CP = np.append(self.CP, ("Clutch is engaged"))
                    else:
                        self.CP = np.append(self.CP, ("Clutch is disengaged"))

                self.y_axislabel = (value + " (On/Off)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.CP

            ############################################################################################################
            # Throttle Position (Pedal) Graph
            ############################################################################################################

            elif value == "Throttle Position (Pedal)":
                self.TP = np.append(self.TP, round((((self.df0140['B0'].apply(int, base=16)) / 256) * 100) * 0.392157))

                self.y_axislabel = (value + " (%)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.TP

            ############################################################################################################
            # Throttle Position (Drive By Wire) Graph
            ############################################################################################################

            elif value == "Throttle Position (Drive By Wire)":
                self.TPD = np.append(self.TPD,
                                     round((((self.df0140['B4'].apply(int, base=16)) / 256) * 100) * 0.392157))

                self.y_axislabel = (value + " (%)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.TPD

            self.plot(x=self.Timestamp0140, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 0141 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 0141":
            self.df0141 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df0141.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
            self.df0141.dropna(inplace=True)

            self.EL = np.array([], dtype=float)
            self.Time0141 = np.array([], dtype=float)
            self.Timestamp0141 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df0141['Timestamp']:
                self.Time0141 = np.append(self.Time0141,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp0141 = np.append(self.Timestamp0141, float(item))

            ############################################################################################################
            # Engine Load Graph
            ############################################################################################################

            if value == "Engine Load":
                self.EL = np.append(self.EL, (self.df0141['B3'] + self.df0141['B2']).apply(int, base=16))

                self.y_axislabel = (value + " (I have no clue what this value is)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.EL

            self.plot(x=self.Timestamp0141, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 0360 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 0360":
            self.df0360 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df0360.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
            self.df0360.dropna(inplace=True)

            self.TO = np.array([], dtype=float)
            self.TC = np.array([], dtype=float)
            self.CCState = np.array([], dtype=float)
            self.CCSpeed = np.array([], dtype=float)
            self.Time0360 = np.array([], dtype=float)
            self.Timestamp0360 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df0360['Timestamp']:
                self.Time0360 = np.append(self.Time0360,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp0360 = np.append(self.Timestamp0360, float(item))

            ############################################################################################################
            # Oil Temperature Graph
            ############################################################################################################

            if value == "Oil Temperature":
                self.TO = np.append(self.TO, (self.df0360['B2'].apply(int, base=16) - 40))

                self.y_axislabel = (value + " (Degree C)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.TO

            ############################################################################################################
            # Coolant Temperature Graph
            ############################################################################################################

            elif value == "Coolant Temperature":
                self.TC = np.append(self.TC, (self.df0360['B3'].apply(int, base=16) - 40))

                self.y_axislabel = (value + " (Degree C)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.TC

            ############################################################################################################
            # Cruise Control State Graph
            ############################################################################################################

            elif value == "Cruise Control State":
                CC = self.df0360['B5'].apply(int, base=16)

                for item in CC:
                    if item == 16:
                        self.CCState = np.append(self.CCState, ("Cruise Control Engaged"))
                    else:
                        self.CCState = np.append(self.CCState, ("Cruise Control Engaged"))

                self.y_axislabel = (value + " (On/Off)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.CCState

            ############################################################################################################
            # Cruise Control Speed Graph
            ############################################################################################################

            elif value == "Cruise Control Speed":
                self.CCSpeed = np.append(self.CCState, (self.df0360['B6'] + self.df0360['B7']))

                self.y_axislabel = (value + " (Kph)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.CCSpeed

            self.plot(x=self.Timestamp0360, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

        ################################################################################################################
        # ID 0361 Creating Graph
        ################################################################################################################

        elif self.selectionFilename == "ID 0361":
            self.df0361 = pd.read_table(self.selectionPath, header=None, delim_whitespace=True, dtype=object)
            self.df0361.columns = ['Timestamp', 'ID', "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]
            self.df0361.dropna(inplace=True)

            self.GI = np.array([], dtype=float)
            self.Time0361 = np.array([], dtype=float)
            self.Timestamp0361 = np.array([], dtype=float)

            ############################################################################################################
            # Getting Time Stamps
            ############################################################################################################

            for item in self.df0361['Timestamp']:
                self.Time0361 = np.append(self.Time0361,
                                          datetime.fromtimestamp(float(item)).strftime("%H:%M:%S.%f")[:-4])
                self.Timestamp0361 = np.append(self.Timestamp0361, float(item))

            ############################################################################################################
            # Gear Indicator Graph
            ############################################################################################################

            if value == "Gear Indicator":
                self.GI = np.append(self.GI, (self.df0361['B0'].apply(int, base=16)))

                self.y_axislabel = (value + " (Gear)")
                self.x_axislabel = ("Timestamp (24h)")

                self.y_value = self.GI

            self.plot(x=self.Timestamp0361, y=self.y_value, y_axis=self.y_axislabel, x_axis=self.x_axislabel)

    ####################################################################################################################
    # Functions
    ####################################################################################################################

    def close(self):
        self.editDialog.close()

    def setupGraph(self):
        self.scroll_area = QScrollArea()
        self.scroll_container = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_container)
        self.scroll_layout = QVBoxLayout(self.scroll_container)

        hlay = QHBoxLayout()

        hlay.addWidget(self.scroll_area)
        #hlay.addWidget(QPushButton("HEHEHE"))

        self.groupbox = QGroupBox()
        self.groupbox.setLayout(hlay)

    def plot(self, x, y, y_axis, x_axis):

        stringaxis = TimeAxisItem(orientation='bottom')
        self.graph = pg.PlotWidget(axisItems={'bottom': stringaxis})

        self.graph.plot(x, y, symbol=None)
        self.graph.showGrid(x=True, y=True)
        self.graph.setLabel('left', "{}".format(y_axis))
        self.graph.setLabel('bottom', "{}".format(x_axis))

        self.DeleteButton = QPushButton("Delete Graph")
        self.container = QWidget()
        self.vlayGraph = QVBoxLayout(self.container)
        self.hlayGraph = QHBoxLayout()
        self.hlayGraph.addWidget(self.DeleteButton)
        self.hlayGraph.addWidget(self.graph)
        self.vlayGraph.addLayout(self.hlayGraph)
        #vlay.addWidget(graph)


        self.scroll_layout.addWidget(self.container)
        self.container.setMinimumWidth(1024)
        # container.setMaximumWidth(10000)
        self.container.setMinimumHeight(400)

        self.DeleteButton.clicked.connect(self.DeleteGraph)#self.scroll_layout))

    def DeleteGraph(self):
        # print(self.vlayGraph.count())
        # print(self.scroll_layout.count())
        for i in reversed(range(self.scroll_layout.count())):
            print(i)
            #self.scroll_layout.itemAt(i).widget().deleteLater()
        #     if layout_item.layout() == box:
        #         deleteItemsOfLayout(layout_item.layout())
        #         self.vlayGraph.removeItem(layout_item)
        #         break
        # self.vlayGraph.
        # self.hlayGraph.removeWidget(self.graph)

########################################################################################################################
# End of Main Class
########################################################################################################################

class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime("%H:%M:%S.%f")[:-3] for value in values]


########################################################################################################################
# Create Graph Dialog Box
########################################################################################################################

class CreateGraph(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.resize(700, 500)

        self.layout = QVBoxLayout()
        self.hlay = QHBoxLayout()
        self.hlay1 = QHBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Create Graph")

        self.label = QLabel("Data Type")
        #self.label.setMaximumHeight(20)
        self.labelError = QLabel()
        self.labelError.hide()
        self.labelError.setText("Invalid File Format")

        self.treeview = QTreeView()
        self.treeview.setAnimated(True)

        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(temp_path)
        self.indexRoot = self.fileModel.index(self.fileModel.rootPath())

        self.treeview.setModel(self.fileModel)
        self.treeview.setRootIndex(self.fileModel.index(temp_path))
        self.treeview.setColumnWidth(0, 250)
        #self.treeview.setMaximumHeight(300)


       # self.treeview.doubleClicked.connect(self.onSelectionChanged)

        self.comboboxGraphing = QComboBox()

        self.CBCombineGraph = QCheckBox()

        self.lblCombineGraph = QLabel("Combine Data")

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        self.hlay.addWidget(self.BTNCreateGraph)
        self.hlay.addWidget(self.BTNCancel)

        self.hlay1.addWidget(self.comboboxGraphing, 70)
        self.hlay1.addWidget(self.lblCombineGraph,25)
        self.hlay1.addWidget(self.CBCombineGraph,5)

        self.editline = QLineEdit()
        self.editline.textChanged.connect(self.textchanged)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.treeview)
        self.layout.addWidget(self.editline)
        self.layout.addWidget(self.labelError)
        #self.layout.addWidget(self.comboboxGraphing)

        self.layout.addLayout(self.hlay1)
        self.layout.addLayout(self.hlay)


        self.comboboxGraphing.hide()

        self.treeview.clicked.connect(self.treeClicked)

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def treeClicked(self, index):
        self.path = self.sender().model().filePath(index)
        self.editline.setText("{}".format(self.path))

    def textchanged(self, text):
        self.selectionFilename = (text.split("/")[-1])

        filenameslist = next(walk(text), (None, None, []))[2]  # [] if no file

        self.FolderSelected(filenameslist)
        self.FileSelected()

    def FolderSelected(self, filenameslist):
        self.comboboxGraphing.clear()
        for ID in filenameslist:
            if ID in IDList:
                self.comboboxGraphing.show()
                if ID == "ID 00d0":
                    for item in ID00d0:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 00d1":
                    for item in ID00d1:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 00d3":
                    for item in ID00d3:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 00d4":
                    for item in ID00d4:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 0140":
                    for item in ID0140:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 0141":
                    for item in ID0141:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 0360":
                    for item in ID0360:
                        self.comboboxGraphing.addItem(item)

                elif ID == "ID 0361":
                    for item in ID0361:
                        self.comboboxGraphing.addItem(item)

    def FileSelected(self):
        if self.selectionFilename in IDList:
            self.comboboxGraphing.show()
            self.comboboxGraphing.clear()

            if self.selectionFilename == "ID 00d0":
                for item in ID00d0:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 00d1":
                for item in ID00d1:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 00d3":
                for item in ID00d3:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 00d4":
                for item in ID00d4:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 0140":
                for item in ID0140:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 0141":
                for item in ID0141:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 0360":
                for item in ID0360:
                    self.comboboxGraphing.addItem(item)

            elif self.selectionFilename == "ID 0361":
                for item in ID0361:
                    self.comboboxGraphing.addItem(item)

    def BTNCreateGraph_clicked(self):
        if self.comboboxGraphing.currentText() in ID00d0:
            self.IDselection = "ID 00d0"
            if (self.path.split("/")[-1]) != self.IDselection:
                    self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID00d1:
            self.IDselection = "ID 00d1"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID00d3:
            self.IDselection = "ID 00d3"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID00d4:
            self.IDselection = "ID 00d4"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID0140:
            self.IDselection = "ID 0140"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID0141:
            self.IDselection = "ID 0141"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID0360:
            self.IDselection = "ID 0360"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        elif self.comboboxGraphing.currentText() in ID0361:
            self.IDselection = "ID 0361"
            if (self.path.split("/")[-1]) != self.IDselection:
                self.fullPath = self.path + ("/{}".format(self.IDselection))
            else:
                self.fullPath = self.path

        self.signEmit.emit(self.comboboxGraphing.currentText(), self.IDselection, self.fullPath)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 00d0 Dialog Box
########################################################################################################################

class Dialog00d0(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox00d0 = QComboBox()

        for item in ID00d0:
            self.combobox00d0.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        self.layout.addWidget(label)
        self.layout.addWidget(self.combobox00d0)
        self.layout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox00d0.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 00d1 Dialog Box
########################################################################################################################

class Dialog00d1(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox00d1 = QComboBox()

        for item in ID00d1:
            self.combobox00d1.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox00d1)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox00d1.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 00d3 Dialog Box
########################################################################################################################

class Dialog00d3(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox00d3 = QComboBox()

        for item in ID00d3:
            self.combobox00d3.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox00d3)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox00d3.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 00d4 Dialog Box
########################################################################################################################

class Dialog00d4(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox00d4 = QComboBox()

        for item in ID00d4:
            self.combobox00d4.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox00d4)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox00d4.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 0140 Dialog Box
########################################################################################################################

class Dialog0140(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox0140 = QComboBox()

        for item in ID0140:
            self.combobox0140.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox0140)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox0140.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 0141 Dialog Box
########################################################################################################################

class Dialog0141(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox0141 = QComboBox()

        for item in ID0141:
            self.combobox0141.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox0141)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox0141.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 0360 Dialog Box
########################################################################################################################

class Dialog0360(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox0360 = QComboBox()

        for item in ID0360:
            self.combobox0360.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox0360)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox0360.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# ID 0361 Dialog Box
########################################################################################################################

class Dialog0361(QDialog):
    signEmit = QtCore.pyqtSignal(str, str, str)
    signEmitClose = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        mainlayout = QVBoxLayout()
        hlay = QHBoxLayout()
        self.setLayout(mainlayout)

        self.setWindowTitle("Create Graph")

        label = QLabel("Data Type")

        self.combobox0361 = QComboBox()

        for item in ID0361:
            self.combobox0361.addItem(item)

        self.BTNCreateGraph = QPushButton("Create Graph")
        self.BTNCancel = QPushButton("Cancel")

        hlay.addWidget(self.BTNCreateGraph)
        hlay.addWidget(self.BTNCancel)

        mainlayout.addWidget(label)
        mainlayout.addWidget(self.combobox0361)
        mainlayout.addLayout(hlay)

        self.selection = ""
        self.path = ""

        self.BTNCancel.clicked.connect(self.BTNClose_clicked)

        self.BTNCreateGraph.clicked.connect(self.BTNCreateGraph_clicked)

    def BTNCreateGraph_clicked(self):
        self.signEmit.emit(self.combobox0361.currentText(), self.selection, self.path)

    def BTNClose_clicked(self):
        self.signEmitClose.emit(1)


########################################################################################################################
# Pandas Display Data Frame
########################################################################################################################

class pandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


########################################################################################################################
# Run Script
########################################################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWidget()
    ui.show()
    sys.exit(app.exec_())
