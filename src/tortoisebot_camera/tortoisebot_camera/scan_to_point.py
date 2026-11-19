import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2, PointField
import numpy as np
from math import cos, sin, pi
import struct
from typing import List
import time

class LaserToPointCloud(Node):
    def __init__(self):
        super().__init__('laser_to_pointcloud')
        
        # Subscriber
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # Publisher
        self.publisher = self.create_publisher(
            PointCloud2,
            '/lidar_cloud',
            10
        )
        
        self.get_logger().info('LaserToPointCloud node initialized')
        
    def scan_callback(self, msg: LaserScan):
        # Convert LaserScan to PointCloud2
        points = []
        
        for i, range_val in enumerate(msg.ranges):
            if msg.range_min <= range_val <= msg.range_max:
                # Calculate angle
                angle = msg.angle_min + i * msg.angle_increment
                
                # Convert polar to cartesian
                x = range_val * cos(angle)
                y = range_val * sin(angle)
                z = 0.0  # 2D LIDAR has no vertical component
                
                points.append([x, y, z])
        
        if points:
            # Create PointCloud2 message
            cloud_msg = self.create_cloud_xyz(msg.header, points)
            self.publisher.publish(cloud_msg)
            
            self.get_logger().info(
                f'Published {len(points)} points', 
                throttle_duration_sec=2.0
            )
    
    def create_cloud_xyz(self, header, points: List[List[float]]) -> PointCloud2:
        """Create a PointCloud2 message from xyz points"""
        msg = PointCloud2()
        msg.header = header
        msg.header.frame_id = 'lidar_link'  # Or transform to base_link
        
        # Set fields
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        msg.fields = fields
        
        # Set data
        msg.height = 1
        msg.width = len(points)
        msg.is_bigendian = False
        msg.point_step = 12  # 3 * 4 bytes
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = True
        
        # Pack data
        data = []
        for point in points:
            data.extend([struct.pack('f', coord) for coord in point])
        msg.data = b''.join(data)
        
        return msg

def main(args=None):
    rclpy.init(args=args)
    node = LaserToPointCloud()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()