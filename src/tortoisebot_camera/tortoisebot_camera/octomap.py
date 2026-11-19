#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point
import numpy as np

class SimpleOctomap(Node):
    def __init__(self):
        super().__init__('simple_octomap')
        
        # Create dummy markers for testing
        self.timer = self.create_timer(1.0, self.publish_markers)
        self.pub = self.create_publisher(MarkerArray, '/occupied_cells_vis_array', 10)
        
        self.get_logger().info('Simple OctoMap Publisher Started')
    
    def publish_markers(self):
        markers = MarkerArray()
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "test"
        marker.id = 0
        marker.type = Marker.CUBE_LIST
        marker.action = Marker.ADD
        marker.scale.x = 0.1
        marker.scale.y = 0.1
        marker.scale.z = 0.1
        marker.color.r = 0.0
        marker.color.g = 0.0
        marker.color.b = 1.0
        marker.color.a = 1.0
        
        # Create some test points
        for i in range(10):
            p = Point()
            p.x = i * 0.2
            p.y = 0.0
            p.z = 0.0
            marker.points.append(p)
        
        markers.markers.append(marker)
        self.pub.publish(markers)
        self.get_logger().info('Published test markers')

def main(args=None):
    rclpy.init(args=args)
    node = SimpleOctomap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


# --------------------------------------------------------------fused_cloud----------------------------------------


# #!/usr/bin/env python3
# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import PointCloud2, LaserScan
# from sensor_msgs_py import point_cloud2 as pc2
# from std_msgs.msg import Header
# import numpy as np
# import math

# class WorkingFusionFixed(Node):
#     def __init__(self):
#         super().__init__('working_fusion')
        
#         # Subscribers
#         self.scan_sub = self.create_subscription(
#             LaserScan, '/scan', self.scan_callback, 10)
#         self.depth_sub = self.create_subscription(
#             PointCloud2, '/depth_camera/points', self.depth_callback, 10)
        
#         # Publisher
#         self.fused_pub = self.create_publisher(
#             PointCloud2, '/fused_cloud', 10)
        
#         # Data storage
#         self.lidar_points = None
#         self.depth_points = None
        
#         self.get_logger().info('✅ Working Fusion Node Started')
    
#     def scan_callback(self, msg):
#         """Convert LaserScan to 3D points"""
#         points = []
        
#         for i, range_val in enumerate(msg.ranges):
#             if msg.range_min <= range_val <= msg.range_max:
#                 angle = msg.angle_min + i * msg.angle_increment
#                 x = range_val * math.cos(angle)
#                 y = range_val * math.sin(angle)
#                 z = 0.0  # 2D LIDAR
#                 points.append([x, y, z])
        
#         if points:
#             self.lidar_points = np.array(points, dtype=np.float32)
#             self.get_logger().info(f'📡 LIDAR: {self.lidar_points.shape[0]} points')
#             self.fuse_and_publish()
    
#     def depth_callback(self, msg):
#         """Process depth camera point cloud"""
#         try:
#             points_list = []
            
#             # Extract points properly
#             for point in pc2.read_points(
#                 msg, 
#                 field_names=("x", "y", "z"), 
#                 skip_nans=True
#             ):
#                 points_list.append([point[0], point[1], point[2]])
            
#             if points_list:
#                 points_array = np.array(points_list, dtype=np.float32)
                
#                 # Downsample if needed
#                 if len(points_array) > 2000:
#                     indices = np.random.choice(
#                         len(points_array), 
#                         size=2000, 
#                         replace=False
#                     )
#                     self.depth_points = points_array[indices]
#                 else:
#                     self.depth_points = points_array
                
#                 self.get_logger().info(f'📷 Depth: {len(points_array)} -> {len(self.depth_points)} points')
#                 self.fuse_and_publish()
                
#         except Exception as e:
#             self.get_logger().error(f'Depth processing error: {e}')
    
#     def fuse_and_publish(self):
#         if self.lidar_points is None or self.depth_points is None:
#             return
        
#         try:
#             # Remove NaN values
#             if np.any(np.isnan(self.lidar_points)):
#                 lidar_mask = ~np.isnan(self.lidar_points).any(axis=1)
#                 self.lidar_points = self.lidar_points[lidar_mask]
            
#             if np.any(np.isnan(self.depth_points)):
#                 depth_mask = ~np.isnan(self.depth_points).any(axis=1)
#                 self.depth_points = self.depth_points[depth_mask]
            
#             if len(self.lidar_points) == 0 or len(self.depth_points) == 0:
#                 return
            
#             # Combine point clouds
#             fused_points = np.vstack([self.lidar_points, self.depth_points])
            
#             # FIXED: Create Header properly
#             header = Header()
#             header.stamp = self.get_clock().now().to_msg()
#             header.frame_id = 'base_link'  # This was missing!
            
#             # Create cloud
#             cloud_msg = pc2.create_cloud_xyz32(header, fused_points)
#             self.fused_pub.publish(cloud_msg)
            
#             self.get_logger().info(
#                 f'✅ Published fused cloud: {fused_points.shape[0]} points',
#                 throttle_duration_sec=1.0
#             )
            
#         except Exception as e:
#             self.get_logger().error(f'Fusion error: {str(e)}')

# def main(args=None):
#     rclpy.init(args=args)
#     node = WorkingFusionFixed()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()


#!/usr/bin/env python3