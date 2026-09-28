# sam_bot_description

用于 ROS 2 Jazzy 的 Sam Bot 仿真包，包含机器人 SDF 模型、Gazebo 世界、里程计融合及 Nav2 配置。

## 依赖

- ROS 2 Jazzy、Gazebo Sim。
- `ros_gz_sim`：启动 Gazebo 并生成机器人；`ros_gz_bridge`：桥接 Gazebo 与 ROS 2 的话题。
- `robot_localization`：EKF 里程计融合；`sdformat_urdf`、`robot_state_publisher`：加载 SDF 并发布机器人 TF。
- `nav2_regulated_pure_pursuit_controller`：使用默认 Nav2 配置时需要。其余 ROS 依赖见 `package.xml`。

## 运行

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/CrescentRoseSAMA/sam_bot_description.git
cd ..
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --packages-select sam_bot_description --symlink-install
source install/setup.bash
ros2 launch sam_bot_description display.launch.py
```

首次使用 `rosdep` 时，先运行 `sudo rosdep init` 和 `rosdep update`。

`display.launch.py` 加载本包的 `world/baseline.sdf`（世界名 `nav_lab`），
并在 S 点附近生成机器人：模型原点为 `(-3.38, -2.7, 0.20)` 米，
初始朝向为 +X，`base_footprint` 的水平位置为 `(-3.5, -2.7)` 米。

`config/nav2_params.yaml` 是默认导航配置；`config/nav2_params_mppi.yaml` 保留 MPPI 配置。巡检场景需要另行安装 `nav_lab_scene` 包。

项目采用 Apache-2.0 许可证。
