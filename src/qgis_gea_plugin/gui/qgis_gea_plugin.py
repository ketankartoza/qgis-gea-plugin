# -*- coding: utf-8 -*-

"""
 The plugin main window class file
"""

import os

from qgis.PyQt import (
    QtCore,
    QtGui,
    QtWidgets,
    QtNetwork,
)
from qgis.PyQt.uic import loadUiType

from qgis.core import QgsProject, QgsInterval, QgsUnitTypes, QgsTemporalNavigationObject
from qgis.gui import QgsLayerTreeView

from qgis.utils import iface

from ..resources import *

from ..models.base import IMAGERY
from ..utils import log


WidgetUi, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), "../ui/main_dockwidget.ui")
)


class QgisGeaPlugin(QtWidgets.QDockWidget, WidgetUi):
    """Main plugin UI"""

    def __init__(
        self,
        iface,
        parent=None,
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.iface = iface

        self.navigation_object = QgsTemporalNavigationObject(self)
        self.navigation_object.setFrameDuration(QgsInterval(1, QgsUnitTypes.TemporalIrregularStep))

        self.current_imagery_type = IMAGERY.HISTORICAL

        icon_pixmap = QtGui.QPixmap(":/plugins/qgis_gea_plugin/icon.png")
        self.icon_la.setPixmap(icon_pixmap)

        self.play_btn.setIcon(
            QtGui.QIcon(":/images/themes/default/mActionPlay.svg")
        )

        self.time_values = []

        self.historical_imagery.toggled.connect(self.prepare_time_slider)
        self.nicfi_imagery.toggled.connect(self.prepare_time_slider)

        self.prepare_time_slider()

        self.play_btn.clicked.connect(self.animate_layers)
        self.navigation_object.updateTemporalRange.connect(self.temporal_range_changed)

    def update_map_temporal_range(self):
        value = self.time_slider.value()

    def animate_layers(self):
        self.navigation_object.playForward()

    def temporal_range_changed(self, temporal_range):
        iface.mapCanvas().setTemporalRange(temporal_range)
        self.time_slider.setValue(self.navigation_object.currentFrameNumber())

    def prepare_time_slider(self):
        values = []
        set_layer = None
        active_layer = None

        if self.historical_imagery.isChecked():
            self.current_imagery_type = IMAGERY.HISTORICAL
        else:
            self.current_imagery_type = IMAGERY.NICFI

        layers = QgsProject.instance().mapLayers()
        for path, layer in layers.items():
            if layer.metadata().contains(
                    self.current_imagery_type.value.lower()
            ):
                values.append(
                    layer.temporalProperties().fixedTemporalRange()
                )
                active_layer = layer
            set_layer = layer

        self.update_layer_group(set_layer)
        self.update_layer_group(active_layer, False)

        self.time_slider.setRange(0, len(values) - 1)
        self.navigation_object.setAvailableTemporalRanges(values)

    def update_layer_group(self, layer, show=True):

        if layer is not None:
            layer_tree_view = iface.layerTreeView()
            root = QgsProject.instance().layerTreeRoot()
            layer_tree = root.findLayer(layer.id())

            if layer_tree is not None:
                group_tree = layer_tree.parent()
                if group_tree is not None:
                    index = layer_tree_view.layerTreeModel().node2index(
                        group_tree
                    )
                    layer_tree_view.setRowHidden(
                        index.row(),
                        index.parent(),
                        show
                    )
