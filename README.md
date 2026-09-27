# sam_bot_description

用于 ROS 2 Jazzy 的 Sam Bot 仿真包，包含机器人 SDF 模型、Gazebo 世界、里程计融合及 Nav2 配置。

## 运行

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/CrescentRoseSAMA/sam_bot_description.git
cd ..
source /opt/ros/jazzy/setup.bash
colcon build --packages-select sam_bot_description --symlink-install
source install/setup.bash
ros2 launch sam_bot_description display.launch.py
```

`config/nav2_params.yaml` 是默认导航配置；`config/nav2_params_mppi.yaml` 保留 MPPI 配置。巡检场景需要另行安装 `nav_lab_scene` 包。

项目采用 Apache-2.0 许可证。
