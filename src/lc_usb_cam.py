#!/usr/bin/env python3

import rclpy
import time
import threading
from rclpy.lifecycle import LifecycleNode
from rclpy.lifecycle import State
from rclpy.lifecycle import TransitionCallbackReturn
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition, State

import subprocess

class USBCamLifecycleWrapper(LifecycleNode):
    def __init__(self, node_name='usb_cam_lifecycle_wrapper'):
        super().__init__(node_name)

        self._process = None

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Configuring the usb_cam node (starting external process).")

        # Example: Launch the usb_cam_node as a subprocess
        # Adjust as needed for your actual package/executable names or arguments.
        try:
            self._process = subprocess.Popen(
                ["ros2", "run", "usb_cam", "usb_cam_node_exe"],
                # optional: stdout=subprocess.PIPE, stderr=subprocess.PIPE
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )

            self._reader_thread = threading.Thread(target=print_stdout, args=(self._process.stdout,), daemon=True)
            self._reader_thread.start()
            self._poll_thread = threading.Thread(target=self._process.poll, daemon=True)
            self._poll_thread.start()
        except Exception as e:
            self.get_logger().error(f"Failed to launch usb_cam_node: {e}")
            return TransitionCallbackReturn.FAILURE

        self.get_logger().info("Configured successfully")
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Activating the usb_cam node.")
        # If needed, you could do more checks here, or send topics/params to the subprocess.
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Deactivating the usb_cam node.")
        # Optionally do something like pausing data flow, but keep the process alive.
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Cleaning up (shutting down the usb_cam process).")
        if self._process is not None:
            self._process.kill()
            self._process.wait()  # Wait for the process to fully exit
            self._process = None
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Shutting down wrapper node (final kill).")
        if self._process is not None:
            self._process.kill()
            self._process.wait()
            self._process = None
        return TransitionCallbackReturn.SUCCESS

    def on_error(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().error(f"Error state reached: {state.label}")
        return TransitionCallbackReturn.SUCCESS

    def process_poll_thread(self):
        while self._process is not None:
            ret = self._process.poll()
            if ret is not None:
                self.get_logger().info(f"usb_cam_node process exited with return code {ret}")
                self._process = None
                # need a different state transition depending on the current state
                self.get_logger().info(f'Current state: {self._state_machine.current_state[1]}')

                if self._state_machine.current_state[1] == 'active':
                    req = ChangeState.Request()
                    req.transition.id = Transition.TRANSITION_ACTIVE_SHUTDOWN

                break
            time.sleep(1.0)
        

def main(args=None):
    rclpy.init(args=args)
    wrapper_node = USBCamLifecycleWrapper()
    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(wrapper_node)

    # Spin until interrupted (Ctrl-C) or until another lifecycle transition kills us
    try:
        executor.spin()
    except KeyboardInterrupt:
        wrapper_node.get_logger().info("Keyboard interrupt - shutting down.")

    # Cleanup
    wrapper_node.destroy_node()
    rclpy.shutdown()

def print_stdout(pipe):
    if pipe is None:
        return
    for line in iter(pipe.readline, ''):
        print(f"[usb_cam_node] {line}", end='')

if __name__ == "__main__":
    main()
