from __future__ import unicode_literals
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QGridLayout, QSpacerItem
from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QGraphicsView, QGraphicsScene, QSizePolicy
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from Parametry import Parametr, modelComboBox
import math


class main_window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450, 200, 1000, 600)
        self.setWindowTitle("NRange")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.interfejs()
        self.show()

    def interfejs(self):
        layout = QHBoxLayout()
        ### INPUTY PARAMETROW
        fieldsLayout = QGridLayout()     #layout dla prawej części
        rightHlayout = QVBoxLayout()
        itemsLayout = QVBoxLayout()     # g lowny layout

        self.Ptx = Parametr("Ptx", 0, 99, 0)
        self.Gtx = Parametr("Gtx", 0, 99, 0)
        self.Ftx = Parametr("Ftx", 0, 99, 0)
        self.Grx = Parametr("Grx", 0, 99, 0)
        self.Frx = Parametr("Frx", 0, 99, 0)
        self.SNR = Parametr("SNR", 0, 99, 0)
        self.bandwitch = Parametr("B", 0, 99, 0)
        self.Fnoise = Parametr("Fnoise", 0, 99, 0)
        self.Temp = Parametr("Temp [K]", 0, 999, 0)
        self.Freq = Parametr("Freq [MHz]", 1, 99999, 1)
        self.wyborModelu = modelComboBox("Model propagacyjny")

        fieldsLayout.addItem(self.wyborModelu,0,0)
        fieldsLayout.addItem(self.Ptx,1,0)
        fieldsLayout.addItem(self.Gtx,1,1)
        fieldsLayout.addItem(self.Ftx,1,2)
        fieldsLayout.addItem(self.Grx,2,0)
        fieldsLayout.addItem(self.Frx,2,1)
        fieldsLayout.addItem(self.SNR,2,2)
        fieldsLayout.addItem(self.bandwitch,3,0)
        fieldsLayout.addItem(self.Temp,3,1)
        fieldsLayout.addItem(self.Fnoise,3,2)
        fieldsLayout.addItem(self.Freq,4,0)
        fieldsLayout.setSpacing(20)
        #self.scene = QGraphicsScene()
        #scene.addText("ddddddddddddddddddddddddddddddddddddddddddddd")
        #view = QGraphicsView(self.scene)

        # oblcizanie
        calculateButton = QPushButton()
        calculateButton.setText("Oblicz zasięg")
        calculateButton.clicked.connect(lambda x: self.propagationModel())
        fieldsLayout.addWidget(calculateButton, 5, 2)

        layout.addWidget(self.view)
        self.view.show()
        # lewa strona
        #layout.addWidget(paintContainer)
        verticalSpacer = QSpacerItem(1, 50, QSizePolicy.Fixed, QSizePolicy.Expanding)
        fieldsLayout.addItem(verticalSpacer,5,0)
        fieldsLayout.setRowStretch(0, 1)
        fieldsLayout.setRowStretch(1, 1)
        fieldsLayout.setRowStretch(1, 1)

        itemsLayout.addItem(fieldsLayout)
        layout.addItem(itemsLayout)         # główny layout dzieli obszar na dwie czesci
        #self.Ptx = self.Ptx.container.text()
        #self.scene.addText(self.Ptx.container.text())
        self.setLayout(layout)

    def propagationModel(self, name='ddd'):
        # Lmax = Ptx + Gtx - Ftx + Grx - Frx - S/N - k*T*B - Fnoise - IM
        Ptx = self.Ptx.returnParameterValues()
        Gtx = self.Gtx.returnParameterValues()
        Ftx = self.Ftx.returnParameterValues()
        Grx = self.Grx.returnParameterValues()
        Frx = self.Frx.returnParameterValues()
        SNR = self.SNR.returnParameterValues()
        bandwitch = self.bandwitch.returnParameterValues()
        Temp = self.Temp.returnParameterValues()
        Fnoise = self.Fnoise.returnParameterValues()
        Freq = self.Freq.returnParameterValues()
        k = 1.38e-23
        Lmax = Ptx + Gtx - Ftx + Grx - Frx - SNR - k * bandwitch * Temp - Fnoise - 2

        ### obliczanie zasiegu
        fdB = 20 * math.log10(Freq)
        x = Lmax - 32.4 - fdB
        d = 10**(x/20)
        if name.lower() == 'wpp':
            return 0
        self.scene.clear()
        self.scene.addText(str(round(d*1000, 2)))
        # L = 32,4 +20lg f [MHz] + 20lg d [km]
        # 20lg d = L - 32,4 - 20lg f
        # d = 10^(x/20)
        
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = main_window()
    sys.exit(app.exec_())
