from ament_index_python import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
import os

def generate_launch_description():
    
    pkg_share = get_package_share_directory('tortoisebot_camera')

    use_sim_time = LaunchConfiguration('use_sim_time')

    
    default_slam_params_file = os.path.join(
        pkg_share, 
        'config', 
        'slam_toolbox_params.yaml'
    )

    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')    

    slam_params_file_arg = DeclareLaunchArgument(
        'slam_params_file',
        default_value=default_slam_params_file,
        description='Full path to the SLAM Toolbox parameters file to use',
    )
    
    slam_params_file = LaunchConfiguration('slam_params_file')

    slam_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('slam_toolbox'), 
                'launch', 
                'online_async_launch.py'
            )]),
            launch_arguments={
                # Mapping your declared argument to the one expected by slam_toolbox
                'slam_params_file': slam_params_file, 
                'use_sim_time': use_sim_time
            }.items(),
        )
    

    pointcloudtolaser=Node(
        package="pointcloud_to_laserscan",
        executable="pointcloud_to_laserscan_node",
        name="pcl2scan",
        remappings=[
                ("cloud", "/depth_camera/points"),
                ("scan", "/scan")
            ],
        parameters=[{
                "target_frame":"base_link",
                "min_height": -1.0,
                "max_height": 1.0,
                "range_min": 0.1,
                "range_max": 6.0,
                'use_sim_time': True,
            }]
    )

    octomap=Node(
        package='octomap_server',
        executable='octomap_server_node',
        name='octomap_server',
        output='screen',
        parameters=[{'frame_id': 'map'}],
        remappings=[('cloud_in', '/depth_camera/points')]
    )
     
    rviz=Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        
    ) 

    return LaunchDescription([
       
        declare_use_sim_time_argument,
         slam_params_file_arg,
         slam_launch,
        #  pointcloudtolaser,
         octomap,
         rviz,
     
        
    ])