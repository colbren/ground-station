# generated from pendulum_control/test/test_pendulum_teleop.py.in
# generated code does not contain a copyright notice

import os
import sys

import unittest

from launch import LaunchDescription
from launch.actions import ExecuteProcess

import launch_testing
import launch_testing.actions
import launch_testing.asserts
import launch_testing_ros


def generate_test_description():
    os.environ['OSPL_VERBOSITY'] = '8'  # 8 = OS_NONE
    # bare minimum formatting for console output matching
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '{message}'

    launch_description = LaunchDescription()
    pendulum_demo_process = ExecuteProcess(
        cmd=['/home/colbren/ground-station/build/pendulum_control/pendulum_demo', '-i', '0'],
        name='pendulum_demo',
        output='screen'
    )
    launch_description.add_action(pendulum_demo_process)

    execute_with_delay_command = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'execute_with_delay.py')

    pendulum_teleop_process = ExecuteProcess(
        cmd=[sys.executable, execute_with_delay_command, '500',
             '/home/colbren/ground-station/build/pendulum_control/pendulum_teleop', '100'],
        name='pendulum_teleop',
        output='screen'
    )
    launch_description.add_action(pendulum_teleop_process)

    launch_description.add_action(
        launch_testing.actions.ReadyToTest()
    )
    return launch_description, locals()


class TestPendulumTeleop(unittest.TestCase):

    def test_pendulum_demo_output(self, proc_output, pendulum_demo_process):
        """Test demo output against expectations."""
        proc_output.assertWaitFor(
            expected_output=launch_testing.tools.expected_output_from_file(
                path='/home/colbren/ground-station/src/demos/pendulum_control/test/pendulum_demo_teleop'
            ), process=pendulum_demo_process, timeout=10, stream='stdout'
        )

    def test_pendulum_teleop_output(self, proc_output, pendulum_teleop_process):
        """Test teleop output against expectations."""
        rmw_implementation = 'rmw_fastrtps_cpp'
        from launch_testing.tools.output import get_default_filtered_prefixes
        filtered_prefixes = get_default_filtered_prefixes()
        if rmw_implementation.startswith('rmw_connext'):
            # This output can be caused by a small QoS depth leading to samples being discarded.
            # Since we are optimizing for performance with a depth of 1, we can ignore it.
            filtered_prefixes.append(
                'PRESWriterHistoryDriver_completeBeAsynchPub:!make_sample_reclaimable'
            )
        output_filter = launch_testing_ros.tools.basic_output_filter(
            filtered_prefixes=filtered_prefixes,
            filtered_rmw_implementation=rmw_implementation
        )
        proc_output.assertWaitFor(
            expected_output=launch_testing.tools.expected_output_from_file(
                path='/home/colbren/ground-station/src/demos/pendulum_control/test/pendulum_teleop'
            ), process=pendulum_teleop_process, output_filter=output_filter, timeout=10, stream='stdout'
        )
