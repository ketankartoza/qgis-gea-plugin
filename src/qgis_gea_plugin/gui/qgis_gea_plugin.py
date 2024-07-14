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
from ..definitions.defaults import ANIMATION_PLAY_ICON, ANIMATION_PAUSE_ICON, PLUGIN_ICON
from ..conf import settings_manager, Settings
from ..utils import animation_state_change, log, tr


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
        self.navigation_object.setFrameDuration(
            QgsInterval(1, QgsUnitTypes.TemporalIrregularStep)
        )

        self.current_imagery_type = IMAGERY.HISTORICAL

        icon_pixmap = QtGui.QPixmap(PLUGIN_ICON)
        self.icon_la.setPixmap(icon_pixmap)

        self.play_btn.setIcon(
            QtGui.QIcon(ANIMATION_PLAY_ICON)
        )

        self.time_values = []

        self.historical_imagery.setChecked(
            settings_manager.get_value(
                Settings.HISTORICAL_VIEW,
                setting_type=bool,
                default=True)
        )

        self.nicfi_imagery.setChecked(
            settings_manager.get_value(
                Settings.NICFI_VIEW,
                setting_type=bool,
                default=False)
        )
        self.prepare_time_slider()

        self.historical_imagery.toggled.connect(self.prepare_time_slider)
        self.nicfi_imagery.toggled.connect(self.prepare_time_slider)

        self.play_btn.clicked.connect(self.animate_layers)
        self.navigation_object.updateTemporalRange.connect(
            self.temporal_range_changed
        )
        self.time_slider.valueChanged.connect(
            self.slider_value_changed
        )

        iface.projectRead.connect(self.prepare_time_slider)

    def slider_value_changed(self, value):
        self.navigation_object.setCurrentFrameNumber(value)

    def animate_layers(self):
        if self.navigation_object.animationState() == \
            QgsTemporalNavigationObject.AnimationState.Idle:
            self.play_btn.setIcon(
                QtGui.QIcon(ANIMATION_PAUSE_ICON)
            )
            self.navigation_object.playForward()
        else:
            self.navigation_object.pause()
            self.play_btn.setIcon(
                QtGui.QIcon(ANIMATION_PLAY_ICON)
            )

    def temporal_range_changed(self, temporal_range):
        iface.mapCanvas().setTemporalRange(temporal_range)
        self.temporal_range_la.setText(
            tr(
                f'Current time range: '
                f'<b>{temporal_range.begin().toString("yyyy-MM-ddTHH:mm:ss")} to '
                f'{temporal_range.end().toString("yyyy-MM-ddTHH:mm:ss")} </b>'
            ))
        self.time_slider.setValue(
            self.navigation_object.currentFrameNumber()
        )

        # On the last animation frame
        if self.navigation_object.currentFrameNumber() == \
            len(self.navigation_object.availableTemporalRanges()) - 1:

            self.play_btn.setIcon(
                QtGui.QIcon(ANIMATION_PLAY_ICON)
            )

    def prepare_time_slider(self):
        values = []
        set_layer = None
        active_layer = None

        if self.historical_imagery.isChecked():
            settings_manager.set_value(Settings.HISTORICAL_VIEW, True)
            settings_manager.set_value(Settings.NICFI_VIEW, False)

            self.current_imagery_type = IMAGERY.HISTORICAL
        else:
            settings_manager.set_value(Settings.NICFI_VIEW, True)
            settings_manager.set_value(Settings.HISTORICAL_VIEW, False)

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
            else:
                set_layer = layer

        self.update_layer_group(set_layer)
        self.update_layer_group(active_layer, True)

        self.time_slider.setRange(0, len(values) - 1)
        self.navigation_object.setAvailableTemporalRanges(values)

        temporal_range = values[0] if len(values) > 0 else None

        if temporal_range:
            iface.mapCanvas().setTemporalRange(temporal_range)
            self.temporal_range_la.setText(
                tr(
                    f'Current time range: '
                    f'<b>{temporal_range.begin().toString("yyyy-MM-ddTHH:mm:ss")} to '
                    f'{temporal_range.end().toString("yyyy-MM-ddTHH:mm:ss")} </b>'
                ))

    def update_layer_group(self, layer, show=False):

        if layer is not None:
            root = QgsProject.instance().layerTreeRoot()
            layer_tree = root.findLayer(layer.id())

            if layer_tree is not None:
                group_tree = layer_tree.parent()
                if group_tree is not None:
                    group_tree.setItemVisibilityCheckedRecursive(show)
