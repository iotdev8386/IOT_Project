import sys
import random
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

def fake_data():
    return {
        "amperage": round(random.uniform(10, 20), 1),
        "energy": round(random.uniform(500, 800), 1),
        "frequency": round(random.uniform(49, 61), 1),
        "power": round(random.uniform(1000, 3000), 1),
        "voltage": round(random.uniform(210, 250), 1),
    }

class PowerMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔌 Realtime Power Monitoring")
        self.setGeometry(200, 200, 500, 300)
        self.setStyleSheet("background-color: #1e1e2f; color: #fff;")

        self.font_label = QFont("Arial", 14, QFont.Bold)
        self.font_value = QFont("Arial", 22)

        self.layout = QVBoxLayout()
        self.grid = QGridLayout()

        self.fields = ["amperage", "energy", "frequency", "power", "voltage"]
        self.units = {
            "amperage": "A",
            "energy": "kWh",
            "frequency": "Hz",
            "power": "W",
            "voltage": "V"
        }
        self.labels = {}

        row = 0
        for field in self.fields:
            label = QLabel(field.capitalize())
            label.setFont(self.font_label)
            label.setStyleSheet("color: #aaa;")
            value = QLabel("—")
            value.setFont(self.font_value)
            value.setStyleSheet("color: #00ffcc;")
            self.labels[field] = value

            box = QFrame()
            box.setStyleSheet("""
                QFrame {
                    background-color: #2a2a40;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
            box_layout = QVBoxLayout()
            box_layout.addWidget(label)
            box_layout.addWidget(value)
            box.setLayout(box_layout)
            self.grid.addWidget(box, row // 2, row % 2)
            row += 1

        self.layout.addLayout(self.grid)
        self.setLayout(self.layout)

        # Update data every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(5000)
        self.update_data()

    def update_data(self):
        data = fake_data()
        for key in self.fields:
            value = data[key]
            self.labels[key].setText(f"{value} {self.units[key]}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = PowerMonitor()
    monitor.show()
    sys.exit(app.exec_())
