from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess ,TimerAction,SetEnvironmentVariable
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():
    world_path = os.path.join(
        os.getenv('HOME'),
        'ros2_ws',
        'src',
        'tortoisebot_cleaning',
        'world',
        'myWorld.sdf'
    )


    # world_path = os.path.join(
    #     os.getenv('HOME'),
    #     'ros2_ws',
    #     'src',
    #     'tortoisebot_gazebo',
    #     'worlds',
    #     'custom_object_world2.sdf'
    # )
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_cleaning'),
        'urdf',
        'tortoisebot.urdf'
    )


    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value="/home/arz-1028/ros2_ws/src"
    )
    
    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim','-r',world_path],
        output='screen'
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'use_sim_time': True}],
        arguments=[urdf_file],
        output='screen'
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'tortoisebot', '-x', '0', '-y', '0', '-z', '0.7'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',

        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    bridge1 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/depth_camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            'depth_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/depth_camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    rviz=Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ) 




    return LaunchDescription([
       
       gazebo_resource_path,
       gazebo_launch,
       robot_state_publisher_node,
       spawn_entity ,
       bridge,
       bridge1,
       rviz,




    ])


