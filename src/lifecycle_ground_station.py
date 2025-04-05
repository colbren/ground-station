import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QGroupBox
from PyQt5.QtCore import QProcess, QTimer


class NodeController(QWidget):
    def __init__(self, node_name):
        super().__init__()
        self.node_name = node_name
        self.process = None

        layout = QVBoxLayout()

        self.label = QLabel(f"Node: {self.node_name}")
        layout.addWidget(self.label)

        self.lifecycle_label = QLabel("Lifecycle State: Unknown")
        layout.addWidget(self.lifecycle_label)

        self.start_button = QPushButton("Start Node")
        self.start_button.clicked.connect(self.start_node)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Node")
        self.stop_button.clicked.connect(self.stop_node)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Timer to update the lifecycle state every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_lifecycle_status)
        self.timer.start(1000)

    def start_node(self):
        self.process = QProcess(self)
        self.process.start("ros2", ["lifecycle", "set", self.node_name, "configure"])
        self.process.waitForFinished()
        self.process.start("ros2", ["lifecycle", "set", self.node_name, "activate"])
        self.process.waitForFinished()

    def stop_node(self):
        if self.process:
            stop_process = QProcess(self)
            stop_process.start("ros2", ["lifecycle", "set", self.node_name, "deactivate"])
            stop_process.waitForFinished()
            stop_process.start("ros2", ["lifecycle", "set", self.node_name, "cleanup"])
            stop_process.waitForFinished()
        
    def update_lifecycle_status(self):
        # Create the QProcess to execute the command asynchronously
        process = QProcess(self)
        # Connect the finished signal to a custom slot for handling the output
        process.finished.connect(lambda: self.handle_lifecycle_output(process))
        # Start the process
        process.start("ros2", ["lifecycle", "get", self.node_name])

    def handle_lifecycle_output(self, process):
        # Read the output of the command
        output = process.readAllStandardOutput().data().decode().strip()

        # Determine the lifecycle state based on the output
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

        # Update the label with the lifecycle state
        self.lifecycle_label.setText(f"Lifecycle State: {state}")


class ROSNodeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.node_controllers = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.launch_button = QPushButton("Launch Nodes from Launch File")
        self.launch_button.clicked.connect(self.launch_nodes)
        layout.addWidget(self.launch_button)

        self.node_group = QVBoxLayout()
        node_group_widget = QWidget()
        node_group_widget.setLayout(self.node_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(node_group_widget)

        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.setWindowTitle("ROS 2 Node Lifecycle Manager")

    def launch_nodes(self):
        # Launch your full launch file
        launch_process = QProcess(self)

        # Launch file to launch all nodes
        launch_process.start("ros2", ["run", "lifecycle_py", "lifecycle_talker"])

        # Add NodeController widgets for expected nodes
        for node_name in ["/lc_talker"]:  # Add more node names as needed
            controller = NodeController(node_name)
            self.node_controllers.append(controller)
            self.node_group.addWidget(controller)

    def closeEvent(self, event):
        # Shutdown all nodes when the window is closed
        for controller in self.node_controllers:
            controller.stop_node()  # Ensure all nodes are stopped properly
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROSNodeManager()       
    window.show()
    sys.exit(app.exec_())
