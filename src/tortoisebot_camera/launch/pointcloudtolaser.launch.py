from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    pcl_to_laser = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[
            {"use_sim_time": True},
            {"target_frame": "base_link"},
            {"min_height": -1.0},
            {"max_height": 1.0}
        ],
        remappings=[
            ("cloud_in", "/depth_camera/points"),
            ("scan", "/scan")
        ]
    )

    return LaunchDescription([
        pcl_to_laser
    ])
