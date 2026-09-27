# 连续导航转圈排查（2026-09-27）

## 证据与判断

用户说明问题在调整 cost_scaling_factor 之前已存在。因此未把膨胀系数当成根因，也未回退用户当前的 1.5。

现场日志：第一次 Goal succeeded，之后反复 Failed to make progress，行为树依次执行 spin / wait / backup。采样时控制器约发出 vx=0.105 m/s、wz=-1 rad/s，平滑器和碰撞监控后的输出接近，底盘跟随这些指令。大角速度来自控制器输出，并非碰撞监控单独造成。

现场一次激光端点与地图的对齐检查：障碍距离中位数 0 米，样本全部在 15 cm 内。这只能说明该次采样的定位对齐良好，不能证明长期定位无误。数据见 turning_live_snapshot.json。

## 隔离的连续目标对比

统一场景、由场景几何生成的地图、已知出生点初始化 AMCL、同样的速度限制与膨胀系数。ROS_DOMAIN_ID=86，独立 GZ_PARTITION，未混入用户现有图。

目标依次为：(-2.5,-2.7,0)、(-3.5,-2.7,π)、(-3.5,-1.5,π/2)。后一个目标仅在前一个成功后发送。

| 控制配置 | 第一个直行目标 | 第二个掉头返回 | 第三个转弯 |
| --- | --- | --- | --- |
| 原 MPPI | 成功，12.2 s | 70 s 超时，反复无法取得进展 | 未执行 |
| MPPI + Rotation Shim | 成功，15.3 s | 70 s 超时 | 未执行 |
| RPP | 成功，7.9 s | 成功，16.1 s | 成功，14.9 s |

这些是墙上时钟耗时，会受系统负载影响；终点均使用原配置 0.25 m 位置容差。原始结果见 turning_before.json、turning_shim_trial.json、turning_after_rpp.json。

结论：已将复现问题缩小到当前 MPPI 路径跟踪配置在大角度换向场景的表现。不能据此断言 MPPI 算法本身有缺陷，也尚未定位到某一个 critic 或数值优化实现错误。

## 实际修正

默认 nav2_params.yaml 改用 RPP，保留 NavFn、AMCL、EKF、代价地图、速度平滑器和碰撞监控。RPP 显式执行起步方向对齐与终点朝向调整，再跟踪前视点。原 MPPI 配置完整保存在 config/nav2_params_mppi.yaml，便于后续单独调参研究。

没有把“增大允许卡住时间”当作修复，也没有禁用碰撞检测。

统一入口：

```bash
ros2 launch nav_lab_scene navigation.launch.py map:=/绝对路径/nav_lab.yaml
ros2 launch nav_lab_scene navigation_view.launch.py
```

两个入口都使用 LOCALHOST 发现范围。复现实验脚本位于 nav_lab_scene/tests/check_sequential_navigation.py，需先 source ROS 与工作空间；默认测试修正后的配置，也可用 --params-file 指定原 MPPI 文件。脚本使用域 86，不应与其他域 86 测试并发运行，自动关闭自身测试进程。

## 另外发生的 odom 缺失

用户重启导航后出现 base_footprint → odom 不存在。现场 Gazebo /clock 正常，但 ROS /clock、原始里程计、滤波里程计都没有数据；原桥接进程存在，却未被新诊断节点发现。只重启 ros_gz_bridge 后恢复数据，odom TF 恢复，Nav2 自动继续激活。这个问题与先前已经复现的转圈分开记录，桥接为什么失去通信尚未确定。

## 验证边界

上述三个目标验证直行、掉头和转弯的连续执行；不等于已经完成全场景巡检、封门绕行或长期稳定性测试。原有单次约 1 米导航成功的测试不足以覆盖连续目标，本次补充了回归脚本。

## 当前运行实例

已为用户当前场景重启本机发现范围的 Nav2 和 RViz，加载默认 RPP 配置。AMCL 与导航生命周期管理器均报告 active，实际控制器日志确认为 RegulatedPurePursuitController。

最后一次当前扫描与保存地图的局部匹配检查：匹配前端点到障碍距离 RMSE 约 0.012 米，中位数为 0；在当前估计周围有限范围内优化后 RMSE 约 0.007 米，初值仅修正约 1.6 厘米及 0.003 弧度，并作为一次 initialpose 发布。此检查用于确认当前对齐状态，不是新增永久定位算法，也不代表全局定位真值误差。结果见 current_map_alignment.json。

仿真、恢复后的桥接、Nav2、RViz保持运行；隔离测试实例全部关闭。将来重新启动时使用 navigation.launch.py 的默认参数，并在 RViz 设置当前地图初始位置；本次恢复用的 /tmp/nav_recovery_rpp.yaml 不是长期启动配置。
