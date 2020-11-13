from __future__ import unicode_literals
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox
from PyQt5.QtWidgets import QLabel, QGridLayout, QSpacerItem
from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QGraphicsView, \
    QGraphicsScene, QSizePolicy, QCheckBox, QAction, QFileDialog
from PyQt5.QtCore import Qt, QRect
from Parametry import Parametr, modelComboBox, CQI
import math
import pyqtgraph as pg
import random
import numpy as np
import time
import xlwt
from xlwt import Workbook
from datetime import date

MAX_FREQ = 18000
MIN_FREQ = 2000
STEP = 100


class main_window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450, 200, 1100, 550)
        self.setWindowTitle("NRange")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.interfejs()
        self.show()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)

    def interfejs(self):
        layout = QHBoxLayout()
        ### INPUTY PARAMETROW
        fieldsLayout = QGridLayout()  # layout dla prawej części
        itemsLayout = QVBoxLayout()  # g lowny layout

        self.Ptx = Parametr("Ptx [dBm]", 0, 99, 10)
        self.Gtx = Parametr("Gtx [dBi]", 0, 99, 14)
        self.Ftx = Parametr("Ftx [dB]", 0, 99, 2)
        self.Grx = Parametr("Grx [dBi]", 0, 99, 3)
        self.Frx = Parametr("Frx [dB]", 0, 99, 1)
        self.SNR = Parametr("SNR [dB]", -20, 99, 5)
        self.bandwitch = Parametr("B [MHz]", 1, 200, 20)
        self.Fnoise = Parametr("Fnoise [dB]", 0, 99, 5)
        self.Temp = Parametr("Temp [K]", 1, 999, 293)
        self.Freq = Parametr("Freq [MHz]", MIN_FREQ, MAX_FREQ, MIN_FREQ)
        self.CQIbox = Parametr("CQI", 1, 15, 1)
        self.wyborModelu = modelComboBox("Model propagacyjny")
        self.wyborOsiX = modelComboBox("Oś x")
        self.wynikLabel = QLabel()
        self.wynik2Label = QLabel()
        self.zapiszButton = QPushButton("Zapisz")
        self.usrednianieButton = QCheckBox("Uśrednianie")
        self.wynikiGrid = QVBoxLayout()
        self.wynikiGrid.addWidget(self.wynikLabel)
        self.wynikiGrid.addWidget(self.wynik2Label)

        fieldsLayout.addItem(self.wyborModelu, 0, 0)
        fieldsLayout.addItem(self.wyborOsiX, 0, 2)
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
        fieldsLayout.addItem(self.CQIbox, 5, 0)
        fieldsLayout.addItem(self.wynikiGrid, 5, 1)
        # fieldsLayout.addWidget(self.wynik2Label, 6, 1)
        fieldsLayout.addWidget(self.zapiszButton, 6, 2)
        fieldsLayout.addWidget(self.usrednianieButton, 6, 0)
        fieldsLayout.setSpacing(20)
        # self.scene = QGraphicsScene()
        # scene.addText("ddddddddddddddddddddddddddddddddddddddddddddd")
        # view = QGraphicsView(self.scene)
        # oblcizanie
        calculateButton = QPushButton()
        calculateButton.setText("Oblicz zasięg")
        calculateButton.clicked.connect(lambda x: self.propagationModel())
        fieldsLayout.addWidget(calculateButton, 5, 2)

        # zapisywanie
        # TUTAJ DEFINICJA ELEMENTOW DO ZAPISYWANIA
        self.savePtx, self.saveGtx, self.saveFtx, self.saveGrx, self.saveFrx, self.saveSNR, self.saveB, self.saveTemp, self.saveFnoise = 0, 1, 2, 3, 4, 5, 6, 7, 8
        self.saveFreq = 0
        self.saveOdleglosc, self.saveOdlegloscFading, self.saveOSX = [1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]       # test, docelowo puste, sprawdzic w saveToExcel()
        self.saveModel, self.saveOSXname = "TEST", "TEST_NAME"
        # TJ WSZYSTKIE PARAMETRY JAKIE SIE ZMIENIA
        # ORAZ TABLICE WYNIKOW
        # I NAZWE MODELU I OSI
        self.zapiszButton.clicked.connect(lambda x: self.saveToExcel())

        layout.addWidget(self.view)
        self.view.show()
        # lewa strona
        # layout.addWidget(paintContainer)
        verticalSpacer = QSpacerItem(1, 50, QSizePolicy.Fixed, QSizePolicy.Expanding)
        fieldsLayout.setAlignment(Qt.AlignRight)
        fieldsLayout.addItem(verticalSpacer, 7, 0)
        fieldsLayout.addItem(verticalSpacer, 7, 1)
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

        if self.wyborOsiX.wybor.currentText() == 'f [MHz]':
            self.freqChoosen(Ptx, Gtx, Ftx, Grx, Frx, SNR, bandwitch, Temp, Fnoise, Freq, k)
        elif self.wyborOsiX.wybor.currentText() == 'CQI':
            self.CQIchoosen(Ptx, Gtx, Ftx, Grx, Frx, SNR, bandwitch, Temp, Fnoise, Freq, k)

        # self.scene.clear()
        # self.scene.addText(str(round(d*1000, 2)))  # odleglosc w metrach
        # L = 32,4 +20lg f [MHz] + 20lg d [km]
        # 20lg d = L - 32,4 - 20lg f
        # d = 10^(x/20)

    def plot(self, x, y, plotname, color, dash=False):
        if dash:
            pen = pg.mkPen(color=color, style=Qt.DashLine)
            plotname = plotname + ' z zanikami'
        else:
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

    def ABGmodel(self, Lmax=0, LmaxQPSK=0, Lmax16QAM=0, Lmax64QAM=0, FdBtab=list(), type='', cqi=False, freq=0, fading=0):
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

        if fading != 0:
            idk = fading

        if cqi == False:
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
        else:
            x = Lmax - beta - 10 * gamma * math.log10(freq / 1000) - idk
            d = 10 ** (x / (10 * alfa))
            return d

    def CImodel(self, Lmax=0, LmaxQPSK=0, Lmax16QAM=0, Lmax64QAM=0, FdBtab=list(), type='', cqi=False, freq=0, fading=0):
        # obliczanie X
        n = 1
        idk = 0
        if type == 'SC':
            n = 3.1
        elif type == 'OS':
            n = 2.8

        if fading != 0:
            idk = fading

        if cqi == False:
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
        else:
            x = Lmax - 20 * math.log10(4 * math.pi * freq * 10 ** 6 / (3 * 10 ** 8)) - idk
            d = 10 ** (x / (10 * n))
            return d

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

    def calcRange(self, Freq, type, Lmax, fading=0, cqi=False):
        d = 0
        if fading == 0:
            self.wynikLabel.clear()
            self.wynik2Label.clear()
        else:
            self.wynik2Label.clear()

        idk = fading
        if type == 'WPP':
            fdB = 20 * math.log10(Freq)
            x = Lmax - 32.4 - fdB
            d = 10 ** (x / 20)
        elif type == 'ABG SC':
            alfa = 3.5
            beta = 24.4
            gamma = 1.9
            x = Lmax - beta - 10 * gamma * math.log10(Freq / 1000) - idk
            d = 10 ** (x / (10 * alfa))
        elif type == 'ABG OS':
            alfa = 4.4
            beta = 2.4
            gamma = 1.9
            x = Lmax - beta - 10 * gamma * math.log10(Freq / 1000) - idk
            d = 10 ** (x / (10 * alfa))
        elif type == 'CI SC':
            n = 3.1
            x = Lmax - 20 * math.log10(4 * math.pi * Freq * 10 ** 6 / (3 * 10 ** 8)) - idk
            d = 10 ** (x / (10 * n))
        elif type == 'CI OS':
            n = 2.8
            idk = 0
            x = Lmax - 20 * math.log10(4 * math.pi * Freq * 10 ** 6 / (3 * 10 ** 8)) - idk
            d = 10 ** (x / (10 * n))
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

        text = ''
        if cqi == True:
            text = "d(CQI): "
        else:
            text = "d(f): "
        if fading == 0:
            self.wynikLabel.setText(text + str(round(d, 2)) + "m")
        else:
            self.wynik2Label.setText(text + str(round(d, 2)) + "m")

    def freqChoosen(self,Ptx, Gtx, Ftx, Grx, Frx, SNR, bandwitch, Temp, Fnoise, Freq, k):
        # Częstoty do rysowania
        Ftab = [x for x in range(MIN_FREQ, MAX_FREQ + STEP, STEP)]
        FdBtab = [20 * math.log10(x) for x in Ftab]
        N = 10 * math.log10((k * bandwitch * (10 ** 6) * Temp) * 1000)
        # SNR USTAWIONE
        Lmax = Ptx + Gtx - Ftx + Grx - Frx - SNR - N - Fnoise - 2
        # Lmax dla QPSK
        LmaxQPSK = Ptx + Gtx - Ftx + Grx - Frx - calcLossForMod('QPSK') - N - Fnoise - 2
        # Lmax dla 16QAM
        Lmax16QAM = Ptx + Gtx - Ftx + Grx - Frx - calcLossForMod('16QAM') - N - Fnoise - 2
        # Lmax dla 64QAM
        Lmax64QAM = Ptx + Gtx - Ftx + Grx - Frx - calcLossForMod('64QAM') - N - Fnoise - 2

        mean = 0
        sigmaABG = 8
        sigmaCI = 8.1
        fadingABG = abs(random.gauss(mean, sigmaABG))
        fadingCI = abs(random.gauss(mean, sigmaCI))

        Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = 0, 0, 0, 0
        Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = 0, 0, 0, 0
        self.graphWidget.clear()

        if not self.usrednianieButton.isChecked():
            if self.wyborModelu.wybor.currentText() == 'ABG SC':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC')
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC', fading=fadingABG)
            elif self.wyborModelu.wybor.currentText() == 'ABG OS':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS')
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS', fading=fadingABG)
            elif self.wyborModelu.wybor.currentText() == 'CI SC':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC')
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC', fading=fadingCI)
            elif self.wyborModelu.wybor.currentText() == 'CI OS':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS')
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS', fading=fadingCI)
            elif self.wyborModelu.wybor.currentText() == 'WINNER II LOS':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.WINNERIIB1model(Ftab, Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM)
            else:
                self.scene.clear()
        else:
            if self.wyborModelu.wybor.currentText() == 'ABG SC':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC')
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array([]), np.array([]),  np.array([]), np.array([])
                N = 1000
                for x in range(N):
                    fadingABG = abs(random.gauss(mean, sigmaABG))
                    Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC', fading=fadingABG)
                    if x == 0:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array(Dtabfading), np.array(DtabQPSKfading),  np.array(Dtab16QAMfading), np.array(Dtab64QAMfading)
                    else:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.add(Dmeantab, np.array(Dtabfading)), np.add(DQPSKmeantab, np.array(DtabQPSKfading)), \
                            np.add(D16QAMmeantab, np.array(Dtab16QAMfading)), np.add(D64QAMmeantab, np.array(Dtab64QAMfading))
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = Dmeantab / N, DQPSKmeantab / N, D16QAMmeantab / N, D64QAMmeantab / N
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = Dmeantab.tolist(), DQPSKmeantab.tolist(), D16QAMmeantab.tolist(), D64QAMmeantab.tolist()
            elif self.wyborModelu.wybor.currentText() == 'ABG OS':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS')
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array([]), np.array([]), np.array([]), np.array([])
                N = 1000
                for x in range(N):
                    fadingABG = abs(random.gauss(mean, sigmaABG))
                    Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.ABGmodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS', fading=fadingABG)
                    if x == 0:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array(Dtabfading), np.array(DtabQPSKfading), np.array(Dtab16QAMfading), np.array(Dtab64QAMfading)
                    else:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.add(Dmeantab, np.array(Dtabfading)), np.add(DQPSKmeantab, np.array(DtabQPSKfading)), np.add(D16QAMmeantab, np.array(
                            Dtab16QAMfading)), np.add(D64QAMmeantab, np.array(Dtab64QAMfading))
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = Dmeantab / N, DQPSKmeantab / N, D16QAMmeantab / N, D64QAMmeantab / N
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = Dmeantab.tolist(), DQPSKmeantab.tolist(), D16QAMmeantab.tolist(), D64QAMmeantab.tolist()
            elif self.wyborModelu.wybor.currentText() == 'CI SC':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC')
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array([]), np.array([]), np.array([]), np.array([])
                N = 1000
                for x in range(N):
                    fadingCI = abs(random.gauss(mean, sigmaCI))
                    Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'SC', fading=fadingCI)
                    if x == 0:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array(Dtabfading), np.array(DtabQPSKfading), np.array(Dtab16QAMfading), np.array(Dtab64QAMfading)
                    else:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.add(Dmeantab, np.array(Dtabfading)), np.add(DQPSKmeantab, np.array(DtabQPSKfading)), np.add(D16QAMmeantab, np.array(
                            Dtab16QAMfading)), np.add(D64QAMmeantab, np.array(Dtab64QAMfading))
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = Dmeantab / N, DQPSKmeantab / N, D16QAMmeantab / N, D64QAMmeantab / N
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = Dmeantab.tolist(), DQPSKmeantab.tolist(), D16QAMmeantab.tolist(), D64QAMmeantab.tolist()
            elif self.wyborModelu.wybor.currentText() == 'CI OS':
                Dtab, DtabQPSK, Dtab16QAM, Dtab64QAM = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS')
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array([]), np.array([]), np.array([]), np.array([])
                N = 1000
                for x in range(N):
                    fadingCI = abs(random.gauss(mean, sigmaCI))
                    Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = self.CImodel(Lmax, LmaxQPSK, Lmax16QAM, Lmax64QAM, Ftab, 'OS', fading=fadingCI)
                    if x == 0:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.array(Dtabfading), np.array(DtabQPSKfading), np.array(Dtab16QAMfading), np.array(Dtab64QAMfading)
                    else:
                        Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = np.add(Dmeantab, np.array(Dtabfading)), np.add(DQPSKmeantab, np.array(DtabQPSKfading)), np.add(D16QAMmeantab, np.array(
                            Dtab16QAMfading)), np.add(D64QAMmeantab, np.array(Dtab64QAMfading))
                Dmeantab, DQPSKmeantab, D16QAMmeantab, D64QAMmeantab = Dmeantab / N, DQPSKmeantab / N, D16QAMmeantab / N, D64QAMmeantab / N
                Dtabfading, DtabQPSKfading, Dtab16QAMfading, Dtab64QAMfading = Dmeantab.tolist(), DQPSKmeantab.tolist(), D16QAMmeantab.tolist(), D64QAMmeantab.tolist()

        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend(offset=(400, 10))

        # self.graphWidget.setXRange(1,10000)
        # self.graphWidget.setYRange(1,10000)
        self.scene.addWidget(self.graphWidget)
        # xLabelFreqdB = [10 * math.log10(x) for x in Ftab]
        xLabelFreqdB = Ftab
        self.plot(xLabelFreqdB, Dtab, 'Własne SNR', 'k')
        self.plot(xLabelFreqdB, DtabQPSK, 'QPSK', 'r')
        self.plot(xLabelFreqdB, Dtab16QAM, '16QAM', 'g')
        self.plot(xLabelFreqdB, Dtab64QAM, '64QAM', 'b')
        self.plot(xLabelFreqdB, Dtabfading, 'Własne SNR', 'k', dash=True)
        self.plot(xLabelFreqdB, DtabQPSKfading, 'QPSK', 'r', dash=True)
        self.plot(xLabelFreqdB, Dtab16QAMfading, '16QAM', 'g', dash=True)
        self.plot(xLabelFreqdB, Dtab64QAMfading, '64QAM', 'b', dash=True)
        self.graphWidget.setTitle("Zasięg użyteczny [m] w funkcji częstotliwości [MHz]", color='k', size='10pt')
        styles = {'color': 'k', 'font-size': '15px'}
        self.graphWidget.setLabel('left', 'Odległość [m]', **styles)
        self.graphWidget.setLabel('bottom', 'Częstotliwość f[MHz]', **styles)

        # obliczanie zasiegu
        if self.wyborModelu.wybor.currentText() == 'ABG SC':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "ABG SC", Lmax)
            text = "d'(f): "
            value = Freq - MIN_FREQ
            index = int(value/100)
            self.wynik2Label.setText(text + str(round(Dtabfading[index], 2)) + "m")
        elif self.wyborModelu.wybor.currentText() == 'ABG OS':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "ABG OS", Lmax)
            text = "d'(f): "
            value = Freq - MIN_FREQ
            index = int(value / 100)
            self.wynik2Label.setText(text + str(round(Dtabfading[index], 2)) + "m")
        elif self.wyborModelu.wybor.currentText() == 'CI SC':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "CI SC", Lmax)
            text = "d'(f): "
            value = Freq - MIN_FREQ
            index = int(value / 100)
            self.wynik2Label.setText(text + str(round(Dtabfading[index], 2)) + "m")
        elif self.wyborModelu.wybor.currentText() == 'CI OS':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "CI OS", Lmax)
            text = "d'(f): "
            value = Freq - MIN_FREQ
            index = int(value / 100)
            self.wynik2Label.setText(text + str(round(Dtabfading[index], 2)) + "m")
        #               Ptx, Gtx, Ftx, Grx, Frx, SNR, bandwitch, Temp, Fnoise, Freq,
        self.savePtx, self.saveGtx, self.saveFtx, self.saveGrx, self.saveFrx, self.saveSNR, self.saveB, self.saveTemp, self.saveFnoise = Ptx, Gtx, Ftx, Grx, Frx, SNR, bandwitch, Temp, Fnoise
        self.saveOdlegloscFading, self.saveOdleglosc, self.saveOSX = [round(x, 2) for x in Dtabfading], [round(x, 2) for x in Dtab], Ftab  # test, docelowo puste, sprawdzic w saveToExcel()
        self.saveOSXname = "Częstotliwość [MHz]"
        self.saveModel = self.wyborModelu.wybor.currentText()

    def CQIchoosen(self,Ptx, Gtx, Ftx, Grx, Frx, SNR, bandwitch, Temp, Fnoise, Freq, k):
        CQItab = [-7.8474, -6.2369, -4.3591, -1.9319, 0.1509, 1.9976, 4.7278, 6.2231, 8.0591, 9.8585, 11.8432, 13.4893, 15.3598, 17.4435,
                  19.2155]
        CQIindex = [x for x in range(1, 16)]
        N = 10 * math.log10((k * bandwitch * (10 ** 6) * Temp) * 1000)
        # SNR USTAWIONE
        Ltab = [Ptx + Gtx - Ftx + Grx - Frx - value - N - Fnoise - 2 for value in CQItab]

        mean = 0
        sigmaABG = 8
        sigmaCI = 8.1
        fadingABG = abs(random.gauss(mean, sigmaABG))
        fadingCI = abs(random.gauss(mean, sigmaCI))
        Dtab = []
        Dfadingtab = []

        if not self.usrednianieButton.isChecked():
            for L in Ltab:
                D = 0
                Dfading = 0
                if self.wyborModelu.wybor.currentText() == 'ABG SC':
                    D = self.ABGmodel(L, type='SC', cqi=True, freq=Freq)
                    Dfading = self.ABGmodel(L, type='SC', cqi=True, freq=Freq, fading=fadingABG)
                elif self.wyborModelu.wybor.currentText() == 'ABG OS':
                    D = self.ABGmodel(L, type='OS', cqi=True, freq=Freq)
                    Dfading = self.ABGmodel(L, type='OS', cqi=True, freq=Freq, fading=fadingABG)
                elif self.wyborModelu.wybor.currentText() == 'CI SC':
                    D = self.CImodel(L, type='SC', cqi=True, freq=Freq)
                    Dfading = self.CImodel(L, type='SC', cqi=True, freq=Freq, fading=fadingCI)
                elif self.wyborModelu.wybor.currentText() == 'CI OS':
                    D = self.CImodel(L, type='OS', cqi=True, freq=Freq)
                    Dfading = self.CImodel(L, type='OS', cqi=True, freq=Freq, fading=fadingCI)
                Dtab.append(D)
                Dfadingtab.append(Dfading)
        else:
            if self.wyborModelu.wybor.currentText() == 'ABG SC':
                Dtab = [self.ABGmodel(L, type='SC', cqi=True, freq=Freq) for L in Ltab]
                Dmeantab = np.array([])
                N = 1000
                for x in range(N):
                    fadingABG = abs(random.gauss(mean, sigmaABG))
                    fadingCI = abs(random.gauss(mean, sigmaCI))
                    Dfadingtab = [self.ABGmodel(L, type='SC', cqi=True, freq=Freq, fading=fadingABG) for L in Ltab]
                    if x == 0:
                        Dmeantab = np.array(Dfadingtab)
                    else:
                        Dmeantab = np.add(Dmeantab, np.array(Dfadingtab))
                Dmeantab = Dmeantab / N
                Dfadingtab = Dmeantab.tolist()
            elif self.wyborModelu.wybor.currentText() == 'ABG OS':
                Dtab = [self.ABGmodel(L, type='OS', cqi=True, freq=Freq) for L in Ltab]
                Dmeantab = np.array([])
                N = 1000
                for x in range(N):
                    fadingABG = abs(random.gauss(mean, sigmaABG))
                    fadingCI = abs(random.gauss(mean, sigmaCI))
                    Dfadingtab = [self.ABGmodel(L, type='OS', cqi=True, freq=Freq, fading=fadingABG) for L in Ltab]
                    if x == 0:
                        Dmeantab = np.array(Dfadingtab)
                    else:
                        Dmeantab = np.add(Dmeantab, np.array(Dfadingtab))
                Dmeantab = Dmeantab / N
                Dfadingtab = Dmeantab.tolist()
            elif self.wyborModelu.wybor.currentText() == 'CI SC':
                Dtab = [self.CImodel(L, type='SC', cqi=True, freq=Freq) for L in Ltab]
                Dmeantab = np.array([])
                N = 1000
                for x in range(N):
                    fadingABG = abs(random.gauss(mean, sigmaABG))
                    fadingCI = abs(random.gauss(mean, sigmaCI))
                    Dfadingtab = [self.CImodel(L, type='SC', cqi=True, freq=Freq, fading=fadingABG) for L in Ltab]
                    if x == 0:
                        Dmeantab = np.array(Dfadingtab)
                    else:
                        Dmeantab = np.add(Dmeantab, np.array(Dfadingtab))
                Dmeantab = Dmeantab / N
                Dfadingtab = Dmeantab.tolist()
            elif self.wyborModelu.wybor.currentText() == 'CI OS':
                Dtab = [self.CImodel(L, type='OS', cqi=True, freq=Freq) for L in Ltab]
                Dmeantab = np.array([])
                N = 1000
                for x in range(N):
                    fadingABG = abs(random.gauss(mean, sigmaABG))
                    fadingCI = abs(random.gauss(mean, sigmaCI))
                    Dfadingtab = [self.CImodel(L, type='OS', cqi=True, freq=Freq, fading=fadingABG) for L in Ltab]
                    if x == 0:
                        Dmeantab = np.array(Dfadingtab)
                    else:
                        Dmeantab = np.add(Dmeantab, np.array(Dfadingtab))
                Dmeantab = Dmeantab / N
                Dfadingtab = Dmeantab.tolist()

        self.graphWidget.clear()
        # self.graphWidget.setLimits(xMin=0, xMax=16, yMin=0)
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend(offset=(440, 10))
        self.scene.addWidget(self.graphWidget)
        xLabel = CQIindex
        self.plot(xLabel, Dtab, 'd(CQI) - bez zaników', 'k')
        self.plot(xLabel, Dfadingtab, 'd(CQI) - z zanikami', 'r')
        self.graphWidget.setTitle("Zasięg użyteczny [m] w funkcji CQI [SNR [dB]]", color='k', size='10pt')
        styles = {'color': 'k', 'font-size': '15px'}
        self.graphWidget.setLabel('left', 'Odległość [m]', **styles)
        self.graphWidget.setLabel('bottom', 'CQI', **styles)

        # obliczenie zasięgu

        CQInumber = int(self.CQIbox.container.text())
        if CQInumber > 15 or CQInumber < -1:
            self.CQIbox.container.setText('1')
            self.CQIbox.slider.setValue(1)
            CQInumber = 1
        Lmax = Ltab[CQInumber - 1]
        if self.wyborModelu.wybor.currentText() == 'ABG SC':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "ABG SC", Lmax, cqi=True)
            text = "d'(CQI): "
            self.wynik2Label.setText(text + str(round(Dfadingtab[CQInumber - 1], 2)) + "m")
        elif self.wyborModelu.wybor.currentText() == 'ABG OS':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "ABG OS", Lmax, cqi=True)
            text = "d'(CQI): "
            self.wynik2Label.setText(text + str(round(Dfadingtab[CQInumber - 1], 2)) + "m")
        elif self.wyborModelu.wybor.currentText() == 'CI SC':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "CI SC", Lmax, cqi=True)
            text = "d'(CQI): "
            self.wynik2Label.setText(text + str(round(Dfadingtab[CQInumber - 1], 2)) + "m")
        elif self.wyborModelu.wybor.currentText() == 'CI OS':
            self.wynikLabel.clear()
            self.wynik2Label.clear()
            self.calcRange(Freq, "CI OS", Lmax, cqi=True)
            text = "d'(CQI): "
            self.wynik2Label.setText(text + str(round(Dfadingtab[CQInumber - 1], 2)) + "m")

        self.savePtx, self.saveGtx, self.saveFtx, self.saveGrx, self.saveFrx, self.saveFreq, self.saveB, self.saveTemp, self.saveFnoise = Ptx, Gtx, Ftx, Grx, Frx, Freq, bandwitch, Temp, Fnoise
        self.saveOdlegloscFading, self.saveOdleglosc, self.saveOSX = [round(x, 2) for x in Dfadingtab], [round(x, 2) for x in Dtab], CQIindex  # test, docelowo puste, sprawdzic w saveToExcel()
        self.saveOSXname = "CQI"
        self.saveModel = self.wyborModelu.wybor.currentText()

    def saveToExcel(self):
        name = QFileDialog.getSaveFileName(self, 'Zapisz plik')
        actualname = str(name[0])
        if '.xls' in actualname:
            actualname = actualname.replace('.xls', '')
        wb = Workbook()
        sheet1 = wb.add_sheet('Zasięg')
        t = time.localtime()
        today = date.today()
        todaydate = today.strftime("%d/%m/%Y")
        currentTime = time.strftime("%H:%M:%S", t)        # wiersz, kolumna

        #style = xlwt.easyxf('font: bold 1')

        sheet1.write(0, 0, self.saveModel)
        sheet1.write(0, 2, currentTime)
        sheet1.write(0, 3, todaydate)
        sheet1.write(1, 0, 'Ptx [dBm]')
        sheet1.write(1, 1, 'Gtx [dBm]')
        sheet1.write(1, 2, 'Ftx [dBm]')
        sheet1.write(1, 3, 'Grx [dBm]')
        sheet1.write(1, 4, 'Frx [dBm]')

        sheet1.write(1, 6, 'Bandwidth [MHz]')
        sheet1.write(1, 7, 'Temp [K]')
        sheet1.write(1, 8, 'Fnoise [dBm]')
        sheet1.write(2, 0, self.savePtx)
        sheet1.write(2, 1, self.saveGtx)
        sheet1.write(2, 2, self.saveFtx)
        sheet1.write(2, 3, self.saveGrx)
        sheet1.write(2, 4, self.saveFrx)
        if self.saveOSXname == "CQI":
            sheet1.write(2, 5, self.saveFreq)
            sheet1.write(1, 5, 'Freq [MHz]')
        else:
            sheet1.write(2, 5, self.saveSNR)
            sheet1.write(1, 5, 'SNR [dBm]')
        sheet1.write(2, 6, self.saveB)
        sheet1.write(2, 7, self.saveTemp)
        sheet1.write(2, 8, self.saveFnoise)
        sheet1.write(3, 0, self.saveOSXname)
        sheet1.write(3, 1, "Odległość z zanikami [d]: ")
        sheet1.write(3, 2, "Odległość bez zaników [d]: ")

        for i, x in enumerate(self.saveOSX):
            sheet1.write(4 + i, 0, x)
        for i, x in enumerate(self.saveOdlegloscFading):
            sheet1.write(4 + i, 1, x)
        for i, x in enumerate(self.saveOdleglosc):
            sheet1.write(4 + i, 2, x)


        wb.save(actualname + '.xls')


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
