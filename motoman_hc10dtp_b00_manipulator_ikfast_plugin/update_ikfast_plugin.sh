search_mode=OPTIMIZE_MAX_JOINT
srdf_filename=motoman_hc10dtp_b00.srdf
robot_name_in_srdf=motoman_hc10dtp_b00
moveit_config_pkg=motoman_hc10dtp_b00_moveit_config
robot_name=motoman_hc10dtp_b00
planning_group_name=manipulator
ikfast_plugin_pkg=motoman_hc10dtp_b00_manipulator_ikfast_plugin
base_link_name=base_link
eef_link_name=tool0
ikfast_output_path=/home/juelg/mikado/cells/00hc10dtp/motoman_hc10dtp_b00_manipulator_ikfast_plugin/src/motoman_hc10dtp_b00_manipulator_ikfast_solver.cpp

rosrun moveit_kinematics create_ikfast_moveit_plugin.py\
  --search_mode=$search_mode\
  --srdf_filename=$srdf_filename\
  --robot_name_in_srdf=$robot_name_in_srdf\
  --moveit_config_pkg=$moveit_config_pkg\
  $robot_name\
  $planning_group_name\
  $ikfast_plugin_pkg\
  $base_link_name\
  $eef_link_name\
  $ikfast_output_path
