resource "aws_security_group" "public_slave" {
  name = "Public-Slaves-${var.stack_name}"
  description = "Mesos Public Slaves"

  vpc_id = "${aws_vpc.dcos.id}"
}

resource "aws_security_group_rule" "public_slave_egress_all" {
  security_group_id = "${aws_security_group.public_slave.id}"

  type = "egress"
  from_port = 0
  to_port = 65535
  protocol = "-1"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "public_slave_ingress_public_slave" {
  security_group_id = "${aws_security_group.public_slave.id}"

  type = "ingress"
  from_port = 0
  to_port = 65535
  protocol = "-1"
  self = true
}

resource "aws_security_group_rule" "public_slave_ingress_master" {
  security_group_id = "${aws_security_group.public_slave.id}"

  type = "ingress"
  from_port = 0
  to_port = 65535
  protocol = "-1"
  source_security_group_id = "${aws_security_group.master.id}"
}

resource "aws_security_group_rule" "public_slave_ingress_slave" {
  security_group_id = "${aws_security_group.public_slave.id}"

  type = "ingress"
  from_port = 0
  to_port = 65535
  protocol = "-1"
  source_security_group_id = "${aws_security_group.slave.id}"
}

resource "aws_security_group_rule" "public_slave_ingress_80_tcp" {
  security_group_id = "${aws_security_group.public_slave.id}"

  type = "ingress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "public_slave_ingress_443_tcp" {
  security_group_id = "${aws_security_group.public_slave.id}"

  type = "ingress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
