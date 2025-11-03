# Exercise 05: Docker Volume Management

## Exercise Overview

**Objective**: Master Docker volume management including persistent storage, data sharing between containers, backup strategies, and volume drivers for ML workloads.

**Difficulty**: Intermediate
**Estimated Time**: 3-4 hours
**Prerequisites**:
- Exercise 01-04 (Container Operations, Images, Compose, Networking)
- Lecture 04 (Networking & Volumes)

## Learning Objectives

By completing this exercise, you will:
- Distinguish between volume types (named volumes, bind mounts, tmpfs)
- Implement data persistence strategies for stateful applications
- Share data between containers using volumes
- Execute volume backup and restore procedures
- Configure volume drivers and plugins for different storage backends
- Manage ML models and datasets with optimal volume strategies
- Evaluate performance trade-offs between volume types
- Apply production volume patterns for high-availability systems
- Monitor volume usage and implement cleanup policies
- Design disaster recovery strategies for containerized data

---

## Part 1: Understanding Volume Types

### Step 1.1: Named Volumes

```bash
# Create project directory
mkdir -p ~/docker-exercises/volumes
cd ~/docker-exercises/volumes

# Create a named volume
docker volume create my-data

# Inspect it
docker volume inspect my-data

# Use the volume
docker run -d \
  --name app1 \
  -v my-data:/data \
  alpine sh -c "echo 'Hello from app1' > /data/message.txt && sleep 3600"

# Check the file was created
docker exec app1 cat /data/message.txt

# Stop and remove container
docker stop app1
docker rm app1

# Data persists! Start new container with same volume
docker run -d \
  --name app2 \
  -v my-data:/data \
  alpine sleep 3600

# File still exists!
docker exec app2 cat /data/message.txt

# Cleanup
docker rm -f app2
docker volume rm my-data
```

**Key Points**:
- Named volumes persist after container removal
- Managed by Docker (stored in `/var/lib/docker/volumes/`)
- Can be shared between containers
- Best for production data

### Step 1.2: Bind Mounts

```bash
# Create directory on host
mkdir -p ~/docker-data/app

# Create a file
echo "Hello from host" > ~/docker-data/app/host-file.txt

# Mount host directory into container
docker run -d \
  --name bind-test \
  -v ~/docker-data/app:/app \
  alpine sleep 3600

# File is accessible in container
docker exec bind-test cat /app/host-file.txt

# Create file from container
docker exec bind-test sh -c "echo 'From container' > /app/container-file.txt"

# File appears on host!
cat ~/docker-data/app/container-file.txt

# Cleanup
docker rm -f bind-test
```

**Use Cases**:
- Development (hot reload source code)
- Configuration files
- Host-generated data
- Direct file system access needed

### Step 1.3: tmpfs Mounts

```bash
# Create tmpfs mount (memory-based, not persisted)
docker run -d \
  --name tmpfs-test \
  --tmpfs /tmp:rw,size=100m \
  alpine sleep 3600

# Write to tmpfs
docker exec tmpfs-test sh -c "echo 'Temporary data' > /tmp/temp.txt"
docker exec tmpfs-test cat /tmp/temp.txt

# Check mount
docker exec tmpfs-test df -h /tmp

# Stop and remove container
docker rm -f tmpfs-test

# Start new container - data is gone (tmpfs is not persistent)
docker run -d --name tmpfs-test2 --tmpfs /tmp alpine sleep 3600
docker exec tmpfs-test2 ls /tmp
# Empty!

docker rm -f tmpfs-test2
```

**Use Cases**:
- Temporary cache
- Sensitive data (passwords, tokens)
- High-performance temporary storage
- ML inference temporary files

### Step 1.4: Comparison

```bash
# Create test script
cat > test-volumes.sh << 'EOF'
#!/bin/bash

# Named volume
docker volume create test-named
docker run --rm -v test-named:/data alpine sh -c "echo 'named' > /data/file.txt"

# Bind mount
mkdir -p /tmp/test-bind
docker run --rm -v /tmp/test-bind:/data alpine sh -c "echo 'bind' > /data/file.txt"

# tmpfs
docker run --rm --tmpfs /data alpine sh -c "echo 'tmpfs' > /data/file.txt"

echo "Named volume file:"
docker run --rm -v test-named:/data alpine cat /data/file.txt

echo "Bind mount file:"
cat /tmp/test-bind/file.txt

echo "tmpfs file: (not persisted)"

# Cleanup
docker volume rm test-named
rm -rf /tmp/test-bind
EOF

chmod +x test-volumes.sh
./test-volumes.sh
```

✅ **Checkpoint**: You understand the three types of Docker volumes.

---

## Part 2: Volume Management Operations

### Step 2.1: Basic Volume Commands

```bash
# Create volumes
docker volume create app-data
docker volume create db-data
docker volume create cache-data

# List volumes
docker volume ls

# Inspect specific volume
docker volume inspect app-data

# Find where volume is stored on host
docker volume inspect app-data --format '{{.Mountpoint}}'

# Remove volume
docker volume rm cache-data

# Remove all unused volumes
docker volume prune

# Remove with force
docker volume rm -f app-data db-data
```

### Step 2.2: Volume Labels and Metadata

```bash
# Create volume with labels
docker volume create \
  --label environment=production \
  --label app=myapp \
  --label version=1.0 \
  prod-data

# List volumes with specific label
docker volume ls --filter "label=environment=production"

# Inspect labels
docker volume inspect prod-data --format '{{json .Labels}}' | python -m json.tool

# Cleanup
docker volume rm prod-data
```

### Step 2.3: Volume Drivers

```bash
# Default driver (local)
docker volume create --driver local my-local-volume

# Create volume with driver options
docker volume create \
  --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=100m,uid=1000 \
  tmpfs-volume

# Inspect driver info
docker volume inspect tmpfs-volume

# Cleanup
docker volume rm my-local-volume tmpfs-volume
```

✅ **Checkpoint**: You can manage volumes with Docker CLI.

---

## Part 3: Sharing Data Between Containers

### Step 3.1: Multiple Containers, One Volume

```bash
# Create shared volume
docker volume create shared-data

# Container 1: Writer
docker run -d \
  --name writer \
  -v shared-data:/data \
  alpine sh -c 'while true; do echo "$(date): Message" >> /data/log.txt; sleep 5; done'

# Container 2: Reader
docker run -d \
  --name reader \
  -v shared-data:/data \
  alpine sh -c 'while true; do tail -5 /data/log.txt; sleep 10; done'

# View writer logs
docker logs -f writer

# View reader logs (in another terminal)
docker logs -f reader

# Both containers share the same data!

# Cleanup
docker rm -f writer reader
docker volume rm shared-data
```

### Step 3.2: Data Container Pattern (Legacy)

```bash
# Create data-only container (older pattern)
docker create \
  --name data-container \
  -v /data \
  alpine

# Use data from data container
docker run -d \
  --name app1 \
  --volumes-from data-container \
  alpine sh -c "echo 'App 1' > /data/app1.txt && sleep 3600"

docker run -d \
  --name app2 \
  --volumes-from data-container \
  alpine sh -c "echo 'App 2' > /data/app2.txt && sleep 3600"

# Check both files exist
docker exec app1 ls /data
docker exec app2 ls /data

# Cleanup
docker rm -f data-container app1 app2
```

**Note**: Modern approach uses named volumes instead.

### Step 3.3: Docker Compose Volume Sharing

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Log generator
  app:
    image: alpine
    command: sh -c 'while true; do echo "$(date): Application log" >> /logs/app.log; sleep 2; done'
    volumes:
      - app-logs:/logs

  # Log processor
  processor:
    image: alpine
    command: sh -c 'while true; do echo "=== Last 5 logs ===" && tail -5 /logs/app.log; sleep 10; done'
    volumes:
      - app-logs:/logs
    depends_on:
      - app

  # Log analyzer
  analyzer:
    image: alpine
    command: sh -c 'while true; do wc -l /logs/app.log; sleep 15; done'
    volumes:
      - app-logs:/logs:ro  # Read-only mount!
    depends_on:
      - app

volumes:
  app-logs:
EOF
```

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f processor

# Verify analyzer has read-only access
docker compose exec analyzer sh -c "echo 'test' >> /logs/app.log"
# Should fail: Read-only file system

# Cleanup
docker compose down -v
```

✅ **Checkpoint**: You can share volumes between multiple containers.

---

## Part 4: Database Persistence

### Step 4.1: PostgreSQL with Persistent Storage

```bash
mkdir -p ~/docker-exercises/db-persistence
cd ~/docker-exercises/db-persistence

# Create volume for database
docker volume create postgres-data

# Run PostgreSQL with persistent volume
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15

# Wait for startup
sleep 10

# Create table and insert data
docker exec postgres psql -U postgres -d myapp -c "
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');
"

# Query data
docker exec postgres psql -U postgres -d myapp -c "SELECT * FROM users;"

# Stop and remove container
docker stop postgres
docker rm postgres

# Start new container with same volume
docker run -d \
  --name postgres-new \
  -e POSTGRES_PASSWORD=secret \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15

sleep 10

# Data persists!
docker exec postgres-new psql -U postgres -d myapp -c "SELECT * FROM users;"

# Cleanup
docker rm -f postgres-new
docker volume rm postgres-data
```

### Step 4.2: Complete Database Stack with Compose

```yaml
cat > docker-compose-db.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppass
      - POSTGRES_DB=appdb
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d
      - ./backups:/backups
    ports:
      - "5432:5432"

  mongo:
    image: mongo:7
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
    volumes:
      - mongo-data:/data/db
      - ./mongo-init:/docker-entrypoint-initdb.d
    ports:
      - "27017:27017"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

volumes:
  postgres-data:
  mongo-data:
  redis-data:
EOF
```

```bash
# Create init scripts
mkdir -p init-db backups mongo-init

cat > init-db/01-schema.sql << 'EOF'
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, price) VALUES
    ('Widget', 19.99),
    ('Gadget', 29.99);
EOF

# Start all databases
docker compose -f docker-compose-db.yml up -d

# Wait for startup
sleep 15

# Verify data
docker compose -f docker-compose-db.yml exec postgres \
  psql -U appuser -d appdb -c "SELECT * FROM products;"

# Test MongoDB
docker compose -f docker-compose-db.yml exec mongo \
  mongosh -u admin -p secret --eval "db.adminCommand('listDatabases')"

# Test Redis persistence
docker compose -f docker-compose-db.yml exec redis \
  redis-cli SET mykey "persistent value"

docker compose -f docker-compose-db.yml exec redis \
  redis-cli GET mykey

# Stop and restart - data persists
docker compose -f docker-compose-db.yml down
docker compose -f docker-compose-db.yml up -d

sleep 15

# Data still there!
docker compose -f docker-compose-db.yml exec redis redis-cli GET mykey

# Cleanup
docker compose -f docker-compose-db.yml down -v
```

✅ **Checkpoint**: You can implement persistent database storage.

---

## Part 5: Backup and Restore Strategies

### Step 5.1: Volume Backup

```bash
# Create volume with data
docker volume create app-data

# Add some data
docker run --rm -v app-data:/data alpine sh -c "
  echo 'Important data' > /data/file1.txt
  echo 'More data' > /data/file2.txt
  mkdir -p /data/subdir
  echo 'Nested data' > /data/subdir/file3.txt
"

# Backup volume to tar archive
docker run --rm \
  -v app-data:/source:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/app-data-backup.tar.gz -C /source .

# Verify backup
ls -lh app-data-backup.tar.gz

# List contents
tar tzf app-data-backup.tar.gz

# Delete volume
docker volume rm app-data

# Restore from backup
docker volume create app-data-restored

docker run --rm \
  -v app-data-restored:/target \
  -v $(pwd):/backup \
  alpine tar xzf /backup/app-data-backup.tar.gz -C /target

# Verify restored data
docker run --rm -v app-data-restored:/data alpine ls -laR /data

# Cleanup
docker volume rm app-data-restored
rm app-data-backup.tar.gz
```

### Step 5.2: Database Backup Script

```bash
cat > backup-database.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="postgres"
DB_NAME="myapp"

# Create backup
docker exec $CONTAINER_NAME pg_dump -U postgres $DB_NAME > \
  ${BACKUP_DIR}/backup_${TIMESTAMP}.sql

# Compress
gzip ${BACKUP_DIR}/backup_${TIMESTAMP}.sql

# Keep only last 7 days
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_${TIMESTAMP}.sql.gz"
EOF

chmod +x backup-database.sh
```

### Step 5.3: Automated Backup with Compose

```yaml
cat > docker-compose-backup.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=myapp
    volumes:
      - db-data:/var/lib/postgresql/data

  backup:
    image: postgres:15
    depends_on:
      - db
    volumes:
      - ./backups:/backups
      - db-data:/var/lib/postgresql/data:ro
    command: |
      bash -c '
      while true; do
        TIMESTAMP=$$(date +%Y%m%d_%H%M%S)
        pg_dump -h db -U postgres myapp > /backups/backup_$${TIMESTAMP}.sql
        gzip /backups/backup_$${TIMESTAMP}.sql
        echo "Backup created: backup_$${TIMESTAMP}.sql.gz"
        sleep 86400  # Daily backups
      done
      '
    environment:
      - PGPASSWORD=secret

volumes:
  db-data:
EOF
```

```bash
mkdir -p backups
docker compose -f docker-compose-backup.yml up -d

# Manual backup trigger
docker compose -f docker-compose-backup.yml exec backup \
  sh -c 'pg_dump -h db -U postgres myapp | gzip > /backups/manual_backup.sql.gz'

# List backups
ls -lh backups/

# Cleanup
docker compose -f docker-compose-backup.yml down -v
```

### Step 5.4: Restore from Backup

```bash
# Create database
docker run -d \
  --name postgres-restore \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  -v postgres-restore-data:/var/lib/postgresql/data \
  postgres:15

sleep 10

# Restore from backup
gunzip -c backups/manual_backup.sql.gz | \
  docker exec -i postgres-restore psql -U postgres -d myapp

# Verify data
docker exec postgres-restore psql -U postgres -d myapp -c "\dt"

# Cleanup
docker rm -f postgres-restore
docker volume rm postgres-restore-data
```

✅ **Checkpoint**: You can backup and restore Docker volumes.

---

## Part 6: ML Model and Dataset Management

### Step 6.1: Model Storage Volume

```bash
mkdir -p ~/docker-exercises/ml-volumes
cd ~/docker-exercises/ml-volumes

# Create model storage
docker volume create model-store

# Download and store model
cat > download_model.py << 'EOF'
import torch
import torchvision.models as models
import os

# Download model
print("Downloading ResNet18...")
model = models.resnet18(pretrained=True)

# Save to volume
model_path = '/models/resnet18.pth'
torch.save(model.state_dict(), model_path)
print(f"Model saved to {model_path}")

# Verify
size = os.path.getsize(model_path)
print(f"Model size: {size / 1024 / 1024:.2f} MB")
EOF

# Run download
docker run --rm \
  -v model-store:/models \
  pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime \
  sh -c "pip install torchvision && python -c \"$(cat download_model.py)\""

# Verify model exists
docker run --rm \
  -v model-store:/models \
  alpine ls -lh /models
```

### Step 6.2: Dataset Management

```yaml
cat > docker-compose-ml.yml << 'EOF'
version: '3.8'

services:
  # Data preprocessing
  preprocessor:
    image: python:3.11
    volumes:
      - raw-data:/data/raw:ro  # Read-only
      - processed-data:/data/processed  # Write
      - ./scripts:/scripts
    command: python /scripts/preprocess.py
    environment:
      - INPUT_DIR=/data/raw
      - OUTPUT_DIR=/data/processed

  # Training
  trainer:
    image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
    volumes:
      - processed-data:/data:ro
      - models:/models
      - ./train.py:/workspace/train.py
    command: python /workspace/train.py
    environment:
      - DATA_DIR=/data
      - MODEL_DIR=/models

  # Inference server
  inference:
    image: pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
    volumes:
      - models:/models:ro  # Read-only models
      - inference-cache:/cache
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/models/best_model.pth
      - CACHE_DIR=/cache

volumes:
  raw-data:
  processed-data:
  models:
  inference-cache:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: size=1g
EOF
```

### Step 6.3: Shared Model Registry

```yaml
cat > docker-compose-registry.yml << 'EOF'
version: '3.8'

services:
  # Model registry storage
  registry:
    image: postgres:15
    environment:
      - POSTGRES_DB=model_registry
      - POSTGRES_PASSWORD=secret
    volumes:
      - registry-db:/var/lib/postgresql/data

  # Model file storage
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - model-storage:/data
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=secretkey

  # Model version tracking
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://postgres:secret@registry/model_registry
      - MLFLOW_DEFAULT_ARTIFACT_ROOT=/mlflow/artifacts
    depends_on:
      - registry

volumes:
  registry-db:
  model-storage:
  mlflow-data:
EOF
```

```bash
# Start model registry
docker compose -f docker-compose-registry.yml up -d

# Access MLflow UI
echo "MLflow: http://localhost:5000"
echo "MinIO: http://localhost:9001"

# Cleanup
docker compose -f docker-compose-registry.yml down -v
```

✅ **Checkpoint**: You can manage ML models and datasets with volumes.

---

## Part 7: Performance Considerations

### Step 7.1: Volume Performance Comparison

```bash
# Create test script
cat > volume-performance.sh << 'EOF'
#!/bin/bash

echo "Testing volume performance..."

# Test 1: Named volume
echo "1. Named volume:"
docker volume create perf-named
time docker run --rm \
  -v perf-named:/data \
  alpine sh -c "dd if=/dev/zero of=/data/test bs=1M count=100"
docker volume rm perf-named

# Test 2: Bind mount
echo "2. Bind mount:"
mkdir -p /tmp/perf-bind
time docker run --rm \
  -v /tmp/perf-bind:/data \
  alpine sh -c "dd if=/dev/zero of=/data/test bs=1M count=100"
rm -rf /tmp/perf-bind

# Test 3: tmpfs
echo "3. tmpfs:"
time docker run --rm \
  --tmpfs /data:rw,size=200m \
  alpine sh -c "dd if=/dev/zero of=/data/test bs=1M count=100"

echo "Performance test complete!"
EOF

chmod +x volume-performance.sh
./volume-performance.sh
```

### Step 7.2: Read-Only Mounts for Performance

```yaml
cat > docker-compose-readonly.yml << 'EOF'
version: '3.8'

services:
  # Web server serving static files
  web:
    image: nginx:alpine
    volumes:
      # Static files read-only (better performance)
      - ./static:/usr/share/nginx/html:ro
      # Config read-only
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      # Logs writable
      - logs:/var/log/nginx
    ports:
      - "80:80"

  # ML inference with read-only models
  inference:
    image: pytorch/pytorch
    volumes:
      - models:/models:ro  # Models never change
      - cache:/cache  # Writable cache
    environment:
      - MODEL_DIR=/models

volumes:
  logs:
  models:
  cache:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: size=2g
EOF
```

### Step 7.3: Volume Options for Performance

```bash
# Create volume with performance options
docker volume create \
  --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=1g,uid=1000 \
  fast-cache

# Create volume with specific mount options
docker volume create \
  --driver local \
  --opt type=none \
  --opt device=/mnt/fast-ssd \
  --opt o=bind \
  ssd-storage

# Use in container
docker run -d \
  --name perf-app \
  -v fast-cache:/cache \
  -v ssd-storage:/data \
  alpine sleep 3600

# Cleanup
docker rm -f perf-app
docker volume rm fast-cache ssd-storage
```

✅ **Checkpoint**: You understand volume performance characteristics.

---

## Part 8: Volume Drivers and Plugins

### Step 8.1: NFS Volume Driver

```bash
# Install NFS utilities (if needed)
# sudo apt-get install nfs-common

# Create NFS volume (requires NFS server)
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/nfs/share \
  nfs-volume

# Use NFS volume
docker run -d \
  --name nfs-app \
  -v nfs-volume:/data \
  alpine sleep 3600

# Multiple containers can share NFS volume across hosts
```

### Step 8.2: Cloud Storage Volume (Conceptual)

```bash
# AWS EFS volume (example)
# Requires docker-volume-efs plugin

# Install plugin
# docker plugin install rexray/efs EFS_REGION=us-east-1

# Create EFS volume
# docker volume create \
#   --driver rexray/efs \
#   --name efs-volume \
#   --opt fileSystemId=fs-12345678

# Use in container
# docker run -v efs-volume:/data myapp
```

### Step 8.3: Custom Volume Plugin

```yaml
# Example: Using third-party volume plugin for distributed storage
cat > docker-compose-distributed.yml << 'EOF'
version: '3.8'

services:
  app1:
    image: alpine
    volumes:
      - shared-storage:/data
    command: sh -c 'echo "App1: $(hostname)" >> /data/log.txt && sleep 3600'

  app2:
    image: alpine
    volumes:
      - shared-storage:/data
    command: sh -c 'echo "App2: $(hostname)" >> /data/log.txt && sleep 3600'

volumes:
  shared-storage:
    driver: local  # In production, use distributed driver
    # Examples:
    # driver: rexray/efs  # AWS EFS
    # driver: pxd  # Portworx
    # driver: netshare:nfs  # NFS
EOF
```

✅ **Checkpoint**: You understand volume drivers and plugins.

---

## Part 9: Production Patterns

### Step 9.1: Volume Lifecycle Management

```yaml
cat > docker-compose-lifecycle.yml << 'EOF'
version: '3.8'

services:
  app:
    image: myapp
    volumes:
      # Application data (persisted)
      - app-data:/data
      # Configuration (external)
      - ./config:/config:ro
      # Logs (managed externally)
      - /var/log/app:/logs
      # Cache (ephemeral)
      - type: tmpfs
        target: /cache
        tmpfs:
          size: 500m

volumes:
  app-data:
    driver: local
    labels:
      backup: "daily"
      retention: "30d"
EOF
```

### Step 9.2: Multi-Environment Volume Strategy

```yaml
# Development
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  app:
    image: myapp
    volumes:
      # Bind mount for hot reload
      - ./src:/app/src
      - ./tests:/app/tests
      # Named volume for dependencies
      - node_modules:/app/node_modules

volumes:
  node_modules:
EOF

# Production
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  app:
    image: myapp
    volumes:
      # Only named volumes (no bind mounts)
      - app-data:/app/data
      - app-logs:/app/logs
    deploy:
      replicas: 3

volumes:
  app-data:
    driver: rexray/efs  # Distributed storage
  app-logs:
    driver: syslog
EOF
```

### Step 9.3: Disaster Recovery Setup

```bash
# Create disaster recovery script
cat > dr-backup.sh << 'EOF'
#!/bin/bash

VOLUMES=("db-data" "app-data" "models")
BACKUP_PATH="/backups/dr"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p ${BACKUP_PATH}

for vol in "${VOLUMES[@]}"; do
    echo "Backing up ${vol}..."

    docker run --rm \
        -v ${vol}:/source:ro \
        -v ${BACKUP_PATH}:/backup \
        alpine \
        tar czf /backup/${vol}_${TIMESTAMP}.tar.gz -C /source .

    # Upload to S3 or remote storage
    # aws s3 cp ${BACKUP_PATH}/${vol}_${TIMESTAMP}.tar.gz s3://my-backups/
done

echo "Disaster recovery backup complete!"
EOF

chmod +x dr-backup.sh
```

✅ **Checkpoint**: You can implement production volume patterns.

---

## Part 10: Troubleshooting and Best Practices

### Step 10.1: Common Issues

```bash
# Issue 1: Permission denied
# Solution: Check file ownership

# Create volume
docker volume create test-perms

# Run as non-root user
docker run --rm \
  -u 1000:1000 \
  -v test-perms:/data \
  alpine sh -c "echo 'test' > /data/file.txt"

# If permission denied, fix ownership:
docker run --rm \
  -v test-perms:/data \
  alpine chown -R 1000:1000 /data

# Issue 2: Volume not found
docker volume ls
docker volume inspect volume-name

# Issue 3: Volume full
docker system df -v
docker volume ls -qf dangling=true | xargs docker volume rm

# Issue 4: Slow performance
# Check volume driver and mount options
docker volume inspect volume-name --format '{{.Driver}}'
```

### Step 10.2: Volume Best Practices

```yaml
cat > docker-compose-best-practices.yml << 'EOF'
version: '3.8'

services:
  app:
    image: myapp
    volumes:
      # ✓ Use named volumes for data
      - app-data:/app/data

      # ✓ Read-only when possible
      - ./config:/config:ro

      # ✓ tmpfs for temporary files
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 100m

      # ✓ Specific paths, not root
      - logs:/app/logs

      # ✗ Avoid bind mounting root
      # - ./:/app  # Bad practice!

volumes:
  app-data:
    # ✓ Add labels for management
    labels:
      com.example.backup: "true"
      com.example.environment: "production"
  logs:
    # ✓ Set driver options
    driver: local
    driver_opts:
      type: none
      device: /var/log/myapp
      o: bind
EOF
```

### Step 10.3: Monitoring Volume Usage

```bash
# Create monitoring script
cat > monitor-volumes.sh << 'EOF'
#!/bin/bash

echo "Docker Volume Usage Report"
echo "=========================="
echo

# Overall system usage
echo "System Overview:"
docker system df

echo
echo "Volume Details:"
docker volume ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"

echo
echo "Volume Sizes:"
for vol in $(docker volume ls -q); do
    size=$(docker run --rm -v $vol:/data alpine du -sh /data 2>/dev/null | awk '{print $1}')
    echo "$vol: $size"
done

echo
echo "Dangling Volumes:"
docker volume ls -qf dangling=true
EOF

chmod +x monitor-volumes.sh
./monitor-volumes.sh
```

✅ **Checkpoint**: You can troubleshoot and follow volume best practices.

---

## Practical Challenges

### Challenge 1: Complete Backup System

**Requirements**:
- Automated daily backups of all volumes
- Retention policy (keep last 7 days)
- Backup verification
- Restore procedure documented
- Off-site backup to S3/cloud storage

### Challenge 2: ML Pipeline Storage

**Requirements**:
- Raw data volume (read-only for pipeline)
- Processed data volume
- Model storage with versioning
- Experiment tracking storage
- Cache for inference
- All with appropriate performance settings

### Challenge 3: Multi-Region Deployment

**Requirements**:
- Replicated database volumes across regions
- Shared read-only configuration
- Region-specific cache
- Centralized logging storage
- Disaster recovery strategy

---

## Summary

**What You Accomplished**:
✅ Mastered three volume types (named, bind mounts, tmpfs)
✅ Managed volume lifecycle operations
✅ Implemented data sharing between containers
✅ Created persistent database storage
✅ Built backup and restore strategies
✅ Managed ML models and datasets
✅ Optimized volume performance
✅ Used volume drivers and plugins
✅ Applied production volume patterns
✅ Troubleshooted volume issues

**Key Concepts Mastered**:
- Volume types and use cases
- Data persistence strategies
- Backup and disaster recovery
- Performance optimization
- Production best practices
- ML-specific volume patterns

**Volume Strategy**:
- **Development**: Bind mounts for hot reload
- **Staging**: Named volumes with backups
- **Production**: Distributed volumes with replication

---

## Next Steps

**Continue Learning**:
- **Exercise 06**: Production Deployment Strategies
- **Exercise 07**: Complete ML Application Containerization

---

**Exercise Version**: 1.0
**Last Updated**: October 2025
**Estimated Time**: 3-4 hours
**Difficulty**: Intermediate
