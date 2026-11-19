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

                # # RTAB-Map arguments
                # 'rtabmap_args': '--delete_db_on_start',

                # # Topics
                # 'rgb_topic': '/burger/depth_camera/image',
                # 'depth_topic': '/burger/depth_camera/depth_image',
                # 'camera_info_topic': '/burger/depth_camera/camera_info',
                # 'odom_topic':'/burger/odom',
                # 'scan_topic':'/burger/scan',
               


                # # Frames
                # 'odom_frame_id': 'burger/odom',
                # 'frame_id': 'burger/base_footprint',
                # 'map_frame_id':'burger/map',

                # # Synchronization
                # 'approx_sync': 'true',

                # # Subscriptions
                # 'subscribe_scan': 'true',

                # # Grid parameters
                # 'Grid/3D': 'true',
                # 'Grid/CellSize': '0.05',
                # 'Grid/DepthDecimation': '4',

                # # Point cloud parameters
                # 'Cloud/VoxelSize': '0.05',
                # 'Cloud/NoiseFilteringRadius': '0.1',
                # 'Cloud/NoiseFilteringMinNeighbors': '5',

                # # Visual odometry
                # 'Vis/MinInliers': '10',

                # # RViz
                # 'rviz': 'true',

                # # namespace
                # 'namespace':'burger',
                # 'Grid/Sensor':'0',

                # # Simulation time
                # 'use_sim_time': 'true',


    'rtabmap_args': '--delete_db_on_start',

    # Topics
    'rgb_topic': '/burger/depth_camera/image',
    'depth_topic': '/burger/depth_camera/depth_image',
    'camera_info_topic': '/burger/depth_camera/camera_info',
    'scan_topic': '/burger/scan',
    'odom_topic': '/burger/odom',

    # Frames
    'frame_id': 'burger/base_footprint',
    'odom_frame_id': 'burger/odom',
    'map_frame_id': 'burger/map',

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

    # Namespace
    'namespace': 'burger',

    'use_sim_time': 'true',  

            }.items()
        )
    ])
