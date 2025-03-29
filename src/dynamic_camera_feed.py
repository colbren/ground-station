import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Robot Control Page")  # Window title
        self.setGeometry(100, 100, 900, 600)  # Window size

        self.MainLayout = QHBoxLayout()  # Main Horizontal Layout

        # Left Layout (Video Feed + Buttons)
        self.LeftLayout = QVBoxLayout()

        # Title Label
        self.TitleLabel = QLabel("Robot Control Page")
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setFont(QFont("Arial", 20, QFont.Bold))
        self.LeftLayout.addWidget(self.TitleLabel)

        self.FeedLabel = QLabel()
        self.LeftLayout.addWidget(self.FeedLabel)

        self.CameraSelect = QComboBox()
        self.CameraIndexes = [4, 0, 2]
        self.CameraSelect.addItems(["Camera 1", "Camera 2", "Camera 3"])
        self.LeftLayout.addWidget(self.CameraSelect)

        self.StartBTN = QPushButton("Start")
        self.StartBTN.clicked.connect(self.StartFeed)
        self.LeftLayout.addWidget(self.StartBTN)

        self.CancelBTN = QPushButton("Stop")
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.LeftLayout.addWidget(self.CancelBTN)

        # Right Layout (Soil Data)
        self.RightLayout = QVBoxLayout()
        self.SoilTitle = QLabel("Soil Data")
        self.SoilTitle.setFont(QFont("Arial", 18, QFont.Bold))
        self.SoilTitle.setAlignment(Qt.AlignCenter)
        self.RightLayout.addWidget(self.SoilTitle)

        # Horizontal Layout for Temperature and Humidity Side by Side
        self.SensorLayout = QHBoxLayout()

        self.TemperatureLabel = QLabel("Temperature")
        self.TemperatureLabel.setFont(QFont("Arial", 14))
        self.SensorLayout.addWidget(self.TemperatureLabel)

        self.HumidityLabel = QLabel("Humidity")
        self.HumidityLabel.setFont(QFont("Arial", 14))
        self.SensorLayout.addWidget(self.HumidityLabel)

        self.RightLayout.addLayout(self.SensorLayout)  # Add horizontal layout to right layout

        # Add layouts to the main layout
        self.MainLayout.addLayout(self.LeftLayout, 2)  # 2/3 space for video
        self.MainLayout.addLayout(self.RightLayout, 1)  # 1/3 space for data

        self.Worker1 = Worker1()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)

        self.setLayout(self.MainLayout)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def StartFeed(self):
        if not self.Worker1.ThreadActive:
            selected_index = self.CameraSelect.currentIndex()
            camera_index = self.CameraIndexes[selected_index]
            self.Worker1.setCamera(camera_index)
            self.Worker1.start()

    def CancelFeed(self):
        self.Worker1.stop()

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.ThreadActive = False
        self.CameraIndex = 0

    def setCamera(self, index):
        self.CameraIndex = index

    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(self.CameraIndex)
        if not Capture.isOpened():
            print(f"Camera {self.CameraIndex} could not be opened")
            self.ThreadActive = False
            return

        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)

        Capture.release()

    def stop(self):
        self.ThreadActive = False
        self.quit()
        self.wait()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())
