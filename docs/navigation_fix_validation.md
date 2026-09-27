# 2026-09-27 修改后验证

## 已通过

- SDF 经 xacro 展开后通过 gz sdf -k；旧显示 URDF 通过 check_urdf。
- sam_bot_description 与 nav_lab_scene 构建通过。
- 无 GUI 场景启动、机器人创建、激光、IMU、原始里程计、协方差适配器和二维 EKF 正常。
- TF：odom → base_footprint 的 z=0；base_footprint → base_link 的平移为 (0.12,0,0.15) 米。
- 0.2 m/s 直行命令：末段原始里程计 vx 约 0.200 m/s。
- 0.4 rad/s 原地转向命令：末段轮速里程计约 0.400 rad/s，IMU 约 0.450 rad/s。存在约 0.05 rad/s 差异，未将其视作已完成动力学校准；EKF 使用 IMU yaw rate。轮距保持几何值 0.36 米，不用修改轮距掩盖差异。
- 发送零速度后，末段线速度和角速度均接近零。
- EKF 的 z、roll、pitch 方差约 1e-6；原始未约束三维配置短测 z 方差约 8.98。
- 配置完整 Nav2 bringup：地图服务、AMCL、控制器、规划器、行为树、速度平滑器和碰撞监控启动并激活。
- 发送从 S 附近向前约 1 米的 NavigateToPose 目标，返回状态 4（SUCCEEDED）。最终 AMCL 位置 (-2.72988,-2.69509)，目标 (-2.5,-2.7)，平面误差约 0.230 米，在当前 0.25 米到点容差内。这是定位估计误差相对目标的数值，不是仿真真值定位误差。
- 更新场景几何检查：以轮轴地面投影为参考，保守圆半径增至 0.43 米；基础连通、封上门绕行、封 B 门隔离三项均通过。

## 测试边界

Nav2 测试地图由场景几何栅格化得到，AMCL 初始位置使用已知出生位置，仅用于本次集成检查，没有代替手动 SLAM 建图实验。未测试完整 S→A→B→C→S、封路导航恢复、长期定位漂移或真实硬件。

短时转向的 IMU/轮速差异仍需后续观察，不能声称里程计已经精确标定。速度测量方差为明示的初始仿真假设。

测试使用隔离的 ROS_DOMAIN_ID=85 与 GZ_PARTITION，结束后关闭所有测试实例。

原始结果见 motion_tf_results.json 和 nav2_smoke_results.json。

## 测试过程中修正的启动细节

- SDF 的 canonical_link 必须设为根 base_footprint，否则当前 sdformat_urdf 拒绝解析。
- 本机 Nav2 的非组合启动参数使用 `use_composition:=False`（首字母大写），以兼容 launch 中的 PythonExpression。
- 发送导航目标之前必须等待生命周期节点 active，不能只检查 Action 服务已出现。

## 备份

修改前两个源码包已复制到工作空间的 backups/sam_bot_before_navigation_fix_20260927_100221/。
backups/COLCON_IGNORE 防止 colcon 把备份识别为重复包。
