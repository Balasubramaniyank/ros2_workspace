import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    

    urdf_file = os.path.join(
        get_package_share_directory('tortoisebot_lidar'),
        'urdf',
        'tortoisebot.urdf'
    )

   
    
    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim', '-r','empty.sdf'],
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
        output='screen'
    )

   
    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    
    bridge_scan = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
           
            '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
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