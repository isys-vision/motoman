cmake_minimum_required(VERSION 3.16.0)

project(motoman_hc20_support)

find_package(catkin REQUIRED)

catkin_package()

if (CATKIN_ENABLE_TESTING)
  find_package(roslaunch REQUIRED)
  roslaunch_add_file_check(test/roslaunch_test_hc20.xml)
  roslaunch_add_file_check(test/roslaunch_test_hc20dtp.xml)
  roslaunch_add_file_check(test/roslaunch_test_hc30pl.xml)
endif()

install(DIRECTORY config launch meshes urdf
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
