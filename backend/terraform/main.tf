terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "movie_rec_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "movie-rec-vpc"
  }
}

# Public Subnet
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.movie_rec_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "movie-rec-public-subnet"
  }
}

# Second Public Subnet
resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.movie_rec_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b" # Different AZ
  map_public_ip_on_launch = true
  tags = {
    Name = "movie-rec-public-subnet-2"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "movie_rec_igw" {
  vpc_id = aws_vpc.movie_rec_vpc.id
  tags = {
    Name = "movie-rec-igw"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.movie_rec_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.movie_rec_igw.id
  }
  tags = {
    Name = "movie-rec-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "public_rt_asso" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rt_asso_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# Security Group
resource "aws_security_group" "movie_rec_sg" {
  name        = "movie-rec-sg"
  description = "Security group for movie recommendation system"
  vpc_id      = aws_vpc.movie_rec_vpc.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Flask API access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Redis access (internal)
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Allow access within VPC
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "movie-rec-sg"
  }
}

# EC2 Instances

resource "aws_instance" "master" {
  ami                    = "ami-0c7217cdde317cfec"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.movie_rec_sg.id]
  key_name               = "dist-rec"

  user_data = templatefile("../scripts/EC2-setup.sh", {
    INSTANCE_TYPE = "master"
  })

  root_block_device {
    volume_size = 8
    volume_type = "gp2"
  }

  tags = {
    Name = "movie-rec-master"
  }
}

# Load Balancer
resource "aws_lb" "movie_rec_alb" {
  name               = "movie-rec-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.movie_rec_sg.id]
  subnets            = [aws_subnet.public_subnet.id, aws_subnet.public_subnet_2.id]

  tags = {
    Name = "movie-rec-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "movie_rec_tg" {
  name        = "movie-rec-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.movie_rec_vpc.id
  target_type = "instance"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "movie-rec-tg"
  }
}

# Listener
resource "aws_lb_listener" "movie_rec_listener" {
  load_balancer_arn = aws_lb.movie_rec_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.movie_rec_tg.arn
  }
}

# Attach EC2 Instances to Target Group
resource "aws_lb_target_group_attachment" "movie_rec_tg_attachment" {
  target_group_arn = aws_lb_target_group.movie_rec_tg.arn
  target_id        = aws_instance.master.id
  port             = 80
}

# Outputs
output "master_public_ip" {
  value = aws_instance.master.public_ip
}

output "alb_dns_name" {
  value = aws_lb.movie_rec_alb.dns_name
}
