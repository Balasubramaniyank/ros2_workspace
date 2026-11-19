
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    cleaning_robot = Node(
        package='tortoisebot_cleaning',
        executable='zigzag',
        name='cleaning_robot',
        output='screen',
        # parameters=[{
        #     'auto_start': True,
        #     'room_width': 4.0,
        #     'room_height': 4.0,
        #     'pass_spacing': 0.4,
        #     'pause_duration': 2.0,
        #     'home_x': 0.5,
        #     'home_y': 0.0,       
        #  }]
    )
    
    return LaunchDescription([
         
         cleaning_robot,

    ])
