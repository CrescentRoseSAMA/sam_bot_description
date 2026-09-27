#!/usr/bin/env python3
"""Attach configurable simulation uncertainty to Gazebo wheel odometry.

Raw pose and twist are preserved. This is not an empirical sensor calibration.
Only the twist is fused by ekf.yaml; raw pose covariance remains untouched.
"""
import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class OdomCovariance(Node):
    def __init__(self):
        super().__init__('odom_covariance')
        self.declare_parameter('input_topic', '/demo/odom')
        self.declare_parameter('output_topic', '/demo/odom_with_covariance')
        # [vx, vy, vz, roll_rate, pitch_rate, yaw_rate], in SI units squared.
        self.declare_parameter('twist_variances', [0.0004, 0.0001, 1.0, 1.0, 1.0, 0.0009])
        self.variances = self.get_parameter('twist_variances').value
        if len(self.variances) != 6 or any(not math.isfinite(v) or v <= 0 for v in self.variances):
            raise ValueError('twist_variances must contain six positive finite values')
        self.publisher = self.create_publisher(
            Odometry, self.get_parameter('output_topic').value, 10)
        self.subscription = self.create_subscription(
            Odometry, self.get_parameter('input_topic').value,
            self.on_odom, qos_profile_sensor_data)

    def on_odom(self, msg):
        # Keep already supplied covariance intact; fill only an entirely unknown matrix.
        if not any(msg.twist.covariance):
            for index, variance in enumerate(self.variances):
                msg.twist.covariance[index * 7] = variance
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = OdomCovariance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
