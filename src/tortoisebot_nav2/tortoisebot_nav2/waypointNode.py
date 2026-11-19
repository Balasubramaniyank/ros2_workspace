#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.parameter import Parameter
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import tf2_ros
import math
import time

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')

        # MUST use simulation time
        self.set_parameters([
            Parameter('use_sim_time', Parameter.Type.BOOL, True)
        ])

        # Nav2 action client
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # TF buffer with cache time
        self.tf_buffer = tf2_ros.Buffer(cache_time=rclpy.duration.Duration(seconds=10))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Waypoints (map frame)
        # self.waypoints = [
        #     (5.47185, 2.16938,-0.58),
        #     (8.18081,7.86283,-2.01887),
        #     (8.57968, -2.97183,-1.8119),
        #     (0.119204, -6.55263, -3.11322),
        #     (-6.88872,2.86783, -1.68801)
        # ]


        self.waypoints =[

            # (-2.93560,  9.19065,  0.045064),
            # ( 9.54676,  9.26782, -3.11965),

            # (-3.03960,  8.59689, -0.0556696),
            # ( 9.37377,  7.28997, -3.07478),

            # (-2.78808,  7.12190,  0.0159691),
            # ( 9.17374,  6.31863,  3.12001),

            # (-2.56090,  6.55062, -0.0158746),
            # ( 9.49549,  5.31336, -3.05099),

            # (-2.90901,  5.24337,  0.00470467),
            # ( 9.00108,  4.35007, -3.12451),

            # (-2.92676,  4.18336,  0.0290387),
            # ( 9.08514,  3.80307, -3.12852),

            # (-2.87880,  3.13324, -0.0311123),

            # ( 8.83765,  2.17820,  3.13856),
            # (-3.24011,  1.79703, -0.0138983),

            # ( 9.03870,  1.47580, -3.07549),
            # (-3.08592,  0.669563,  0.0353769),

            # ( 9.38534,  0.724851, -3.11777),
            # (-3.03580, -0.180586, -0.00301463),

            # ( 8.96022,  0.146006, -3.12428),
            # (-2.98769, -0.923886, -0.0164519),

            # ( 9.11737, -0.747062, -3.08697),
            # (-3.03963, -1.40308, -0.00145787),

            # ( 9.22719, -1.97171, -3.11156),
            # (-3.12736, -1.84417, -0.025178),

            # ( 9.07475, -3.20290, -3.04808),
            (-3.19774, -2.91466,  0.0594686),

            ( 9.26345, -3.22335,  3.12175),
            (-3.03781, -3.64687, -0.0123097)

        ]

        self.wait_times = [1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1]
        self.current_index = 0
        self.start_time = time.time()

        self.get_logger().info('Waiting for Nav2 action server...')
        self.client.wait_for_server()

        # IMPORTANT: wait for /clock to start
        self.wait_for_clock()

        # Get home pose safely
        self.home_pose = self.get_home_pose()
        self.get_logger().info('Home pose saved. Starting navigation.')

        self.navigate_next()

    def wait_for_clock(self):
        self.get_logger().info('Waiting for /clock (simulation time)...')
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.get_clock().now().nanoseconds > 0:
                self.get_logger().info('Simulation clock started')
                return

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

    def navigate_next(self):
        if self.current_index < len(self.waypoints):
            x, y, yaw = self.waypoints[self.current_index]
            self.send_goal(x, y, yaw)
        else:
            self.get_logger().info('All waypoints reached. Returning home.')
            self.send_home()

    def send_goal(self, x, y, yaw):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info(f'Sending waypoint {self.current_index + 1}')
        self.client.send_goal_async(goal).add_done_callback(self.goal_response)

    def goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by Nav2')
            return
        goal_handle.get_result_async().add_done_callback(self.goal_done)

    def goal_done(self, future):
        self.get_logger().info('Waypoint reached')
        wait_time = self.wait_times[self.current_index]
        self.get_logger().info(f'Waiting {wait_time} seconds')
        time.sleep(wait_time)
        self.current_index += 1
        self.navigate_next()

    def send_home(self):
        goal = NavigateToPose.Goal()
        goal.pose = self.home_pose
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        self.get_logger().info('Navigating to home')
        self.client.send_goal_async(goal).add_done_callback(self.home_done)

    def home_done(self, future):
        total_time = time.time() - self.start_time
        self.get_logger().info(f'Mission completed in {total_time:.2f} seconds')


def main():
    rclpy.init()
    node = WaypointNavigator()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
