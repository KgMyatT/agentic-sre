#!/bin/bash

set -e

LOG_FILE="/var/log/agentic-bootstrap.log"

exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "==============================="
echo "STARTING AGENTIC-SRE BOOTSTRAP"
echo "==============================="

#############################################
# SYSTEM UPDATE
#############################################

yum update -y

#############################################
# INSTALL REQUIRED PACKAGES
#############################################

yum install -y \
  docker \
  git \
  curl \
  wget

#############################################
# ENABLE & START DOCKER
#############################################

systemctl enable docker
systemctl start docker

usermod -aG docker ec2-user

#############################################
# INSTALL DOCKER COMPOSE
#############################################

curl -L \
https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64 \
-o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

docker-compose version

#############################################
# CREATE PROJECT DIRECTORY
#############################################

mkdir -p /opt/agentic-sre

cd /opt/agentic-sre

#############################################
# CREATE ENV FILE
#############################################

cat > .env <<EOF
REDIS_HOST=redis
REDIS_PORT=6379


SLACK_WEBHOOK_URL=REPLACE_ME

GITHUB_TOKEN=REPLACE_ME
GITHUB_REPO=your-org/agentic-sre

ENVIRONMENT=production
EOF

#############################################
# CREATE DOCKER COMPOSE FILE
#############################################

cat > docker-compose.yml <<'COMPOSE'
version: '3.9'

services:

  redis:
    image: redis:7
    container_name: redis
    restart: always

    ports:
      - "6379:6379"

    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    image: kgmyat/agentic-sre-app:latest

    container_name: agentic-app

    restart: always

    env_file:
      - .env

    ports:
      - "5000:5000"

    depends_on:
      redis:
        condition: service_healthy

  analyzer-worker:
    image: kgmyat/agentic-sre-app:latest

    container_name: analyzer-worker

    restart: always

    command: python agent/workers/analyzer_worker.py

    env_file:
      - .env

    depends_on:
      redis:
        condition: service_healthy

  planner-worker:
    image: kgmyat/agentic-sre-app:latest

    container_name: planner-worker

    restart: always

    command: python agent/workers/planner_worker.py

    env_file:
      - .env

    depends_on:
      redis:
        condition: service_healthy

  executor-worker:
    image: kgmyat/agentic-sre-app:latest

    container_name: executor-worker

    restart: always

    command: python agent/workers/executor_worker.py

    env_file:
      - .env

    depends_on:
      redis:
        condition: service_healthy

COMPOSE

#############################################
# START CONTAINERS
#############################################

docker-compose up -d

#############################################
# VERIFY CONTAINERS
#############################################

docker ps

#############################################
# INSTALL GRAFANA ALLOY
#############################################

mkdir -p /opt/alloy

cd /opt/alloy

curl -fsSL https://storage.googleapis.com/cloud-onboarding/alloy/scripts/install-linux-binary.sh -o install-alloy.sh

chmod +x install-alloy.sh

#############################################
# ENV VARS FOR GRAFANA CLOUD
#############################################

export GCLOUD_HOSTED_METRICS_URL="https://prometheus-prod-37-prod-ap-southeast-1.grafana.net/api/prom"
export GCLOUD_HOSTED_METRICS_ID="3142900"

export GCLOUD_HOSTED_LOGS_URL="https://logs-prod-020.grafana.net"
export GCLOUD_HOSTED_LOGS_ID="1567125"

export GCLOUD_RW_API_KEY="61e8110f-f312-48cd-9b1a-23c5baf6b9f5"

#############################################
# INSTALL ALLOY
#############################################

ARCH="amd64" /bin/sh install-alloy.sh

#############################################
# CREATE BASIC ALLOY CONFIG
#############################################

mkdir -p /etc/alloy

cat > /etc/alloy/config.alloy <<EOF

logging {
  level = "info"
}

prometheus.exporter.unix "node" {
}

prometheus.scrape "node" {
  targets = prometheus.exporter.unix.node.targets

  forward_to = [
    prometheus.remote_write.metrics.receiver
  ]
}

prometheus.remote_write "metrics" {
  endpoint {
    url = "${GCLOUD_HOSTED_METRICS_URL}"

    basic_auth {
      username = "${GCLOUD_HOSTED_METRICS_ID}"
      password = "${GCLOUD_RW_API_KEY}"
    }
  }
}

loki.write "logs" {
  endpoint {
    url = "${GCLOUD_HOSTED_LOGS_URL}"

    basic_auth {
      username = "${GCLOUD_HOSTED_LOGS_ID}"
      password = "${GCLOUD_RW_API_KEY}"
    }
  }
}

loki.source.file "system_logs" {
  targets = [
    {
      __path__ = "/var/log/messages",
      job = "system"
    }
  ]

  forward_to = [
    loki.write.logs.receiver
  ]
}

EOF

#############################################
# START ALLOY
#############################################

systemctl enable alloy
systemctl restart alloy

#############################################
# FINAL STATUS
#############################################

echo "==============================="
echo "BOOTSTRAP COMPLETE"
echo "==============================="

docker ps

systemctl status alloy --no-pager