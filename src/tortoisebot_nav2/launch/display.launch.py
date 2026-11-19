import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess,TimerAction


def generate_launch_description():


    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_nav2'),
        'urdf',
        'tortoisebot.urdf'
    )
    world_path = os.path.join(
        os.getenv('HOME'),
        'ros2_ws',
        'src',
        'tortoisebot_gazebo',
        'worlds',
        'custom_object_world2.sdf'
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
        arguments=['-topic', 'robot_description', '-name', 'xiaomi_gen1', '-x', '0', '-y', '-9', '-z', '0.4'],
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
       
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity,
        bridge,
         bridge1,
        rviz
        
        
        
       

    ])