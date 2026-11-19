#!/usr/bin/env python3
import math
import time
import tf2_ros
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler


class ZigZagVerticalCleaner(Node):

    def __init__(self):
        super().__init__('zigzag_vertical_cleaner')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.tf_buffer = tf2_ros.Buffer(cache_time=rclpy.duration.Duration(seconds=10))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Room size (matches 8x8 Gazebo world)
        self.x_min = -3.5
        self.x_max =  3.5
        self.y_min = -3.5
        self.y_max =  3.5
        self.step  = 0.5

        # Home position (center)
        self.home = self.get_home_pose()


        # print(self.home.pose.position.x)

        print(self.home.pose.orientation)

        self.home=(self.home.pose.orientation.x,self.home.pose.orientation.y,self.home.pose.orientation.z)

        self.get_logger().info("Waiting for Nav2...")
        self.client.wait_for_server()
        self.get_logger().info("Nav2 ready")

        self.waypoints = self.generate_vertical_zigzag()
        self.execute_path()

    # --------------------------------------------------

    def get_home_pose(self):
        self.get_logger().info('Waiting for TF: map -> base_footprint')
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            try:
                if self.tf_buffer.can_transform(
                    'map', 'base_footprint', rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=1)):

                    tf = self.tf_buffer.lookup_transform(
                        'map', 'base_footprint', rclpy.time.Time())

                    pose = PoseStamped()
                    pose.header.frame_id = 'map'
                    pose.pose.position.x = tf.transform.translation.x
                    pose.pose.position.y = tf.transform.translation.y
                    pose.pose.orientation = tf.transform.rotation

                    self.get_logger().info('TF available: map -> base_footprint')
                    return pose

                else:
                    self.get_logger().warn('TF not ready yet, retrying...')

            except Exception as e:
                self.get_logger().warn(f'TF error: {e}')

    # ------------------------------------------------------------------------------------ 
    def generate_vertical_zigzag(self):
        """
        Generate vertical zig-zag coverage:
        North → South sweeps with eastward shifts
        """
        waypoints = []

        x = self.x_min
        go_north = True

        while x <= self.x_max:
            if go_north:
                # bottom → top
                waypoints.append((x, self.y_min, math.pi/2))
                waypoints.append((x, self.y_max, math.pi/2))
            else:
                # top → bottom
                waypoints.append((x, self.y_max, -math.pi/2))
                waypoints.append((x, self.y_min, -math.pi/2))

            go_north = not go_north
            x += self.step

        # print(waypoints)
        self.get_logger().info(f"Generated {len(waypoints)} waypoints")
        return waypoints

    # --------------------------------------------------

    def execute_path(self):
        for i, wp in enumerate(self.waypoints):
            self.get_logger().info(f"Waypoint {i + 1}/{len(self.waypoints)}")
            self.go_to_pose(wp)
            time.sleep(4.0)  # pause like cleaning robot

        self.get_logger().info("Coverage complete. Returning home.")
        self.go_to_pose(self.home)

    # --------------------------------------------------

    def go_to_pose(self, waypoint):
        x, y, yaw = waypoint

        goal = NavigateToPose.Goal()
        goal.pose = self.make_pose(x, y, yaw)

        send_future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

    # --------------------------------------------------

    def make_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y

        q = quaternion_from_euler(0.0, 0.0, yaw)
        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]

        return pose


def main():
    rclpy.init()
    node = ZigZagVerticalCleaner()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
