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

# Outputs
output "master_public_ip" {
  value = aws_instance.master.public_ip
}
