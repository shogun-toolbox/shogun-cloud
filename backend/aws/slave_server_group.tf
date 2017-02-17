resource "aws_autoscaling_group" "slave_server_group" {
  name = "Slaves-${var.stack_name}"

  min_size = "${var.slave_instance_count_min}"
  max_size = "${var.slave_instance_count_max}"
  desired_capacity = "${var.slave_instance_count_max / var.slave_instance_count_min}"

  termination_policies = ["OldestInstance", "ClosestToNextInstanceHour"]

  vpc_zone_identifier = ["${aws_subnet.private.id}"]
  launch_configuration = "${aws_launch_configuration.slave.id}"

  tag {
    key = "role"
    value = "mesos-slave"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = false
  }
}
