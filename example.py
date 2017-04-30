#!/usr/bin/env python2

import sys
from PyQt5 import QtWidgets,QtGui

from ratingWidget import RatingWidget

class myWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        im = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap('rating.png')
        im.setPixmap(pixmap)
        hbox.addWidget(im)
        #im.move(0,0)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Make a label for the rating widget.
        rating_label_widget = QtWidgets.QLabel('Rating:')

        # Make a widget to report the current value of the rating widget.
        rating_value_widget = QtWidgets.QLabel('0')

        # Make the rating widget.
        rating_widget = RatingWidget(num_icons=10)
        rating_widget.value_updated.connect(
            lambda value: rating_value_widget.setText(str(value))
        )

        # Make the central widget layout.
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(rating_label_widget)
        main_layout.addWidget(rating_value_widget)
        main_layout.addWidget(rating_widget, stretch=1)


        # Make the central widget.
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Cleanlooks')
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

