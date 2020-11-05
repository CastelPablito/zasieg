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


MAX_FREQ = 6000
MIN_FREQ = 2000


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
        self.Freq = Parametr("Freq [MHz]", MIN_FREQ, MAX_FREQ, MIN_FREQ)
        self.wyborModelu = modelComboBox("Model propagacyjny")
        self.wynikLabel = QLabel()

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
        fieldsLayout.addWidget(self.wynikLabel, 5, 1)
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

    def propagationModel(self):
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
        Ftab = [x for x in range(MIN_FREQ, MAX_FREQ, 100)]
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
        if self.wyborModelu.wybor.currentText() == 'WPP':
            Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.WPPmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, FdBtab)
        elif self.wyborModelu.wybor.currentText() == 'ABG SC':
            Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC')
        elif self.wyborModelu.wybor.currentText() == 'ABG OS':
            Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS')
        elif self.wyborModelu.wybor.currentText() == 'CI SC':
            Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC')
        elif self.wyborModelu.wybor.currentText() == 'CI OS':
            Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS')
        elif self.wyborModelu.wybor.currentText() == 'WINNER II LOS':
            Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM= self.WINNERIIB1model(Ftab, Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM)
        else:
            self.scene.clear()

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend(offset=(480, 10))

        # self.graphWidget.setXRange(1,10000)
        # self.graphWidget.setYRange(1,10000)
        self.scene.addWidget(self.graphWidget)
        #xLabelFreqdB = [10 * math.log10(x) for x in Ftab]
        xLabelFreqdB = Ftab
        self.plot(xLabelFreqdB, Dtab, 'Własne SNR', 'k')
        self.plot(xLabelFreqdB, DtabQPSK, 'QPSK', 'r')
        self.plot(xLabelFreqdB, Dtab16QAM, '16QAM', 'g')
        self.plot(xLabelFreqdB, Dtab64QAM, '64QAM', 'b')
        self.graphWidget.setTitle("Zasięg użyteczny [m] w funkcji częstotliwości [MHz]", color='k', size='10pt')
        styles = {'color': 'k', 'font-size': '15px'}
        self.graphWidget.setLabel('left', 'Odległość [m]', **styles)
        self.graphWidget.setLabel('bottom', 'Częstotliwość f[MHz]', **styles)

        # obliczanie zasiegu
        if self.wyborModelu.wybor.currentText() == 'WPP':
            self.calcRange(Freq, "WPP", Lmax)
        elif self.wyborModelu.wybor.currentText() == 'ABG SC':
            self.calcRange(Freq, "ABG SC", Lmax)
        elif self.wyborModelu.wybor.currentText() == 'ABG OS':
            self.calcRange(Freq, "ABG OS", Lmax)
        elif self.wyborModelu.wybor.currentText() == 'CI SC':
            self.calcRange(Freq, "CI SC", Lmax)
        elif self.wyborModelu.wybor.currentText() == 'CI OS':
            self.calcRange(Freq, "CI OS", Lmax)
        elif self.wyborModelu.wybor.currentText() == 'WINNER II LOS':
            self.calcRange(Freq, "WINNER II LOS", Lmax)

        # self.scene.clear()
        # self.scene.addText(str(round(d*1000, 2)))  # odleglosc w metrach
        # L = 32,4 +20lg f [MHz] + 20lg d [km]
        # 20lg d = L - 32,4 - 20lg f
        # d = 10^(x/20)

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def WPPmodel(self, Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, FdBtab):
        # obliczanie X
        xTabSet = [(Lmax - 32.4 - x) for x in FdBtab]
        xTabQPSK = [(LmaxQPSK - 32.4 - x) for x in FdBtab]
        xTab16QAM = [(Lmax16QAM - 32.4 - x) for x in FdBtab]
        xTab64QAM = [(Lmax64QAM - 32.4 - x) for x in FdBtab]

        # obliczanie odleglości
        Dtab = [(10 ** (x / 20)) * 1000 for x in xTabSet]
        DtabQPSK = [(10 ** (x / 20)) * 1000 for x in xTabQPSK]
        Dtab16QAM = [(10 ** (x / 20)) * 1000 for x in xTab16QAM]
        Dtab64QAM = [(10 ** (x / 20)) * 1000 for x in xTab64QAM]

        return Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM

    def ABGmodel(self, Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, FdBtab, type):
        # obliczanie X
        alfa = 2
        beta = 31.4
        gamma = 2.1
        idk = 0

        if type == 'SC':
            alfa = 3.5
            beta = 24.4
            gamma = 1.9
            idk = 0
        elif type == 'OS':
            alfa = 4.4
            beta = 2.4
            gamma = 1.9
            idk = 0

        xTabSet = [(Lmax - beta - 10 * gamma * math.log10(x / 1000) - idk) for x in FdBtab]
        xTabQPSK = [(LmaxQPSK - beta - 10 * gamma * math.log10(x / 1000) - idk) for x in FdBtab]
        xTab16QAM = [(Lmax16QAM - beta - 10 * gamma * math.log10(x / 1000) - idk) for x in FdBtab]
        xTab64QAM = [(Lmax64QAM - beta - 10 * gamma * math.log10(x / 1000) - idk) for x in FdBtab]

        # obliczanie odleglości
        Dtab = [(10 ** (x / (10 * alfa))) for x in xTabSet]
        DtabQPSK = [(10 ** (x / (10 * alfa))) for x in xTabQPSK]
        Dtab16QAM = [(10 ** (x / (10 * alfa))) for x in xTab16QAM]
        Dtab64QAM = [(10 ** (x / (10 * alfa))) for x in xTab64QAM]
        return Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM

    def CImodel(self, Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, FdBtab, type):
        # obliczanie X
        n = 1
        idk = 0
        if type == 'SC':
            n = 3.1
        elif type == 'OS':
            n = 2.8

        xTabSet = [(Lmax - 20 * math.log10(4 * math.pi * x * 10 ** 6 / (3 * 10 ** 8)) - idk) for x in FdBtab]
        xTabQPSK = [(LmaxQPSK - 20 * math.log10(4 * math.pi * x * 10 ** 6 / (3 * 10 ** 8)) - idk) for x in FdBtab]
        xTab16QAM = [(Lmax16QAM - 20 * math.log10(4 * math.pi * x * 10 ** 6 / (3 * 10 ** 8)) - idk) for x in FdBtab]
        xTab64QAM = [(Lmax64QAM - 20 * math.log10(4 * math.pi * x * 10 ** 6 / (3 * 10 ** 8)) - idk) for x in FdBtab]

        # obliczanie odleglości
        Dtab = [(10 ** (x / (10 * n))) for x in xTabSet]
        DtabQPSK = [(10 ** (x / (10 * n))) for x in xTabQPSK]
        Dtab16QAM = [(10 ** (x / (10 * n))) for x in xTab16QAM]
        Dtab64QAM = [(10 ** (x / (10 * n))) for x in xTab64QAM]
        return Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM

    def WINNERIIB1model(self, Ftab, Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM):
        # LOS
        # 10m < d1 < dbp, sigma = 3
        # L = 22,7 * log10(d[m]) + 41 + 20 * log10((fc[GHz]/5)) + X
        # d = 10^(L - 41 - 20*log10(fc/5))/22.7
        # dbp < d1 < 5km
        # hbs = 10m, hms = 1,5m
        # L = 40 * log10(d1) + 9,45 -17,3 * log10(hbs + hms) + 2,7 * log10(fc/5)
        # d = 10**((L - 9.45 + 17.3 * log10(hbs + hms) - 2.7 * log10(fc/5))/40
        # dbp = 4 * (hbs - 1)(hms -1) * fc/c,, c = 3*10**8
        hbs = 10
        hms = 1.5
        c = 3e8
        dbpTab = [4 * (hbs - 1) * (hms - 1) * x*10**6/c for x in Ftab]
        dTab = []
        dQPSKTab = []
        d16QAMTab = []
        d64QAMTab = []
        for i, freq in enumerate(Ftab):
            # L = 22,7 * log10(d[m]) + 41 + 20 * log10((fc[GHz]/5)) + X
            d = 10**((Lmax - 41 - 20 * math.log10(freq/5000))/22.7)
            dQPSK = 10**((LmaxQPSK - 41 - 20 * math.log10(freq/5000))/22.7)
            d16QAM = 10**((Lmax16QAM - 41 - 20 * math.log10(freq/5000))/22.7)
            d64QAM = 10**((Lmax64QAM - 41 - 20 * math.log10(freq/5000))/22.7)
            # L = 40 * log10(d1) + 9,45 -17,3 * log10(hbs + hms) + 2,7 * log10(fc/5)
            if d > dbpTab[i]:
                d = 10 ** ((Lmax - 9.45 + 17.3 * math.log10(hbs + hms) - 2.7 * math.log10(freq / 5000)) / 40)

            if dQPSK > dbpTab[i]:
                dQPSK = 10 ** ((LmaxQPSK - 9.45 + 17.3 * math.log10(hbs + hms) - 2.7 * math.log10(freq / 5000)) / 40)

            if d16QAM > dbpTab[i]:
                d16QAM = 10 ** ((Lmax16QAM - 9.45 + 17.3 * math.log10(hbs + hms) - 2.7 * math.log10(freq / 5000)) / 40)

            if d64QAM > dbpTab[i]:
                d64QAM = 10 ** ((Lmax64QAM - 9.45 + 17.3 * math.log10(hbs + hms) - 2.7 * math.log10(freq / 5000)) / 40)

            dTab.append(d)
            dQPSKTab.append(dQPSK)
            d16QAMTab.append(d16QAM)
            d64QAMTab.append(d64QAM)
        print(dbpTab)
        print(dTab)
        return dTab, dQPSKTab, d16QAMTab, d64QAMTab

    def calcRange(self, Freq, type, Lmax):
        d = 0
        self.wynikLabel.clear()
        if type == 'WPP':
            fdB = 20 * math.log10(Freq)
            x = Lmax - 32.4 - fdB
            d = 10 ** (x / 20)
            self.wynikLabel.setText("d(f): " + str(round(d, 2)) + "m")
        elif type == 'ABG SC':
            alfa = 3.5
            beta = 24.4
            gamma = 1.9
            idk = 0
            x = Lmax - beta - 10 * gamma * math.log10(Freq / 1000) - idk
            d = 10 ** (x / (10 * alfa))
            self.wynikLabel.setText("d(f): " + str(round(d, 2)) + "m")
        elif type == 'ABG OS':
            alfa = 4.4
            beta = 2.4
            gamma = 1.9
            idk = 0
            x = Lmax - beta - 10 * gamma * math.log10(Freq / 1000) - idk
            d = 10 ** (x / (10 * alfa))
            self.wynikLabel.setText("d(f): " + str(round(d, 2)) + "m")
        elif type == 'CI SC':
            n = 3.1
            idk = 0
            x = Lmax - 20 * math.log10(4 * math.pi * Freq * 10 ** 6 / (3 * 10 ** 8)) - idk
            d = 10 ** (x / (10 * n))
            self.wynikLabel.setText("d(f): " + str(round(d, 2)) + "m")
        elif type == 'CI OS':
            n = 2.8
            idk = 0
            x = Lmax - 20 * math.log10(4 * math.pi * Freq * 10 ** 6 / (3 * 10 ** 8)) - idk
            d = 10 ** (x / (10 * n))
            self.wynikLabel.setText("d(f): " + str(round(d, 2)) + "m")
        elif type == "WINNER II LOS":
            hbs = 10
            hms = 1.5
            c = 3e8
            dbp = 4 * (hbs - 1) * (hms - 1) * Freq*10**6/c
            d = 10**((Lmax - 41 - 20 * math.log10(Freq/5000))/22.7)
            if d < dbp:
                d = d
            else:
                d = 10**((Lmax - 9.45 + 17.3 * math.log10(hbs + hms) - 2.7 * math.log10(Freq/5000))/40)
            self.wynikLabel.setText("d(f): " + str(round(d, 2)) + "m")


def calcLossForMod(mod):
    SNR = 0
    if mod == 'QPSK':  # CQI 1,2,3,4,5,6
        SNR = -8
    elif mod == '16QAM':  # CQI 7,8,9
        SNR = 6
    elif mod == "64QAM":  # CQI 10,11,12,13,14,15
        SNR = 15
    else:
        SNR = -20
    return SNR


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    okno = main_window()
    sys.exit(app.exec_())
