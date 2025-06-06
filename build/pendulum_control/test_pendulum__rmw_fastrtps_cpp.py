# generated from pendulum_control/test/test_pendulum_demo.py.in
# generated code does not contain a copyright notice

import os

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

    pendulum_logger_process = ExecuteProcess(
        cmd=['/home/colbren/ground-station/build/pendulum_control/pendulum_logger'],
        name='pendulum_logger',
        output='screen'
    )
    launch_description.add_action(pendulum_logger_process)

    pendulum_demo_process = ExecuteProcess(
        cmd=['/home/colbren/ground-station/build/pendulum_control/pendulum_demo', '-i', '1000'],
        name='pendulum_demo',
        output='screen'
    )
    launch_description.add_action(pendulum_demo_process)

    launch_description.add_action(
        launch_testing.actions.ReadyToTest()
    )
    return launch_description, locals()


class TestPendulumDemo(unittest.TestCase):

    def test_pendulum_logger_output(self, proc_output, pendulum_logger_process):
        """Test logger output against expectations."""
        proc_output.assertWaitFor(
            expected_output=launch_testing.tools.expected_output_from_file(
                path='/home/colbren/ground-station/src/demos/pendulum_control/test/pendulum_logger'
            ), process=pendulum_logger_process, timeout=10, stream='stdout'
        )

    def test_pendulum_demo_output(self, proc_output, pendulum_demo_process):
        """Test demo output against expectations."""
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
                path='/home/colbren/ground-station/src/demos/pendulum_control/test/pendulum_demo'
            ), process=pendulum_demo_process, output_filter=output_filter, timeout=15, stream='stdout'
        )
