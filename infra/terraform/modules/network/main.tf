data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs                         = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  nat_gateway_count_effective = min(var.nat_gateway_count, var.az_count)
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.common_tags, {
    Name = "${var.name}-vpc"
  })
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name = "${var.name}-igw"
  })
}

resource "aws_subnet" "public" {
  count                   = var.az_count
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name                                = "${var.name}-public-${count.index + 1}"
    "kubernetes.io/role/elb"            = "1"
    "kubernetes.io/cluster/${var.name}" = "shared"
  })
}

resource "aws_subnet" "private_app" {
  count             = var.az_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = local.azs[count.index]

  tags = merge(var.common_tags, {
    Name                                = "${var.name}-private-app-${count.index + 1}"
    "kubernetes.io/role/internal-elb"   = "1"
    "kubernetes.io/cluster/${var.name}" = "shared"
  })
}

resource "aws_subnet" "private_db" {
  count             = var.az_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = local.azs[count.index]

  tags = merge(var.common_tags, {
    Name = "${var.name}-private-db-${count.index + 1}"
  })
}

resource "aws_eip" "nat" {
  count  = local.nat_gateway_count_effective
  domain = "vpc"

  tags = merge(var.common_tags, {
    Name = "${var.name}-nat-eip-${count.index + 1}"
  })
}

resource "aws_nat_gateway" "nat" {
  count         = local.nat_gateway_count_effective
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.common_tags, {
    Name = "${var.name}-nat-${count.index + 1}"
  })

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(var.common_tags, {
    Name = "${var.name}-public-rt"
  })
}

resource "aws_route_table" "private" {
  count  = var.az_count
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index % local.nat_gateway_count_effective].id
  }

  tags = merge(var.common_tags, {
    Name = "${var.name}-private-rt-${count.index + 1}"
  })
}

resource "aws_route_table_association" "public_assoc" {
  count          = var.az_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_app_assoc" {
  count          = var.az_count
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "private_db_assoc" {
  count          = var.az_count
  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
