# generated from intra_process_demo/test/test_executables_demo.py.in
# generated code does not contain a copyright notice

import unittest

from launch import LaunchDescription
from launch.actions import ExecuteProcess

import launch_testing
import launch_testing.actions
import launch_testing.asserts


def generate_test_description():
    launch_description = LaunchDescription()
    processes_under_test = [
        ExecuteProcess(
            cmd=[executable, 'test_executable'],
            name='test_executable_' + str(i),
            output='screen'
        ) for i, executable in enumerate('/home/colbren/ground-station/build/intra_process_demo/cyclic_pipeline'.split(';'))
    ]
    for process in processes_under_test:
        launch_description.add_action(process)
    launch_description.add_action(
        launch_testing.actions.ReadyToTest()
    )
    return launch_description, locals()


class TestExecutablesDemo(unittest.TestCase):

    def test_executables_output(self, proc_output, processes_under_test):
        """Test all processes output against expectations."""
        output_files = '/home/colbren/ground-station/src/demos/intra_process_demo/test/cyclic_pipeline'.split(';')
        for process, output_file in zip(processes_under_test, output_files):
            proc_output.assertWaitFor(
                expected_output=launch_testing.tools.expected_output_from_file(
                    path=output_file
                ), process=process, stream='stdout'
            )
