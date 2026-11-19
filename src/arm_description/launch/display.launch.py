from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess ,TimerAction,SetEnvironmentVariable
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import AppendEnvironmentVariable
import os
import xacro


def generate_launch_description():
    

    set_plugin_path = AppendEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value='/opt/ros/jazzy/lib'
    )
        
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("arm_description"), "urdf", "arm.urdf.xacro"]
            ),
        ]
    )

    robot_description = {"robot_description": robot_description_content}
    pkg_description = get_package_share_directory('arm_description')

    urdf_file = os.path.join(pkg_description, 'urdf', 'arm.urdf')
   
    gazebo_launch = ExecuteProcess(
            cmd=['gz', 'sim','-r','empty.sdf'],
            output='screen'
        )

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description,{'use_sim_time':True}],
        output="screen",    
    )
      
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'arm', '-x', '-2', '-y', '0', '-z', '0.05'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    rviz2= Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]

    )
    
    jointState= Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        # parameters=[{'use_sim_time': True}]

    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[  
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',    
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # 1. Joint State Broadcaster
    joint_state_broadcaster = TimerAction(
        period=1.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster'],
                output='screen',
                parameters=[{'use_sim_time': True}],
            )
        ]
    )

    # 2. Arm Controller
    arm_controller = TimerAction(
        period=1.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['arm_controller'],
                output='screen',
                parameters=[{'use_sim_time': True}],
            )
        ]
    )

    # 3. Gripper Controller
    gripper_controller = TimerAction(
        period=1.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['gripper_controller'],
                output='screen',
                parameters=[{'use_sim_time': True}],
            )
        ]
    )

    return LaunchDescription([            
   
    # robot_state_publisher_node,
    set_plugin_path,
    gazebo_launch,
    node_robot_state_publisher,
    spawn_entity,
    # jointState,
    bridge,
    rviz2,
    joint_state_broadcaster,
    arm_controller,
    # gripper_controller,

    ]
    )