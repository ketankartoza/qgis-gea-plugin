# -*- coding: utf-8 -*-
"""
    Plugin utilities
"""

import hashlib
import json
import os
import uuid
import datetime
from pathlib import Path

from qgis.PyQt import QtCore, QtGui
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
    QgsDistanceArea,
    QgsMessageLog,
    QgsProcessingFeedback,
    QgsProject,
    QgsProcessing,
    QgsRasterLayer,
    QgsRectangle,
    QgsUnitTypes,
)




def log(
    message: str,
    name: str = "qgis_gea",
    info: bool = True,
    notify: bool = True,
):
    """Logs the message into QGIS logs using qgis_cplus as the default
    log instance.
    If notify_user is True, user will be notified about the log.

    :param message: The log message
    :type message: str

    :param name: Name of te log instance, qgis_cplus is the default
    :type message: str

    :param info: Whether the message is about info or a
    warning
    :type info: bool

    :param notify: Whether to notify user about the log
    :type notify: bool
    """
    level = Qgis.Info if info else Qgis.Warning
    QgsMessageLog.logMessage(
        message,
        name,
        level=level,
        notifyUser=notify,
    )
