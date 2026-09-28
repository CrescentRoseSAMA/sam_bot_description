import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('sam_bot_description')
    nav2_share = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_gazebo = LaunchConfiguration('start_gazebo')
    map_path = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    nav2_rviz_config = os.path.join(nav2_share, 'rviz', 'nav2_default_view.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use the Gazebo simulation clock',
        ),
        DeclareLaunchArgument(
            'start_gazebo', default_value='true',
            description='Start Gazebo, the robot, bridges, and localization',
        ),
        DeclareLaunchArgument(
            'map', default_value=os.path.join(package_share, 'maps', 'nav_lab.yaml'),
            description='Full path to the map YAML file',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(package_share, 'config', 'nav2_params.yaml'),
            description='Full path to the Nav2 parameters file',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(package_share, 'launch', 'display.launch.py')
            ),
            condition=IfCondition(start_gazebo),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'rvizconfig': nav2_rviz_config,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_share, 'launch', 'bringup_launch.py')
            ),
            launch_arguments={
                'map': map_path,
                'use_sim_time': use_sim_time,
                'params_file': params_file,
            }.items(),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            condition=UnlessCondition(start_gazebo),
            arguments=['-d', nav2_rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ])
