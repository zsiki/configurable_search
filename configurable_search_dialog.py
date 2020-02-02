# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConfigurableSearchDialog
                                 A QGIS plugin
 Attribute search based on config file
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-02-01
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Zoltan Siki
        email                : siki1958@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
from qgis.core import QgsProject, QgsMapLayer, Qgis

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread
from .searchWorker import Worker

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'configurable_search_dialog_base.ui'))


class ConfigurableSearchDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, plugin, parent=None):
        """Constructor."""
        super(ConfigurableSearchDialog, self).__init__(parent)
        self.setupUi(self)
        self.plugin = plugin
        self.iface = plugin.iface
        self.tr = plugin.tr
        self.canvas = plugin.iface.mapCanvas()
        self.doneButton.clicked.connect(self.closeDialog)
        self.stopButton.clicked.connect(self.killWorker)
        self.searchButton.clicked.connect(self.runSearch)
        self.clearButton.clicked.connect(self.clearResults)
        self.maxResults = 1500
        self.resultsTable.setColumnCount(4)
        self.resultsTable.setSortingEnabled(False)
        self.resultsTable.setHorizontalHeaderLabels(self.plugin.headers)
        self.resultsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.comparisonComboBox.addItems(self.plugin.compTypes)
        self.comparisonComboBox.setCurrentIndex(2)  # starts with ...
        self.searchTypeComboBox.addItems(plugin.searchTypes.keys())
        self.resultsTable.itemSelectionChanged.connect(self.select_feature)

    def closeDialog(self):
        '''Close the dialog box when the Close button is pushed'''
        self.hide()

    def select_feature(self):
        '''A feature has been selected from the list so we need to select
        and zoom to it'''
        if self.noSelection:
            # We do not want this event while data is being changed
            return
        # Deselect all selections
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()
        # Find the layer that was selected and select the feature in the layer
        selectedRow = self.resultsTable.currentRow()
        selectedLayer = self.results[selectedRow][0]
        selectedFeature = self.results[selectedRow][1]
        selectedLayer.select(selectedFeature.id())
        # Zoom to the selected feature
        self.canvas.zoomToSelected(selectedLayer)

    def runSearch(self):
        '''Called when the user pushes the Search button'''
        searchT = str(self.searchTypeComboBox.currentText())
        searchL = self.plugin.searchTypes[searchT][0]
        searchP = self.plugin.searchTypes[searchT][1]
        selectedField = self.plugin.searchTypes[searchT][2]
        infield = True  # TODO
        comparisonMode = self.comparisonComboBox.currentIndex()
        self.noSelection = True
        try:
            sstr = self.findStringEdit.text().strip()
        except:
            self.showErrorMessage(self.tr(u'Invalid Search String'))
            return

        if str == '':
            self.showErrorMessage(self.tr(u'Search string is empty'))
            return
        # the vector layers that are to be searched
        self.vlayers = QgsProject.instance().mapLayersByName(searchL)
        if len(self.vlayers) == 0:
            # find layer by path
            for lay in self.iface.mapCanvas().layers():
                lp = lay.dataProvider().dataSourceUri().split('|')[0]
                print(lp)
                if lp == searchP:
                    self.vlayers.append(lay)
                    break
        # layer found?
        if len(self.vlayers) == 0:
            self.showErrorMessage(self.tr(u'There are no vector layers to search through'))
            return
        # vlayers contains the layers that we will search in
        self.searchButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.doneButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.clearResults()
        self.resultsLabel.setText('')

        # Because this could take a lot of time, set up a separate thread
        # for a worker function to do the searching.
        thread = QThread()
        worker = Worker(self.vlayers, infield, sstr, comparisonMode, selectedField, self.maxResults)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self.workerFinished)
        worker.foundmatch.connect(self.addFoundItem)
        worker.error.connect(self.workerError)
        self.thread = thread
        self.worker = worker
        self.noSelection = False
        thread.start()

    def workerFinished(self, status):
        '''Clean up the worker and thread'''
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.worker = None
        self.resultsLabel.setText('Results: '+str(self.found))

        self.vlayers = []
        self.searchButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.doneButton.setEnabled(True)

    def workerError(self, exception_string):
        '''An error occurred so display it.'''
        #self.showErrorMessage(exception_string)
        print(exception_string)

    def killWorker(self):
        '''This is initiated when the user presses the Stop button
        and will stop the search process'''
        if self.worker is not None:
            self.worker.kill()

    def clearResults(self):
        '''Clear all the search results.'''
        self.noSelection = True
        self.found = 0
        self.results = []
        self.resultsTable.setRowCount(0)
        self.noSelection = False

    def addFoundItem(self, layer, feature, attrname, value):
        '''We found an item so add it to the found list.'''
        self.resultsTable.insertRow(self.found)
        self.results.append([layer, feature])
        self.resultsTable.setItem(self.found, 0, QtWidgets.QTableWidgetItem(value))
        self.resultsTable.setItem(self.found, 1, QtWidgets.QTableWidgetItem(layer.name()))
        self.resultsTable.setItem(self.found, 2, QtWidgets.QTableWidgetItem(attrname))
        self.resultsTable.setItem(self.found, 3, QtWidgets.QTableWidgetItem(str(feature.id())))
        self.found += 1

    def showErrorMessage(self, message):
        '''Display an error message.'''
        self.iface.messageBar().pushMessage("", message, level=Qgis.Warning, duration=2)