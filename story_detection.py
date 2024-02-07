import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from math import atan2, pi, asin

class CmdVelSubscriber(Node):
    def __init__(self):
        super().__init__('cmd_vel_subscriber')
        self.cmd_vel_subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10)
        self.imu_subscription = self.create_subscription(
            Imu,
            '/imu',
            self.imu_callback,
            10)
        self.previous_yaw = None
        self.total_rotation = 0.0
        self.previous_movement = None

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        if linear_x == 0:
            movement = "Stop"
        elif linear_x > 0:
            movement = "Move forward"
        else:
            movement = "Move backward"

        if movement != self.previous_movement:
            self.get_logger().info(f"Movement: {movement}")
            self.previous_movement = movement

    def imu_callback(self, msg):
        orientation = msg.orientation
        roll, pitch, yaw = self.quaternion_to_euler(orientation.x, orientation.y, orientation.z, orientation.w)

        if self.previous_yaw is None:
            self.previous_yaw = yaw
            return

        delta_yaw = self.angle_difference(yaw, self.previous_yaw)

        self.total_rotation += delta_yaw

        if abs(self.total_rotation) >= pi / 2:  # 90 degrees in radians
            direction = "clockwise" if delta_yaw > 0 else "counter clockwise"
            self.get_logger().info(f"Movement: Turned 90 degrees {direction}")
            self.total_rotation = 0.0

        self.previous_yaw = yaw

    def quaternion_to_euler(self, x, y, z, w):
        roll = atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = asin(2 * (w * y - z * x))
        yaw = atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        return roll, pitch, yaw

    def angle_difference(self, new_angle, old_angle):
        diff = new_angle - old_angle
        if diff > pi:
            diff -= 2 * pi
        elif diff < -pi:
            diff += 2 * pi
        return diff

def main(args=None):
    rclpy.init(args=args)
    cmd_vel_subscriber = CmdVelSubscriber()
    rclpy.spin(cmd_vel_subscriber)
    cmd_vel_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
