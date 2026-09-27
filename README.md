# sam_bot_description：二维导航基线

## 当前入口

- `ros2 launch sam_bot_description display.launch.py`：原始简单世界、机器人、EKF 与 RViz。
- `ros2 launch nav_lab_scene scene.launch.py rviz:=true`：巡检实验场景，关闭深度相机，保留二维导航传感器。
- 两个入口均加载 **SDF**。旧 `.urdf` 已修复链接内元素结构、删除 Classic 插件，只作早期简化显示模型，不包含完整激光/相机仿真，不应通过 model 参数替换 SDF 来做导航。

## 2026-09-27 修正

1. 差速轮距由 0.4 改为表达式 `base_width + 2*wheel_ygap`，实际为 0.36 米。轮半径 0.1 米。
2. 15 kg 车身惯性放回 base_link；修正盒体惯性轴和竖直激光圆柱的惯性朝向。base_footprint 只有用于数值计算的 1e-6 kg，无几何碰撞体。
3. base_footprint 位于驱动轮轴中点的地面投影，车身 base_link 在它前方 0.12 米、上方 0.15 米。SDF 模型原点仍在车身中心，canonical_link 改为树根 base_footprint 以满足 sdformat_urdf。巡检场景启动器补偿生成位置，使 S 点与 base_footprint 对齐。
4. EKF 使用 two_d_mode=true，以 base_footprint 为运动参考。删除用 z=0.15 初值维持车身高度的做法，高度由固定 TF 表达。
5. Gazebo、MPPI、速度平滑器统一：前进上限 0.30 m/s，后退上限 0.15 m/s，角速度 1.0 rad/s；线加减速度 0.5 m/s²，角加减速度 1.5 rad/s²。关闭 MPPI 轨迹可视化。
6. Nav2 使用 /odometry/filtered 和 base_footprint；局部与全局代价地图使用相同矩形 footprint：x∈[-0.11,0.35]、y∈[-0.21,0.21] 米，覆盖车轮、车身与前相机。
7. 声明 sdformat_urdf、rclpy、nav_msgs、ament_index_python 运行依赖；原始生成高度从 0.65 降至 0.20 米，减小落地冲击。
8. 删除 SDF 相机中遗留的非标准 Classic 参数。gz_frame_id 是传感器桥接所需扩展，保留它；解析器的相关警告不代表传感器故障。

## TF 与里程计

```text
map                   SLAM 或 AMCL
 └─ odom
     └─ base_footprint EKF，z=0，轮轴地面投影
         └─ base_link  固定 TF：x=0.12、z=0.15
             ├─ drivewhl_l_link / drivewhl_r_link
             ├─ front_caster
             ├─ imu_link
             ├─ lidar_link
             └─ camera_link
```

Gazebo /tf 不桥接到 ROS，避免重复发布定位 TF。

Gazebo /demo/odom 的速度协方差全零。新增 odom_covariance.py 将其转发到 /demo/odom_with_covariance，仅当速度协方差矩阵全零时填入可配置方差，保留时间戳、坐标系、位姿和速度。若输入已含非零协方差，则保留原矩阵。

默认速度方差按 [vx,vy,vz,roll_rate,pitch_rate,yaw_rate] 为 `[0.0004,0.0001,1,1,1,0.0009]`，单位为对应 SI 单位的平方。它们是仿真初始假设，**不是实测标定值**。EKF 只融合轮速 vx、轮轴非侧滑约束 vy=0，以及 IMU 偏航角速度。原始 pose 的零协方差未改动，也不用于融合。

## 使用与边界

```bash
cd /path/to/your/ros2_workspace
source /opt/ros/jazzy/setup.bash
colcon build --packages-select sam_bot_description --symlink-install
source install/setup.bash
ros2 launch sam_bot_description display.launch.py
```

巡检场景入口需要另行安装 `nav_lab_scene` 包；安装后可运行 `ros2 launch nav_lab_scene scene.launch.py rviz:=true`。

手动控制必须发送 TwistStamped 到 /demo/cmd_vel，并在停止时明确发送零速度。差速插件不应被当作具有失联自动停车功能的真实底盘。

模型参考坐标与 footprint 已变更；已有导航站点需核对。新实验建议重新建图、重新记录 map 坐标目标。测试记录见 `docs/navigation_fix_validation.md`。

## 连续目标转圈修正（2026-09-27）

默认 nav2_params.yaml 现使用 NavFn + Regulated Pure Pursuit（RPP）。原 MPPI 配置保留为 nav2_params_mppi.yaml，仅用于后续诊断对比。膨胀系数保留用户当前的 1.5，未通过改膨胀参数掩盖问题。

RPP 在偏离路径方向较大时先原地对准方向，再按前视点跟踪路径；期望线速度 0.25 m/s，原地转向速度 0.6 rad/s。仍启用碰撞检测、速度平滑和碰撞监控。结果与局限见 docs/turning_diagnosis.md。
