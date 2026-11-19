import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from tortoisebot_lidar import lidar_subscriber

def generate_launch_description():
  
    pkg_gazebo_sim = get_package_share_directory('ball_follow')
   
    
    world_file = os.path.join(pkg_gazebo_sim, 'worlds', 'red_ball_world.sdf')
   
    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_lidar'),
        'urdf',
        'tortoisebot.urdf'
    )
    
  
   
    gazebo_launch = ExecuteProcess(
            cmd=['gz', 'sim','-r', world_file],
            output='screen'
    )
   
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'use_sim_time': True}],
        arguments=[urdf_file],
        output='screen'
    )
    
    joint_state_publisher= Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher',
        output='screen'
    )


  
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'tortoisebot', '-x', '0', '-y', '0', '-z', '0.9'],
        output='screen'
    )
  
    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Maps ROS 2 /cmd_vel (Twist) to Gazebo's internal topic (Twist)
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # 6. Define the Bridge Node for /scan
    bridge_scan = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',

        ],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )
    
   

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity,
        bridge_cmd_vel,
        bridge_scan,
        
    ])