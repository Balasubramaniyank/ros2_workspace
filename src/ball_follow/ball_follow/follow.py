# # import rclpy
# # from rclpy.node import Node
# # from std_msgs.msg import Float32
# # from geometry_msgs.msg import Twist

# # class FollowBall(Node):
# #     def __init__(self):
# #         super().__init__('ball_follower')

        
# #         self.subscriber = self.create_subscription(
# #             Float32,
# #             'closest_object_distance',
# #             self.call_distance,
# #             10
# #         )

       
# #         self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

# #         self.current_distance = float('inf')

# #         # Timer calls control loop every 0.1 sec
# #         self.timer = self.create_timer(0.1, self.control_loop)

# #     def call_distance(self, msg):
# #         self.current_distance = msg.data

# #     def control_loop(self):
# #         cmd = Twist()

# #         if self.current_distance == float('inf'):
# #             # No object detected → stop
# #             cmd.linear.x = 0.0
# #             self.get_logger().info('No object detected. Stopping.')
# #         elif self.current_distance > 1.0:
# #             # Object is far → move forward
# #             cmd.linear.x = 0.1
# #             self.get_logger().info(f'Object far ({self.current_distance:.2f} m) → moving forward.')
# #         elif 0.5 < self.current_distance <= 1.0:
# #             # Near → move slowly
# #             cmd.linear.x = 0.1
# #             self.get_logger().info(f'Object near ({self.current_distance:.2f} m) → slowing down.')
# #         else:
# #             # Very close → stop
# #             cmd.linear.x = 0.0
# #             self.get_logger().info(f'Object very close ({self.current_distance:.2f} m) → stop.')

# #         self.publisher.publish(cmd)


# # def main(args=None):
# #     rclpy.init(args=args)
# #     node = FollowBall()
# #     rclpy.spin(node)
# #     node.destroy_node()
# #     rclpy.shutdown()


# # if __name__ == '__main__':
# #     main()

# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import LaserScan
# from geometry_msgs.msg import Twist
# import math
# import numpy as np

# class LidarFollower(Node):
#     def __init__(self):
#         super().__init__('lidar_follower')

#         self.subscriber = self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)
#         self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

#         # tuning
#         self.front_deg = 30.0               # front window ± deg to consider
#         self.angle_deadband = math.radians(5)  # considered "centered"
#         self.k_angular = 1.0                # angular proportional gain (tune)
#         self.max_ang_speed = 0.6            # limit angular speed
#         self.max_lin_speed = 0.25           # limit linear speed

#     def lidar_callback(self, msg: LaserScan):
#         ranges = np.array(msg.ranges)               # raw ranges
#         # build angles robustly: one angle per range index
#         angles = msg.angle_min + np.arange(len(ranges)) * msg.angle_increment

#         # valid mask (finite and > 0)
#         valid_mask = np.isfinite(ranges) & (ranges > 0.0)

#         # front window mask (angles in radians)
#         half = math.radians(self.front_deg)
#         front_mask = (angles >= -half) & (angles <= half)

#         # combined mask: valid AND in front
#         mask = valid_mask & front_mask

#         if not np.any(mask):
#             # nothing valid in front window
#             self.get_logger().debug("No valid readings in front window")
#             self.stop_robot()
#             return

#         front_ranges = ranges[mask]
#         front_angles = angles[mask]

#         # find closest object in the front window
#         idx = np.argmin(front_ranges)
#         min_distance = float(front_ranges[idx])
#         angle_to_object = float(front_angles[idx])   # in radians

#         if min_distance <1.0:
#             self.get_logger().info('Stop!!')
#         else:    
#             self.get_logger().info(f"Detected object at {min_distance:.2f} m, angle {math.degrees(angle_to_object):.1f}°")

#         cmd = Twist()

#         # ROTATION: use proportional control on angle (positive angle = left (CCW))
#         # Angular velocity should have same sign as angle_to_object so robot turns toward the object
#         if abs(angle_to_object) > self.angle_deadband:
#             ang = self.k_angular * angle_to_object
#             # clamp angular speed
#             if ang > self.max_ang_speed:
#                 ang = self.max_ang_speed
#             elif ang < -self.max_ang_speed:
#                 ang = -self.max_ang_speed
#             cmd.angular.z = ang
#             cmd.linear.x = 0.0
#             self.get_logger().info(f"Rotating {'left' if ang>0 else 'right'} at {ang:.2f} rad/s")
#         elif min_distance < 1.0:
#             self.get_logger().info(f"Stop !!")
#             self.stop_robot()    
#         else:
#             # CENTERED: small angular velocity and move forward based on distance
#             cmd.angular.z = 0.0
#             if min_distance > 1.0:
#                 cmd.linear.x = self.max_lin_speed
#             elif min_distance > 0.5:
#                 cmd.linear.x = 0.12
#             elif min_distance > 0.35:
#                 cmd.linear.x = 0.05
#             else:
#                 cmd.linear.x = 0.0
#             self.get_logger().info(f"Centered → move forward {cmd.linear.x:.2f} m/s")

#         self.publisher.publish(cmd)

#     def stop_robot(self):
#         cmd = Twist()
#         cmd.linear.x = 0.0
#         cmd.angular.z = 0.0
#         self.publisher.publish(cmd)

# def main(args=None):
#     rclpy.init(args=args)
#     node = LidarFollower()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()

# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import LaserScan
# from geometry_msgs.msg import Twist
# import numpy as np
# import math


# class ObjectFollower(Node):
#     def __init__(self):
#         super().__init__('object_follower')
#         self.create_subscription(LaserScan, '/scan', self.lidar_cb, 10)
#         self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

#     def lidar_cb(self, msg):
#         ranges = np.array(msg.ranges)
#         angles = msg.angle_min + np.arange(len(ranges)) * msg.angle_increment
        
#         # Filter: valid readings within ±30° front
#         valid = np.isfinite(ranges) & (ranges > 0) & (abs(angles) < math.radians(30))
        
#         if not np.any(valid):
#             self.move(0, 0)
#             return
        
#         # Find closest object
#         dist = float(ranges[valid][np.argmin(ranges[valid])])
#         angle = float(angles[valid][np.argmin(ranges[valid])])
        
#         cmd = Twist()
        
#         if dist <= 1.0:
#             cmd.linear.x=0.0
#             cmd.angular.z=0.0
#         else:    
#         # Turn if not aligned, else move forward based on distance
#             if abs(angle) > math.radians(5):
#                 cmd.angular.z = np.clip(angle, -0.6, 0.6)
#             elif dist > 1.0:
#                 cmd.linear.x = 0.25
#             elif dist > 0.5:
#                 cmd.linear.x = 0.12
#             elif dist > 0.35:
#                 cmd.linear.x = 0.05
        
        
#         if dist <=1.0:
#             self.get_logger().info('Robot will be Stop!!')
#         else:    
#             self.get_logger().info(f"Dist: {dist:.2f}m, Angle: {math.degrees(angle):.1f}°")

#         self.pub.publish(cmd)
#     def move(self, linear, angular):
#         cmd = Twist()
#         cmd.linear.x = linear
#         cmd.angular.z = angular
#         self.pub.publish(cmd)


# def main(args=None):
#     rclpy.init(args=args)
#     node = ObjectFollower()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()

import time
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
        ranges =msg.ranges
        myValid=[]
        myValidMap={}
        dist=float('inf')
        myIdx=0

        for i in range(len(ranges)):
            
            value=float(ranges[i])
            if value>0 and not math.isnan(value) and not math.isinf(value):
                myValid.append(value)
                myValidMap.update({i:ranges[i]})
                

        try:
            dist =min(myValid)
        except:
             self.move(0,0)
             return

        windowSize=3

        halfWindow=windowSize//2

        
        #apply the filter using medium
        for i in range(1,len(myValid)-1):
            window=myValid[i-halfWindow:i+halfWindow+1]
            sortedWindow=sorted(window)
            midValue=sortedWindow[len(sortedWindow)//2]
            myValid[i]=midValue

    
        try:
            dist =min(myValid)
        except:
             self.move(0,0)
             return
              
        for key,values in myValidMap.items():
            if values==dist:
                myIdx=key
                break    

        
        angle=msg.angle_min +(myIdx*msg.angle_increment)
        # print(angle)
        
        cmd = Twist()
        
        if dist <= 1.0:
            cmd.linear.x=0.0
            cmd.angular.z=0.0
        else:
        # Turn if not aligned, else move forward based on distance
            if abs(angle) > math.radians(5):
                if 0>angle:
                    cmd.angular.z=-0.5
                else:
                    cmd.angular.z=0.5    
                
            elif dist > 1.0:
                cmd.linear.x = 0.5
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














