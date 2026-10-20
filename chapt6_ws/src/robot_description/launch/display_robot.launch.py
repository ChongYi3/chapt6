import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('robot_description')
    default_model_path = os.path.join(
        pkg_share, 'urdf', 'fishbot', 'fishbot.urdf.xacro')
    default_rviz_config = os.path.join(
        pkg_share, 'config', 'display_robot.rviz')

    declare_model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model_path,
        description='URDF/xacro 模型文件路径')

    declare_rviz_config_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=default_rviz_config,
        description='RViz 配置文件路径')

    robot_description_content = Command(
        ['xacro ', LaunchConfiguration('model')])

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen')

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        output='screen')

    return LaunchDescription([
        declare_model_arg,
        declare_rviz_config_arg,
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz2_node,
    ])
