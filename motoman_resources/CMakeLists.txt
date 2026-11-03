cmake_minimum_required(VERSION 3.16.0)

project(motoman_resources)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY urdf
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
