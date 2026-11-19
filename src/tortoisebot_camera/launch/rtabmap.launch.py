from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    rtabmap_launch_dir = os.path.join(
        get_package_share_directory('rtabmap_launch'),
        'launch'
    )

    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(rtabmap_launch_dir, 'rtabmap.launch.py')
            ),
            launch_arguments={

    'rtabmap_args': '--delete_db_on_start',

    # Topics
    'rgb_topic': '/depth_camera/image',
    'depth_topic': '/depth_camera/depth_image',
    'camera_info_topic': '/depth_camera/camera_info',
    'scan_topic': '/scan',
    'odom_topic': '/odom',

    # Frames
    'frame_id': 'base_footprint',
    'odom_frame_id': 'odom',
    'map_frame_id': 'map',

    # Sync
    'approx_sync': 'false',

    # Subscriptions
    'subscribe_scan': 'false',
    'subscribe_scan_cloud': 'false',

    # 3D GRID
    'Grid/3D': 'true',
    'Grid/sensor':'1',

    # 3D CLOUD MAP (THIS IS THE FIX)
    'Cloud/Assemble': 'true',
    'Cloud/AssembleOnLoopClosure': 'true',
    'publish_cloud_map': 'true',
    'Cloud/MaxDepth': '6.0',
    'Cloud/VoxelSize': '0.05',

    # RViz
    'rviz': 'true',

    'use_sim_time': 'true',  

            }.items()
        )
    ])
