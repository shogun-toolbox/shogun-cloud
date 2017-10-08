resource "aws_launch_configuration" "public_slave" {
  security_groups = ["${aws_security_group.public_slave.id}"]
  image_id = "${lookup(var.coreos_amis, var.aws_region)}"
  instance_type = "${var.public_slave_instance_type}"
  key_name = "${aws_key_pair.dcos.key_name}"
  user_data = "${data.template_file.public_slave_user_data.rendered}"
  associate_public_ip_address = true

  lifecycle {
    create_before_destroy = false
  }

  root_block_device {
    volume_size = "${var.public_slave_volume_size}"
  }

  ephemeral_block_device {
    device_name = "/dev/xvdz"
    virtual_name = "ephemeral0"
  }

}

data "template_file" "public_slave_user_data" {
  template = "${file("${path.module}/public_slave_user_data.yml")}"

  vars {
    authentication_enabled      = "${var.authentication_enabled}"
    bootstrap_id                = "${var.bootstrap_id}"
    stack_name                  = "${var.stack_name}"
    aws_region                  = "${var.aws_region}"
    cluster_packages            = "${var.cluster_packages}"
    internal_master_lb_dns_name = "${aws_elb.internal_master.dns_name}"
    public_lb_dns_name          = "${aws_elb.public_slaves.dns_name}"
    exhibitor_s3_bucket         = "${aws_s3_bucket.exhibitor.id}"
    dcos_base_download_url      = "${var.dcos_base_download_url}"
    master_role                 = "${aws_iam_role.master.name}"
    slave_role                  = "${aws_iam_user.dcos.name}"
    stack_id                    = "${var.stack_id}"
    dcos_provider_package_id    = "${var.dcos_provider_package_id}"
  }
}
