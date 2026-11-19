#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster, Buffer, TransformListener
from geometry_msgs.msg import TransformStamped
import numpy as np

class TFChainForOctomap(Node):
    def __init__(self):
        super().__init__('tf_chain_for_octomap')
        
        # Use Gazebo time
        use_sim_time = rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        self.set_parameters([use_sim_time])
        
        self.tf_broadcaster = TransformBroadcaster(self)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Timer at 30Hz (faster than needed)
        self.timer = self.create_timer(0.033, self.publish_tf_chain)
        
        # Default transforms (identity)
        self.default_transform = TransformStamped()
        self.default_transform.transform.rotation.w = 1.0
        
        self.get_logger().info('🔗 TF Chain for OctoMap Started')
    
    def publish_tf_chain(self):
        try:
            now = self.get_clock().now()
            
            # 1. Get or create map→odom (from SLAM)
            try:
                map_to_odom = self.tf_buffer.lookup_transform(
                    'map', 'odom', rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=0.1)
                )
            except:
                # If SLAM not ready, use identity
                map_to_odom = TransformStamped()
                map_to_odom.header.stamp = now.to_msg()
                map_to_odom.header.frame_id = 'map'
                map_to_odom.child_frame_id = 'odom'
                map_to_odom.transform.translation.x = 0.0
                map_to_odom.transform.translation.y = 0.0
                map_to_odom.transform.translation.z = 0.0
                map_to_odom.transform.rotation.w = 1.0
            
            # 2. Get or create odom→base_link (from robot/wheels)
            try:
                odom_to_base = self.tf_buffer.lookup_transform(
                    'odom', 'base_link', rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=0.1)
                )
            except:
                # If not available, use identity
                odom_to_base = TransformStamped()
                odom_to_base.header.stamp = now.to_msg()
                odom_to_base.header.frame_id = 'odom'
                odom_to_base.child_frame_id = 'base_link'
                odom_to_base.transform.translation.x = 0.0
                odom_to_base.transform.translation.y = 0.0
                odom_to_base.transform.translation.z = 0.0
                odom_to_base.transform.rotation.w = 1.0
            
            # 3. Compute map→base_link = map→odom * odom→base_link
            map_to_base = self.multiply_transforms(map_to_odom, odom_to_base)
            map_to_base.header.stamp = now.to_msg()
            map_to_base.header.frame_id = 'map'
            map_to_base.child_frame_id = 'base_link'
            
            # 4. Broadcast ALL transforms
            self.tf_broadcaster.sendTransform(map_to_odom)
            self.tf_broadcaster.sendTransform(odom_to_base)
            self.tf_broadcaster.sendTransform(map_to_base)
            
            # Log every 5 seconds
            self.get_logger().debug(
                f'TF: map→base = ({map_to_base.transform.translation.x:.2f}, '
                f'{map_to_base.transform.translation.y:.2f})',
                throttle_duration_sec=5.0
            )
            
        except Exception as e:
            self.get_logger().error(f'TF chain error: {e}', throttle_duration_sec=2.0)
    
    def multiply_transforms(self, tf1, tf2):
        """Multiply two transforms: result = tf1 * tf2"""
        result = TransformStamped()
        
        # Extract positions
        x1, y1, z1 = (
            tf1.transform.translation.x,
            tf1.transform.translation.y,
            tf1.transform.translation.z
        )
        x2, y2, z2 = (
            tf2.transform.translation.x,
            tf2.transform.translation.y,
            tf2.transform.translation.z
        )
        
        # Extract quaternions
        q1 = np.array([
            tf1.transform.rotation.x,
            tf1.transform.rotation.y,
            tf1.transform.rotation.z,
            tf1.transform.rotation.w
        ])
        q2 = np.array([
            tf2.transform.rotation.x,
            tf2.transform.rotation.y,
            tf2.transform.rotation.z,
            tf2.transform.rotation.w
        ])
        
        # Rotate second translation by first rotation
        # Simplified: for small rotations, just add
        result.transform.translation.x = x1 + x2
        result.transform.translation.y = y1 + y2
        result.transform.translation.z = z1 + z2
        
        # Use second rotation (simplified - assumes small angles)
        result.transform.rotation = tf2.transform.rotation
        
        return result

def main(args=None):
    rclpy.init(args=args)
    node = TFChainForOctomap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()