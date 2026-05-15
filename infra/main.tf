provider "aws" {
  region = "us-east-1"
}

# =========================
# VPC
# =========================

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "agentic-sre-vpc"
  }
}

# =========================
# SUBNET
# =========================

resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "agentic-sre-subnet"
  }
}

# =========================
# INTERNET GATEWAY
# =========================

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "agentic-sre-igw"
  }
}

# =========================
# ROUTE TABLE
# =========================

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "agentic-sre-rt"
  }
}

resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.rt.id
}

# =========================
# SECURITY GROUP
# =========================

resource "aws_security_group" "sg" {
  name   = "agentic-sre-sg"
  vpc_id = aws_vpc.main.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Flask App
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # IMPORTANT:
  # Redis should NOT be public in production
  # Remove 6379 public exposure

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "agentic-sre-sg"
  }
}

# =========================
# SSH KEY
# =========================

resource "aws_key_pair" "deployer" {
  key_name   = "agentic-key"
  public_key = file("${path.module}/id_rsa.pub")
}

# =========================
# EC2 INSTANCE
# =========================

resource "aws_instance" "agentic_sre" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.sg.id]
  key_name               = aws_key_pair.deployer.key_name

  user_data = file("${path.module}/user_data.sh")
  
  tags = {
    Name = "agentic-sre"
  }
}

# =========================
# OUTPUTS
# =========================

output "public_ip" {
  value = aws_instance.agentic_sre.public_ip
}