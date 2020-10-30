from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QGridLayout, QSlider, QComboBox
from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout,QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QIntValidator
#from main import main_window

class Parametr(QVBoxLayout):
    #container = QLineEdit()
    def __init__(self, info, minimum, maksimum, defaultValue, parent=None):
        super().__init__(parent)
        Hlayout = QHBoxLayout()
        label = QLabel(info)
        self.container = QLineEdit()
        self.container.setText(str(defaultValue))
        self.container.setMaximumWidth(50)
        Hlayout.addWidget(label)
        Hlayout.addWidget(self.container)
        Hlayout.setSpacing(10)
        self.addItem(Hlayout)
        self.slider = QSlider(Qt.Horizontal)
        self.addWidget(self.slider)
        self.setSpacing(10)
        #container.editingFinished.connect(lambda x: self.setValue(container,x,minimum,maksimum))
        myValidator = QIntValidator(minimum, maksimum, self.container)
        self.container.setValidator(myValidator)
        self.slider.setRange(minimum, maksimum)
        #self.container.textChanged.connect(lambda x: self.slider.setValue(int(x)))     # działa ale w pewnym momencie wywala ;/
        self.slider.valueChanged.connect(lambda x: self.container.setText(str(x)))
        #self.container.textChanged.connect(lambda x: main_window.propagationModel())


    def returnParameterValues(self):
        return int(self.container.text())




class myLineEdit(QLineEdit):
    def __init__(self, parent = None):
        super().__init__(parent)



class modelComboBox(QVBoxLayout):
    def __init__(self, info, parent=None):
        super().__init__(parent)
        label = QLabel(info)
        label.setMaximumHeight(15)
        self.addWidget(label)
        wybor = QComboBox()
        modele = ["WPP", "uMi", "uMa"]
        wybor.addItems(modele)
        self.addWidget(wybor)
        self.setSpacing(10)




