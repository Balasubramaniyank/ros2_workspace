import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np
import math

class ObjectFollower(Node):
    def __init__(self):
        super().__init__('object_follower')
        self.create_subscription(LaserScan, '/scan', self.lidar_cb, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def lidar_cb(self, msg):
        ranges = np.array(msg.ranges)

        angles = msg.angle_min + np.arange(len(ranges)) * msg.angle_increment

        valid = np.isfinite(ranges)& (ranges > 0)

     
        if not np.any(valid):
            self.move(0, 0)
            return
        
        idx = np.argmin(ranges[valid])
        dist = float(ranges[valid][idx])
        angle = float(angles[valid][idx])

        cmd = Twist()

        # print(angle)
        if dist <= 1.0:
            cmd.linear.x=0.0
            cmd.angular.z=0.0
        else:
        # Turn if not aligned, else move forward based on distance
            if abs(angle) > math.radians(5):
                cmd.angular.z = float(np.clip(angle, -0.8, 0.8))
            elif dist > 1.0:
                cmd.linear.x = 0.35
            elif dist > 0.5:
                cmd.linear.x = 0.20
            elif dist > 0.35:
                cmd.linear.x = 0.15
        
        if dist <=1.0:
           self.get_logger().info('Robot will be Stop!!')
        else:    
            self.get_logger().info(f"Clostest Object Distance: {dist:.2f}m")

        self.pub.publish(cmd)  
    def move(self, linear, angular):
        cmd = Twist()
        cmd.linear.x = float(linear)
        cmd.angular.z =float(angular)
        self.pub.publish(cmd)
        self.get_logger().info('Robot will be Stop Because of No object there!!')


def main(args=None):
    rclpy.init(args=args)
    node = ObjectFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
