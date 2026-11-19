import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import ExecuteProcess

def generate_launch_description():
    urdf_file_name = 'ugv_robot.urdf.xacro'
    urdf_path = os.path.join(
        get_package_share_directory('tortoisebot_camera'),
        'urdf',
        urdf_file_name
    )
    rviz_config_path = os.path.join(
        get_package_share_directory('tortoisebot_camera'),
        'rviz',
        'display.rviz'
    )

    gazebo_launch = ExecuteProcess(
            cmd=['gz', 'sim','-r','empty.sdf'],
            output='screen'
    )

    robot_description_content = Command(['xacro ', urdf_path])

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': ParameterValue(robot_description_content, value_type=str)}]
    )

    # Joint State Publisher GUI
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'robot_description': ParameterValue(robot_description_content, value_type=str)}]
    )
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'ugv_robot', '-x', '0', '-y', '0', '-z', '0.9'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )


    # Launch Description
    ld = LaunchDescription()
    ld.add_action(gazebo_launch)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_gui_node) # Make sure this is the GUI node
    ld.add_action(rviz_node)
    ld.add_action(spawn_entity)

    return ld