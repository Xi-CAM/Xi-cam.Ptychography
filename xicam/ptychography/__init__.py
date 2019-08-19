import logging

import numpy as np
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core import msg, threads
import pyqtgraph as pg
import zmq

from xicam.plugins import GUIPlugin, GUILayout


class PtychographyPlugin(GUIPlugin):
    name = 'Ptychography'

    def __init__(self):
        self.logwidget = QListWidget()
        self.leftdisplay = pg.ImageView()
        self.rightdisplay = pg.ImageView()
        self.stages = {'Ptychography': GUILayout(self.leftdisplay, right=self.rightdisplay)}
        super(PtychographyPlugin, self).__init__()

        self.thread = threads.QThreadFutureIterator(self.background_sock, callback_slot=self.display, showBusy=True)
        self.thread.start()

    @staticmethod
    def background_sock():
        ctx = zmq.Context()
        sock = ctx.socket(zmq.SUB)
        # sock.connect("tcp://n0001:5011")
        sock.connect("tcp://localhost:5011")
        sock.setsockopt(zmq.SUBSCRIBE, b"")
        # ax1.set_title('Reconstruction View')

        while True:
            msg.logMessage("waiting", msg.DEBUG)
            images = sock.recv_pyobj()
            msg.logMessage("showing", msg.DEBUG)
            msg.logMessage(images, msg.DEBUG)
            if images is not None:
                msg.logMessage(images[0].shape, msg.DEBUG)
                sq = int(np.sqrt(images[1].shape[0]))
                yield np.absolute(images[0]), np.absolute(images[1]).reshape((sq, sq))

    def display(self, left: np.ndarray, right: np.ndarray):
        self.leftdisplay.setImage(left)
        self.rightdisplay.setImage(right)
