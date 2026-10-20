import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('robot_description')
    default_model_path = os.path.join(
        pkg_share, 'urdf', 'fishbot', 'fishbot.urdf.xacro')
    default_world_path = os.path.join(
        pkg_share, 'world', 'custom_room.world')

    gazebo_launch = os.path.join(
        get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')

    declare_model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model_path,
        description='URDF/xacro 模型文件路径')

    declare_world_arg = DeclareLaunchArgument(
        name='world',
        default_value=default_world_path,
        description='Gazebo 世界文件路径')

    robot_description_content = Command(
        ['xacro ', LaunchConfiguration('model')])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={'world': LaunchConfiguration('world')}.items())

    # 等 Gazebo 启动后再把机器人从 robot_description 话题生成进去。
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'fishbot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15',
        ],
        output='screen')

    action_load_joint_state_controller = ExecuteProcess(
        cmd=[
            'ros2', 'control', 'load_controller',
            'fishbot_joint_state_broadcaster', '--set-state', 'active',
        ],
        output='screen',
    )



    action_load_diff_driver_controller = ExecuteProcess(
            cmd=[
                'ros2', 'control', 'load_controller',
                'fishbot_diff_drive_controller', '--set-state', 'active',
            ],
            output='screen',
        )
    

    return LaunchDescription([
        declare_model_arg,
        declare_world_arg,
        robot_state_publisher_node,
        gazebo,
        TimerAction(period=3.0, actions=[spawn_robot]),
        TimerAction(period=5.0, actions=[action_load_joint_state_controller]),
        TimerAction(period=6.0, actions=[action_load_diff_driver_controller]),
    ])
