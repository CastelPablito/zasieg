from __future__ import unicode_literals
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QGridLayout, QSpacerItem
from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QGraphicsView, \
    QGraphicsScene, QSizePolicy
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5 import QtCore
from Parametry import Parametr, modelComboBox
import math
import matplotlib.pyplot as plt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


class main_window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450, 200, 1100, 550)
        self.setWindowTitle("NRange")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.interfejs()
        self.show()

    def interfejs(self):
        layout = QHBoxLayout()
        ### INPUTY PARAMETROW
        fieldsLayout = QGridLayout()  # layout dla prawej części
        itemsLayout = QVBoxLayout()  # g lowny layout

        self.Ptx = Parametr("Ptx", 0, 99, 0)
        self.Gtx = Parametr("Gtx", 0, 99, 0)
        self.Ftx = Parametr("Ftx", 0, 99, 0)
        self.Grx = Parametr("Grx", 0, 99, 0)
        self.Frx = Parametr("Frx", 0, 99, 0)
        self.SNR = Parametr("SNR", -20, 99, 0)
        self.bandwitch = Parametr("B [MHz]", 0, 99, 0)
        self.Fnoise = Parametr("Fnoise", 0, 99, 0)
        self.Temp = Parametr("Temp [K]", 0, 999, 0)
        self.Freq = Parametr("Freq [MHz]", 1, 99999, 1)
        self.wyborModelu = modelComboBox("Model propagacyjny")

        fieldsLayout.addItem(self.wyborModelu, 0, 0)
        fieldsLayout.addItem(self.Ptx, 1, 0)
        fieldsLayout.addItem(self.Gtx, 1, 1)
        fieldsLayout.addItem(self.Ftx, 1, 2)
        fieldsLayout.addItem(self.Grx, 2, 0)
        fieldsLayout.addItem(self.Frx, 2, 1)
        fieldsLayout.addItem(self.SNR, 2, 2)
        fieldsLayout.addItem(self.bandwitch, 3, 0)
        fieldsLayout.addItem(self.Temp, 3, 1)
        fieldsLayout.addItem(self.Fnoise, 3, 2)
        fieldsLayout.addItem(self.Freq, 4, 0)
        fieldsLayout.setSpacing(20)
        # self.scene = QGraphicsScene()
        # scene.addText("ddddddddddddddddddddddddddddddddddddddddddddd")
        # view = QGraphicsView(self.scene)

        # oblcizanie
        calculateButton = QPushButton()
        calculateButton.setText("Oblicz zasięg")
        calculateButton.clicked.connect(lambda x: self.propagationModel())
        fieldsLayout.addWidget(calculateButton, 5, 2)

        layout.addWidget(self.view)
        self.view.show()
        # lewa strona
        # layout.addWidget(paintContainer)
        verticalSpacer = QSpacerItem(1, 50, QSizePolicy.Fixed, QSizePolicy.Expanding)
        rect = QRect(0,0,100,600)
        fieldsLayout.setAlignment(Qt.AlignRight)
        fieldsLayout.addItem(verticalSpacer, 5, 0)
        fieldsLayout.setRowStretch(0, 1)
        fieldsLayout.setRowStretch(1, 1)
        fieldsLayout.setRowStretch(1, 1)

        itemsLayout.addItem(fieldsLayout)
        layout.addItem(itemsLayout)  # główny layout dzieli obszar na dwie czesci
        # self.Ptx = self.Ptx.container.text()
        # self.scene.addText(self.Ptx.container.text())
        layout.setStretchFactor(self.view, 2)
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

        # Częstoty do rysowania
        Ftab = [x for x in range(100, 100000, 100)]
        FdBtab = [20 * math.log10(x) for x in Ftab]
        # SNR USTAWIONE
        Lmax = Ptx + Gtx - Ftx + Grx - Frx - SNR - k * bandwitch * (10 ** 6) * Temp - Fnoise - 2
        # Lmax dla QPSK
        LmaxQPSK = Ptx + Gtx - Ftx + Grx - Frx - calcLossForMod('QPSK') - k * bandwitch * (10 ** 6) * Temp - Fnoise - 2
        # Lmax dla 16QAM
        Lmax16QAM = Ptx + Gtx - Ftx + Grx - Frx - calcLossForMod('16QAM') - k * bandwitch * (10 ** 6) * Temp - Fnoise - 2
        # Lmax dla 64QAM
        Lmax64QAM = Ptx + Gtx - Ftx + Grx - Frx - calcLossForMod('64QAM') - k * bandwitch * (10 ** 6) * Temp - Fnoise - 2

        # WPP
        # L = 32,4 +20lg f [MHz] + 20lg d [km]
        # 20lg d = L - 32,4 - 20lg f
        # d = 10^(x/20)

        # obliczanie X
        xTabSet = [(Lmax - 32.4 - x) for x in FdBtab]
        xTabQPSK = [(LmaxQPSK - 32.4 - x) for x in FdBtab]
        xTab16QAM = [(Lmax16QAM - 32.4 - x) for x in FdBtab]
        xTab64QAM = [(Lmax64QAM - 32.4 - x) for x in FdBtab]

        # obliczanie odleglości
        Dtab = [(10 ** (x/20)) * 1000 for x in xTabSet]
        DtabQPSK = [(10 ** (x/20)) * 1000 for x in xTabQPSK]
        Dtab16QAM = [(10 ** (x/20)) * 1000 for x in xTab16QAM]
        Dtab64QAM = [(10 ** (x/20)) * 1000 for x in xTab64QAM]

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend(offset=(480,10))

        # self.graphWidget.setXRange(1,10000)
        # self.graphWidget.setYRange(1,10000)
        self.scene.addWidget(self.graphWidget)
        xLabelFreqdB = [10 * math.log10(x) for x in Ftab]
        self.plot(xLabelFreqdB, Dtab, 'Własne SNR', 'k')
        self.plot(xLabelFreqdB, DtabQPSK, 'QPSK', 'r')
        self.plot(xLabelFreqdB, Dtab16QAM, '16QAM', 'g')
        self.plot(xLabelFreqdB, Dtab64QAM, '64QAM', 'b')
        self.graphWidget.setTitle("Zasięg użyteczny [m] w funkcji częstotliwości [MHz]", color='k', size='10pt')
        styles = {'color': 'k', 'font-size': '15px'}
        self.graphWidget.setLabel('left', 'Odległość [m]', **styles)
        self.graphWidget.setLabel('bottom', 'Częstotliwość 10log(f[MHz] / 1 [MHz]', **styles)

        # obliczanie zasiegu
        # fdB = 20 * math.log10(Freq)
        # x = Lmax - 32.4 - fdB
        # d = 10**(x/20)
        # if name.lower() == 'wpp':
        #     return 0
        # self.scene.clear()
        # self.scene.addText(str(round(d*1000, 2)))  # odleglosc w metrach
        # L = 32,4 +20lg f [MHz] + 20lg d [km]
        # 20lg d = L - 32,4 - 20lg f
        # d = 10^(x/20)

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)


def calcLossForMod(mod):
    SNR = 0
    if mod == 'QPSK':   # CQI 1,2,3,4,5,6
        SNR = -8
    elif mod == '16QAM': # CQI 7,8,9
        SNR = 6
    elif mod == "64QAM":    # CQI 10,11,12,13,14,15
        SNR = 15
    else:
        SNR = -20
    return SNR


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = main_window()
    sys.exit(app.exec_())
