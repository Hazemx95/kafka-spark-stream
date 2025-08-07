#!/bin/bash


# This script sets up and tests the real-time SMS pipeline with production Kafka data

echo " Setting up Real-Time SMS Pipeline Testing Environment"
echo "========================================================"

# Create necessary directories
echo " Creating necessary directories..."
mkdir -p /home/homar/spark-kafka-stream/data_lake
mkdir -p /home/homar/spark-kafka-stream/checkpoints
mkdir -p /home/homar/spark-kafka-stream/scripts

# Set permissions
chmod 755 /home/homar/spark-kafka-stream/data_lake
chmod 755 /home/homar/spark-kafka-stream/checkpoints
chmod 755 /home/homar/spark-kafka-stream/scripts

echo " Directories created successfully"

# Create external network if it doesn't exist
echo " Setting up Docker network..."
if ! docker network ls | grep -q "mynet"; then
    docker network create mynet
    echo " Network 'mynet' created"
else
    echo " Network 'mynet' already exists"
fi

# Copy notebook to scripts directory
echo " Copying pipeline notebook..."
cp /home/homar/spark-kafka-stream/script/realtime_sms_pipeline.ipynb /home/homar/spark-kafka-stream/scripts/
echo " Notebook copied to scripts directory"

# Build custom Spark image if needed
echo " Building custom Spark image..."
cd /home/homar/spark-kafka-stream/docker/pyspark-kafka
if docker images | grep -q "drhazem95/spark-kafka-stream"; then
    echo " Custom Spark image already exists"
else
    echo "Building custom image..."
    docker image build -f Dockerfile.spark -t drhazem95/spark-kafka-stream .
    echo " Custom Spark image built successfully"
fi

# Start the services
echo " Starting Docker services..."
docker-compose -f pyspark_db.yml up -d

echo " Waiting for services to start..."
sleep 30

# Check service health
echo " Checking service health..."
echo " Jupyter/Spark: http://localhost:8888"
echo "  DBeaver: http://localhost:8978"
echo " PostgreSQL: localhost:5445"
echo " Vertica: localhost:15433"
echo " Spark UI: http://localhost:4040"

# Test Vertica connection
echo " Testing Vertica connection..."
timeout 60 bash -c 'until docker exec ci-vertica-db /opt/vertica/bin/vsql -U customer_insights -d customer_insights -c "SELECT 1;" 2>/dev/null; do sleep 2; done'
if [ $? -eq 0 ]; then
    echo " Vertica is ready and accessible"
else
    echo "  Vertica might take a few more minutes to be ready"
fi

# Test network connectivity
echo " Testing network connectivity..."
if docker exec spark-master ping -c 1 ci-vertica-db > /dev/null 2>&1; then
    echo " Network connectivity between Spark and Vertica is working"
else
    echo " Network connectivity issue detected"
fi

echo ""
echo " SETUP COMPLETE!"
echo "=================="
echo ""
echo " Next Steps:"
echo "1. Open Jupyter: http://localhost:8888"
echo "2. Open the realtime_sms_pipeline.ipynb notebook"
echo "3. Run the notebook cells to start the pipeline"
echo "4. Monitor in DBeaver: http://localhost:8978"
echo ""
echo " Configuration Summary:"
echo "- Kafka: Production topics from Unifonic"
echo "- Data Lake: Local directory (/home/homar/spark-kafka-stream/data_lake)"
echo "- Vertica: Container (ci-vertica-db:5433)"
echo "- Spark: Container with Vertica JDBC driver"
echo ""
echo "  Important Notes:"
echo "- Ensure VPN connection to Unifonic Kafka is active"
echo "- Production data will be processed and stored locally for testing"
echo "- Monitor the pipeline using Spark UI at http://localhost:4040"
echo ""

# Show running containers
echo " Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo " Ready to test real-time SMS pipeline with production data!"
