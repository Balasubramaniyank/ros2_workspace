import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():



    world_path = os.path.join(
        os.getenv('HOME'),
        'ros2_ws',
        'src',
        'tortoisebot_pkg',
        'worlds',
        'empty.sdf'
    )
  
    pkg_description = get_package_share_directory('tortoisebot_pkg')
    

    # 1. Paths
    urdf_file = os.path.join(pkg_description, 'urdf', 'robotic_arm.urdf')
    
    
    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_path],
        output='screen'
    )
    # 3. Robot State Publisher (needed to publish transforms)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'use_sim_time': True}],
        arguments=[urdf_file],
        output='screen'
    )

    # 4. Spawn the Robot entity into the Gazebo world
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'roboticArm', '-x', '0', '-y', '0', '-z', '0.10'],
        output='screen'
    )

    # 5. Define the Bridge Node
    bridge_cmd_vel = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Maps ROS 2 /cmd_vel (Twist) to Gazebo's internal topic (Twist)
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            # '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    jointState= Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',

    )

    rviz=Node(
        package='rviz2',
        executable='rviz2',
        output='screen'

    )



    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity,
        bridge_cmd_vel,
        jointState,
        rviz,
    ])