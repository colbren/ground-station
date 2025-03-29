import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QProcess, QTimer


class ROSNodeController(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("ROS Node: example_lifecycle")
        layout.addWidget(self.label)

        self.lifecycle_label = QLabel("Lifecycle State: Unknown")
        layout.addWidget(self.lifecycle_label)

        self.start_button = QPushButton("Start Lifecycle Node")
        self.start_button.clicked.connect(self.start_lifecycle_node)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Lifecycle Node")
        self.stop_button.clicked.connect(self.stop_lifecycle_node)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.setWindowTitle("ROS 2 Node Lifecycle Controller")

        # Timer to update the lifecycle state every 1 second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_lifecycle_status)
        self.timer.start(1000)  # Update every 1 second

    def start_lifecycle_node(self):
        if self.process is None:
            self.process = QProcess(self)
            self.process.start("ros2", ["run", "demo_nodes_cpp", "talker"])
            self.process.waitForStarted()  # Wait until the process starts

            # Check if the process is running
            if self.process.state() == QProcess.Running:
                self.label.setText("Lifecycle Node Running")
            else:
                self.label.setText("Failed to Start Lifecycle Node")
        else:
            self.label.setText("Lifecycle Node Already Running")

    def stop_lifecycle_node(self):
        if self.process:
            stop_process = QProcess(self)
            stop_process.start("ros2", ["lifecycle", "set", "/talker", "shutdown"])
            stop_process.waitForFinished()  # Ensure process finishes

            # Check if the process has finished
            self.process = None
            self.label.setText("Lifecycle Node Stopped")
        else:
            self.label.setText("Lifecycle Node Not Running")

    def update_lifecycle_status(self):
        """ Queries the lifecycle state of the example_lifecycle node every second and updates the UI """
        process = QProcess(self)
        process.start("ros2", ["lifecycle", "get", "/talker"])
        process.waitForFinished()
        output = process.readAllStandardOutput().data().decode().strip()

        # Extract the state from the output
        if "unconfigured" in output:
            state = "Unconfigured"
        elif "inactive" in output:
            state = "Inactive"
        elif "active" in output:
            state = "Active"
        elif "finalized" in output:
            state = "Finalized"
        else:
            state = "Unknown"

        self.lifecycle_label.setText(f"Lifecycle State: {state}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROSNodeController()
    window.show()
    sys.exit(app.exec_())
