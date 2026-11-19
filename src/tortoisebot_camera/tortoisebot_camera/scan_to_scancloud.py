import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, PointCloud2
from laser_geometry import LaserProjection


class ScanToCloud(Node):

    def __init__(self):
        super().__init__('scan_to_cloud')

        self.projector = LaserProjection()

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.pub = self.create_publisher(
            PointCloud2,
            '/scan_cloud',
            10
        )

        self.get_logger().info('Scan to Cloud node started')


    def scan_callback(self, scan_msg):
        cloud_msg = self.projector.projectLaser(scan_msg)
        cloud_msg.header = scan_msg.header
        self.pub.publish(cloud_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ScanToCloud()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
