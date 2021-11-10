import sys
import sqlite3
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Ui.ui', self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.coords)
        self.x = self.y = self.size = None

    def coords(self):
        self.x = random.randint(0, 300)
        self.y = random.randint(0, 300)
        self.size = random.randint(0, 200)
        self.repaint()

    def yellowCircles(self, qp):
        if self.x is None or self.y is None or self.size is None:
            return
        qp.setBrush(QBrush(Qt.yellow))
        qp.drawEllipse(self.x, self.y, self.size, self.size)
        """if self.x is None or self.y is None or self.button is None:
            return
        size = random.randint(0, 200)
        color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if self.button == Qt.MouseButton.LeftButton:
            # Задаем кисть
            qp.setBrush(color)
            # Рисуем прямоугольник заданной кистью
            qp.drawEllipse(self.x - size // 2, self.y - size // 2, size, size)
        elif self.button == Qt.MouseButton.RightButton:
            # Задаем кисть
            qp.setBrush(color)
            # Рисуем прямоугольник заданной кистью
            qp.drawRect(self.x - size // 2, self.y - size // 2, size, size)
        elif self.button == Qt.Key.Key_Space:
            qp.setBrush(color)
            # Рисуем прямоугольник заданной кистью
            points = [QPoint(self.x - size // 3, self.y - size // 5),
                      QPoint(self.x + size // 2, self.y + size),
                      QPoint(self.x + size // 2, self.y - size // 2)]
            qp.drawPolygon(QPolygon(points))"""

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(Qt.yellow))
        self.yellowCircles(qp)
        qp.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
