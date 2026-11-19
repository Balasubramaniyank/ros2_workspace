from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter   # <--- 1. NEW IMPORT
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    rtabmap_launch_dir = os.path.join(
        get_package_share_directory('rtabmap_launch'),
        'launch'
    )

    return LaunchDescription([
        
        # <--- 2. FORCE NODE PARAMETERS HERE
        SetParameter(name='map_always_update', value=True),
        SetParameter(name='cloud_output_voxel_size', value=0.02),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(rtabmap_launch_dir, 'rtabmap.launch.py')
            ),
            launch_arguments={
                'args': '--delete_db_on_start '
                        '--Vis/MaxFeatures 0 '
                        '--Kp/MaxFeatures 0 '
                        '--Reg/Strategy 1 '
                        '--Icp/VoxelSize 0.1 '
                        '--Icp/MaxCorrespondenceDistance 1.0 '
                        '--Icp/PointToPlane false '
                        '--Icp/PointToPlanek 10 '
                        '--Icp/PointToPlaneRadius 0.2 '
                        '--RGBD/ProximityBySpace true '
                        '--Mem/STMSize 30 '
                        '--Mem/IncrementalMemory true '
                        '--Mem/InitWMWithAllNodes true '
                        '--Grid/3D true '
                        '--Grid/FromDepth false '
                        '--Grid/MaxGroundHeight 0.1 '
                        '--Grid/MaxObstacleHeight 2.0 '
                        '--Grid/CellSize 0.1 '
                        '--Rtabmap/CreateIntermediateNodes false '
                        '--RGBD/OptimizeFromGraphEnd false '
                        '--RGBD/OptimizeMaxError 1.0 '
                        '--Rtabmap/DetectionRate 1.0 '
                        '--Rtabmap/TimeThr 700',

                'depth':               'false',
                'subscribe_depth':     'false',
                'subscribe_rgb':       'false',
                'subscribe_rgbd':      'false',
                'visual_odometry':     'false',
                'icp_odometry':        'false',
                'rtabmap_viz':         'false',

                'subscribe_scan_cloud': 'true',
                'scan_cloud_topic':     '/scan/points',

                'frame_id':      'base_link',
                'odom_frame_id': 'odom',
                'map_frame_id':  'map',

                'approx_sync':              'true',
                'approx_sync_max_interval': '0.1',
                'use_sim_time':             'true',

                'guess_frame_id':    'odom',
                'Odom/GuessMotion':  'true',
                'Odom/ResetCountdown': '1',

                'rviz': 'true',
            }.items()
        )
    ])