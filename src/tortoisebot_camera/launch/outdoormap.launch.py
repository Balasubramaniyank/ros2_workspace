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
                'args': '--delete_db_on_start '
                        '--Vis/MaxFeatures 0 '
                        '--Kp/MaxFeatures 0 '
                        '--Reg/Strategy 1 '
                        '--Icp/VoxelSize 0.1 '
                        '--Icp/MaxCorrespondenceDistance 1.0 '
                        # '--RGBD/LinearUpdate 0.01 '
                        # '--RGBD/AngularUpdate 0.01 '
                        '--RGBD/ProximityBySpace true '
                        '--Mem/STMSize 30 '
                        '--Rtabmap/TimeThr 700 '
                        # '--map_always_update true '
                        '--Grid/3D true '
                        '--Grid/FromDepth false '           # ← use lidar not depth camera
                        '--Grid/MaxGroundHeight 0.1 '
                        '--Grid/MaxObstacleHeight 2.0 '
                        '--Mem/IncrementalMemory true '
                        '--Mem/InitWMWithAllNodes true '
                        '--Rtabmap/CreateIntermediateNodes false '
                        '--RGBD/OptimizeFromGraphEnd false '      # avoid full graph re-optimization each time
                        '--RGBD/OptimizeMaxError 1.0 '
                        '--Grid/CellSize 0.1 '                     # coarser grid = faster cloud regen
                        '--Rtabmap/DetectionRate 1.0',
                                
                'depth': 'false',
                'subscribe_depth': 'false',
                'subscribe_rgb': 'false',
                'subscribe_rgbd': 'false',
                'visual_odometry': 'false',
                'rtabmap_viz': 'false',
                'subscribe_scan_cloud': 'true',
                'scan_cloud_topic': '/scan/points',
                'Odom/GuessMotion': 'true',
                'guess_frame_id': 'odom',
                'Icp/MaxCorrespondenceDistance': '1.0',
                'Icp/MaxTranslation': "5.0",             
                'RGBD/LinearUpdate': "0.3",             
                'RGBD/AngularUpdate': "0.3",
                'approx_sync_max_interval':'0.1',
                'Icp/VoxelSize': '0.1',
                'Odom/ResetCountdown': '1', 
                'icp_odometry': 'false',
                'frame_id': 'base_footprint',
                'odom_frame_id': 'odom',
                'map_frame_id': 'map',
                'approx_sync': 'true',
                'use_sim_time': 'true',
                'Reg/Strategy': '1',
                # 'Grid/3D': 'true',
                'Grid/sensor': '2',
                'Cloud/Assemble': 'true',
                'Cloud/AssembleOnLoopClosure': 'true',
                'publish_cloud_map': 'true',
                'rviz': 'true',
                # 'Odom/ScanKeyFrameThr': '0.6',
                # 'OdomF2M/MaxSize': '1000',
                'map_always_update': 'true',
                'cloud_output_voxel_size':'0.05',

            }.items()
        )
    ])
