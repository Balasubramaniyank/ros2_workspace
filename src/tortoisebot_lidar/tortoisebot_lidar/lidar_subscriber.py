import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math
from std_msgs.msg import Float32
from std_msgs.msg import String

class Lidar_subscriber(Node):
    def __init__(self):
        super().__init__('lidar_subscriber')

        self.subscriber = self.create_subscription(LaserScan,'scan',self.call_back,20)

        self.publisher=self.create_publisher(Float32,'closest_object_distance',20)

    def call_back(self, msg):
      
        # Convert 15 degrees to radians
        angle_range = math.radians(15)

        start_index = int((0.0 - angle_range - msg.angle_min) / msg.angle_increment)
        end_index   = int((0.0 + angle_range - msg.angle_min) / msg.angle_increment)
        self.valid =[]
        front_ranges = msg.ranges[start_index:end_index]
        closest=float('inf')
        for f in front_ranges:
            if(f>0.0 and not math.isnan(f) and not math.isinf(f)):
                if closest>f:
                    closest=f
                self.valid.append(f)    
        if closest==float('inf'):
            self.get_logger().info('No valid objects detected')

        elif (False):
            #for median finding code ----------------------------------------------------
            msg =Float32()
            sort_array=sorted(self.valid)
            n=len(sort_array)

            if n%2==1:
                msg.data=round(sort_array[n//2],2)
            else:
                msg.data=round((sort_array[n//2-1]+sort_array[n//2])/2 ,2)

            self.publisher.publish(msg)
            print(msg.data)      
            #------------------------------------------------------------------------------
        else:    
            self.get_logger().info(f'Closest Object {closest:.2f} m')
            msg =Float32()
            msg.data=round(closest, 2)  
            self.publisher.publish(msg)

       
            
   
       
def main():
    rclpy.init()
    lidar_node = Lidar_subscriber()
    rclpy.spin(lidar_node)
    lidar_node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()


