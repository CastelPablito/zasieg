from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QGridLayout, QSlider, QComboBox
from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QIntValidator


# from main import main_window

class Parametr(QVBoxLayout):
    # container = QLineEdit()
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
        # container.editingFinished.connect(lambda x: self.setValue(container,x,minimum,maksimum))
        myValidator = QIntValidator(minimum, maksimum, self.container)
        self.container.setValidator(myValidator)
        self.slider.setRange(minimum, maksimum)
        self.slider.setValue(defaultValue)
        # self.container.textChanged.connect(lambda x: self.slider.setValue(int(x)))     # działa ale w pewnym momencie wywala ;/
        self.slider.valueChanged.connect(lambda x: self.container.setText(str(x)))
        # self.container.textChanged.connect(lambda x: main_window.propagationModel())

    def returnParameterValues(self):
        x = self.container.text()
        try:
            a = int(x)
        except:
            print('d')
        return int(self.container.text())


class myLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)


class modelComboBox(QVBoxLayout):
    def __init__(self, info, parent=None):
        super().__init__(parent)
        label = QLabel(info)
        label.setMaximumHeight(15)
        self.addWidget(label)
        self.wybor = QComboBox()
        modele = ["ABG SC", "ABG OS", "CI SC", "CI OS"]
        axis_X = ["CQI", "f [MHz]"]
        if info == "Model propagacyjny":
            self.wybor.addItems(modele)
        elif info == "Oś x":
            self.wybor.addItems(axis_X)
        self.addWidget(self.wybor)
        self.setSpacing(10)


CQI = {'CQI 1': -7.8474,
       'CQI 2': -6.2369,
       'CQI 3': -4.3591,
       'CQI 4': -1.9319,
       'CQI 5': 0.1509,
       'CQI 6': 1.9976,
       'CQI 7': 4.7278,
       'CQI 8': 6.2231,
       'CQI 9': 8.0591,
       'CQI 10': 9.8585,
       'CQI 11': 11.8432,
       'CQI 12': 13.4893,
       'CQI 13': 15.3598,
       'CQI 14': 17.4435,
       'CQI 15': 19.2155,
       }
