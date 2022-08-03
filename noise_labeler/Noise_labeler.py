import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

from scipy import signal
from collections import defaultdict

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas


__appname__ = "Dong's Noise Labeler"

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        self.setWindowTitle(__appname__)
        
        self.setGeometry(50,50,1770,730)


        ''' Widgets '''

        # csv list
        self.csv_list_widget = QListWidget()
        self.currIndex = 0


        # Spectrogram
        self.fig = plt.Figure(figsize = (120, 1000))

        self.Canvas = FigureCanvas(self.fig)
        self.Canvas.move(5, 5)

        self.file_title = QLabel(self)
        self.file_title.move(5,5)
        
        # labels
        self.labels = QTextBrowser(self)
        self.labels.move(5,5)

        ''' Layouts '''
        # Label layout
        self.labelLayout = QHBoxLayout()

        self.split_ratio = 10
        self.label_edits_list = []
        for i in range(self.split_ratio):
            label_edits = QLineEdit(self)
            self.label_edits_list.append(label_edits)           
            self.labelLayout.addWidget(label_edits)

        labelButton = self.initButton(":edit", "Labeling", "enter")
        labelButton.clicked.connect(self.labelingEvent)

        self.labelLayout.addWidget(labelButton)


        # Button layout
        buttonLayout = QHBoxLayout()

        prevButton = self.initButton(":start", "prevButton", "B")
        nextButton = self.initButton(":next", "nextButton", "N")
        saveButton = self.initButton(":open", "Save File", "S")
        
        buttonLayout.addWidget(prevButton)
        buttonLayout.addWidget(nextButton)
        buttonLayout.addWidget(saveButton)

        prevButton.clicked.connect(self.filePrevEvent)
        nextButton.clicked.connect(self.fileNextEvent)
        saveButton.clicked.connect(self.fileSaveEvent)


        # Left layout
        self.leftLayout = QVBoxLayout()

        self.leftLayout.addWidget(self.file_title)
        self.leftLayout.addLayout(self.labelLayout)
        self.leftLayout.addWidget(self.Canvas)


        # Right layout
        self.rightLayout = QVBoxLayout()

        self.rightLayout.addLayout(buttonLayout, stretch=1)
        self.rightLayout.addWidget(self.labels)
        self.rightLayout.addWidget(self.csv_list_widget)
        

        # Layout
        Layout = QHBoxLayout()

        Layout.addLayout(self.leftLayout)
        Layout.addLayout(self.rightLayout)

        self.setLayout(Layout)


        ''' Functions '''
        self.openDirClicked()


    def initButton(self, icon, name, shortcut):
        Button = QPushButton(self)
        Button.setMaximumHeight(100)
        Button.setText(name)
        Button.setIcon(QIcon(icon))
        Button.setShortcut(shortcut)
        return Button


    def openDirClicked(self):
        self.csv_dir_path = QFileDialog.getExistingDirectory(self, self.tr("Open Raw data files"), "./", QFileDialog.ShowDirsOnly)  # './raw_data'
        self.json_dir_path = QFileDialog.getExistingDirectory(self, self.tr("Open json files"), "./", QFileDialog.ShowDirsOnly)     # './json_data'

        self.csv_list = self.scan_all_items(self.csv_dir_path)
        for csv_path in self.csv_list:
            item = QListWidgetItem(csv_path)
            self.csv_list_widget.addItem(item)

        self.draw_spectrogram(self.csv_list, self.currIndex)


    def scan_all_items(self, folderPath):
        item = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                relative_path = os.path.join(root, file)
                path = str(os.path.abspath(relative_path))
                item.append(path)
        return item


    ## raw file open utils
    def filePrevEvent(self):
        self.imageOpenEvent(-1)

    def fileNextEvent(self):
        self.imageOpenEvent(1)

    def imageOpenEvent(self, index):
        self.currIndex = self.currIndex + index

        self.updateCanvas()
        self.draw_spectrogram(self.csv_list, self.currIndex)       

    def updateCanvas(self) :
        self.leftLayout.removeWidget(self.Canvas)
        self.Canvas.close()
        
        self.Canvas = FigureCanvas(self.fig)
        self.leftLayout.addWidget(self.Canvas)


    ## file save utils
    def labelingEvent(self):
        text = ""
        for label in self.label_edits_list:
            text = text + label.text()
        self.labels.setText(text)


    def fileSaveEvent(self):
        
        database = defaultdict(list)

        file_name = self.curr_item_name.split('.')[0]
        exportPath = self.json_dir_path + '/' + file_name + '.json'

        for data, label in zip(self.split_data, self.label_edits_list):
            label = label.text()

            database['data'].append(data.tolist())
            database['label'].append(label)

        with open(exportPath, 'w') as f:
            json.dump(dict(database), f)


    ## draw spectroram on canvas
    def draw_spectrogram(self, item_list, index):

        try:
            self.curr_item = item_list[index]
            self.curr_item_name = self.curr_item.split('/')[-1]
            
            data = np.array(pd.read_csv(self.curr_item))
            
            self.split_data = np.split(data, self.split_ratio, axis = 1)

            self.file_title.setText(self.curr_item_name)
            self.axes = self.Canvas.figure.subplots(1,10)
            for i in range(10):
                self.axes[i].imshow(self.split_data[i], origin="lower", cmap='jet', extent=[0, 200, 0, 1200],  vmin = 60, vmax =120)

        except:
            print('End of the items')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    windowExample = MainWindow()
    windowExample.show()
    sys.exit(app.exec_())
