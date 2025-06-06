# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import unittest
from unittest.case import SkipTest

from launch import LaunchDescription
from launch.actions import ExecuteProcess

import launch_testing
import launch_testing.actions
import launch_testing.asserts
import launch_testing_ros


def generate_test_description():
    launch_description = LaunchDescription()
    process_under_test = ExecuteProcess(
        cmd=['/home/colbren/ground-station/build/composition/linktime_composition'],
        name='test_linktime_composition',
        output='screen'
    )
    launch_description.add_action(process_under_test)
    launch_description.add_action(
        launch_testing.actions.ReadyToTest()
    )
    return launch_description, locals()


class TestComposition(unittest.TestCase):

    def test_linktime_composition(self, proc_output, process_under_test):
        """Test process' output against expectations."""
        if os.name == 'nt':
            print('The link time registration of classes does not work on Windows')
            raise SkipTest
        output_filter = launch_testing_ros.tools.basic_output_filter(
            filtered_rmw_implementation='rmw_fastrtps_cpp'
        )
        proc_output.assertWaitFor(
            expected_output=launch_testing.tools.expected_output_from_file(
                path='/home/colbren/ground-station/src/demos/composition/test/composition_all'
            ), process=process_under_test, output_filter=output_filter, timeout=10
        )
