import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, LaserScan
from sensor_msgs_py import point_cloud2 as pc2
from std_msgs.msg import Header
import numpy as np
import math
import time

class FusionSlow(Node):
    def __init__(self):
        super().__init__('fusion_slow')
        
        # Subscribers
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.depth_sub = self.create_subscription(
            PointCloud2, '/depth_camera/points', self.depth_callback, 10)
        
        # Publisher with SMALL queue (forces slow rate)
        self.fused_pub = self.create_publisher(
            PointCloud2, '/fused_cloud', 1)  # Queue size 1!
        
        # Rate limiting
        self.last_publish = 0
        self.publish_rate = 2.0  # 2 Hz (0.5 seconds between messages)
        
        self.get_logger().info('🐢 Slow Fusion Node Started (2 Hz)')
    
    def scan_callback(self, msg):
        points = []
        for i, r in enumerate(msg.ranges):
            if msg.range_min <= r <= msg.range_max:
                angle = msg.angle_min + i * msg.angle_increment
                points.append([r * math.cos(angle), r * math.sin(angle), 0.0])
        
        if points:
            self.lidar_points = np.array(points, dtype=np.float32)
            self.try_publish()
    
    def depth_callback(self, msg):
        try:
            points = [
                [p[0], p[1], p[2]]
                for p in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
            ]
            
            if points:
                points_array = np.array(points, dtype=np.float32)
                
                # Downsample more
                if len(points_array) > 500:  # Only 500 points!
                    indices = np.random.choice(len(points_array), 500, False)
                    self.depth_points = points_array[indices]
                else:
                    self.depth_points = points_array
                
                self.try_publish()
                
        except Exception as e:
            self.get_logger().error(f'Depth error: {e}')
    
    def try_publish(self):
        if not hasattr(self, 'lidar_points') or not hasattr(self, 'depth_points'):
            return
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_publish < (1.0 / self.publish_rate):
            return
        
        try:
            fused = np.vstack([self.lidar_points, self.depth_points])
            
            header = Header()
            header.stamp = self.get_clock().now().to_msg()
            header.frame_id = 'base_link'
            
            cloud = pc2.create_cloud_xyz32(header, fused)
            self.fused_pub.publish(cloud)
            
            self.last_publish = current_time
            self.get_logger().info(
                f'📤 Published: {fused.shape[0]} points at {current_time:.1f}s',
                throttle_duration_sec=2.0
            )
            
        except Exception as e:
            self.get_logger().error(f'Publish error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = FusionSlow()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()