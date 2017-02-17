resource "aws_efs_file_system" "user_data" {
  performance_mode = "generalPurpose"

  tags {
    "Name" = "user_data"
  }
}

resource "aws_efs_mount_target" "slave_private_subnet" {
  file_system_id = "${aws_efs_file_system.user_data.id}"
  subnet_id = "${aws_subnet.private.id}"
  security_groups = ["${aws_security_group.slave.id}"]
}
