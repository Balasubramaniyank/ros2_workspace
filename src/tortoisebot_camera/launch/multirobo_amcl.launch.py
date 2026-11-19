import os
from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg = get_package_share_directory('tortoisebot_camera')
    amcl_yaml = os.path.join(pkg, 'config', 'amcl.yaml')
    map_yaml  ='/home/arz-1028/ros2_ws/amcl.map.yaml'

    def robot_group(ns):
        return GroupAction([
            PushRosNamespace(ns),

            Node(
                package='nav2_map_server',
                executable='map_server',
                name='map_server',
                parameters=[{
                    'yaml_filename': map_yaml,
                    'use_sim_time': True
                }]
            ),

            Node(
                package='nav2_amcl',
                executable='amcl',
                name='amcl',
                parameters=[amcl_yaml]
            ),

            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_localization',
                parameters=[{
                    'autostart': True,
                    'use_sim_time':True,
                    'node_names': ['map_server', 'amcl']
                }]
            ),
        ])

    return LaunchDescription([
        robot_group('burger'),
        # robot_group('waffle'),
    ])
