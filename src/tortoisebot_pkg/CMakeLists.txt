cmake_minimum_required(VERSION 3.8)
project(tortoisebot_pkg)

find_package(ament_cmake REQUIRED)
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz REQUIRED)
find_package(ros_gz_bridge REQUIRED)
find_package(robot_state_publisher REQUIRED)

# Install launch files
install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.py"
)

# Install urdf files
install(
  DIRECTORY urdf/
  DESTINATION share/${PROJECT_NAME}/urdf
  FILES_MATCHING PATTERN "*.urdf"
)

install(
  DIRECTORY worlds/
  DESTINATION share/${PROJECT_NAME}/worlds
  FILES_MATCHING PATTERN "*.sdf"
)

ament_package()