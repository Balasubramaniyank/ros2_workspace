from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess ,TimerAction
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
        'tortoisebot_gazebo',
        'worlds',
        'custom_object_world2.sdf'
    )
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'),
        'urdf',
        'tortoisebot.urdf'
    )
      
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    default_slam_params_file = os.path.join(
        get_package_share_directory('tortoisebot_gazebo'), 
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
        arguments=['-topic', 'robot_description', '-name', 'tortoisebot', '-x', '0', '-y', '0', '-z', '0.3'],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
           
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    bridge2 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
         
            '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan', 
        ],
        parameters=[{'qos.queue_size': 100}],
        output='screen',
    )

    bridge3 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
           '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
           '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',

        ],
        parameters=[{'qos.queue_size': 100}],
        output='screen',
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
        bridge2,
        bridge,
        bridge3,
        declare_use_sim_time_argument,
        slam_params_file_arg,
        slam_launch,
        TimerAction(period=7.0, actions=[rviz])
        
        
    ])
