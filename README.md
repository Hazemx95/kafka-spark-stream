# Real-Time SMS Pipeline Testing Guide

##  Overview

This setup allows you to test your real-time SMS pipeline using **production Kafka data from Unifonic** in a containerized environment before deploying to full production.

##  What This Setup Provides

###  **Data Flow**
```
Production Kafka Topics → Spark Streaming → Data Lake (Local) → Vertica (Container)
                                      ↓
                               Real-time Processing
                               Business Logic
                               Data Quality Checks
```

###  **Container Services**
- **Spark/Jupyter**: Main processing engine with your pipeline code
- **Vertica**: Database for storing processed SMS data
- **PostgreSQL**: Additional database for testing
- **DBeaver**: Web-based database client for monitoring

---

##  Quick Start

### 1. **Setup Environment**
```bash
# Run the setup script
cd /home/homar/spark-kafka-stream
./setup_pipeline_test.sh
```

### 2. **Validate Setup**
```bash
# Check if everything is configured correctly
python3 validate_pipeline.py
```

### 3. **Start Pipeline**
- Open Jupyter: http://localhost:8888
- Open `realtime_sms_pipeline.ipynb`
- Run all cells to start the pipeline

### 4. **Monitor Results**
- DBeaver: http://localhost:8978 (admin/admin123)
- Spark UI: http://localhost:4040
- Check data lake: `/home/homar/spark-kafka-stream/data_lake`

---

##  Pipeline Configuration

### 🔌 **Kafka Configuration (Production)**
- **Bootstrap Servers**: `strimzi-kafka-cluster-oci-preprod-kafka-bootstrap.strimzi-kafka-preprod:9092`
- **Topics**: 
  - FCDR Jasmin: 5 production topics
  - FCDR Telestax: 1 production topic  
  - ECDR: 2 production topics

###  **Data Storage (Test)**
- **Data Lake**: Local directory (`/home/homar/spark-kafka-stream/data_lake`)
- **Vertica**: Container database (`ci-vertica-db:5433`)
- **Format**: Parquet files with time-based partitioning

###  **Processing Configuration**
- **Trigger**: 1-minute micro-batches
- **Checkpointing**: Local directory for fault tolerance
- **Business Logic**: Same as production pipeline

---

##  Database Configuration

### **Vertica Container**
- **Host**: ci-vertica-db (container) / localhost:15433 (external)
- **Database**: customer_insights
- **Username**: customer_insights
- **Password**: customer_insights1
- **Table**: standard.fact_sms

### **PostgreSQL Container**
- **Host**: pg-db (container) / localhost:5445 (external)
- **Username**: postgres
- **Password**: P@ssw0rd

---

##  Monitoring & Validation

### **Real-time Monitoring**
1. **Spark UI**: http://localhost:4040
   - Monitor streaming queries
   - Check processing rates
   - View job execution details

2. **DBeaver**: http://localhost:8978
   - Query Vertica data
   - Validate data quality
   - Check record counts

3. **Data Lake Files**
   ```bash
   # Check parquet files
   ls -la /home/homar/spark-kafka-stream/data_lake/fact_sms/
   ```

### **Data Quality Checks**
The pipeline includes built-in data quality monitoring:
- Record count validation
- Schema validation
- Null value checks
- Message status distribution
- Processing lag monitoring

---

##  Troubleshooting

### **Common Issues & Solutions**

#### 1. **Kafka Connection Issues**
```bash
# Check VPN connection to Unifonic
ping strimzi-kafka-cluster-oci-preprod-kafka-bootstrap.strimzi-kafka-preprod

# Verify from inside container
docker exec spark-master ping strimzi-kafka-cluster-oci-preprod-kafka-bootstrap.strimzi-kafka-preprod
```

#### 2. **Vertica Connection Issues**
```bash
# Check Vertica container status
docker logs ci-vertica-db

# Test database connection
docker exec ci-vertica-db /opt/vertica/bin/vsql -U customer_insights -d customer_insights -c "SELECT 1;"
```

#### 3. **Network Connectivity**
```bash
# Test container-to-container communication
docker exec spark-master ping ci-vertica-db
docker exec spark-master ping pg-db
```

#### 4. **Pipeline Processing Issues**
- Check Spark UI for error messages
- Review Jupyter notebook cell outputs
- Verify checkpoint directory permissions
- Check data lake directory space

### **Container Management**
```bash
# Stop all services
docker-compose -f docker/pyspark-kafka/pyspark_db.yml down

# Start all services
docker-compose -f docker/pyspark-kafka/pyspark_db.yml up -d

# View logs
docker-compose -f docker/pyspark-kafka/pyspark_db.yml logs -f

# Check container status
docker ps
```

---

##  Performance Tuning

### **For Testing Environment**
- Processing trigger: 1 minute (can be reduced to 30s for faster testing)
- Batch size: 10,000 records per Vertica write
- Checkpoint interval: 10 minutes

### **For Production Deployment**
- Use actual S3 data lake configuration
- Connect to production Vertica cluster
- Adjust memory and CPU resources
- Enable monitoring and alerting

---

##  Security Considerations

### **Testing Environment**
- All passwords are for testing only
- Containers are isolated in custom network
- Data is processed locally

### **Production Environment**
- Use secure credential management
- Enable SSL/TLS for all connections
- Implement proper access controls
- Set up audit logging

---

##  Validation Checklist

Before running the pipeline, ensure:

- [ ] All Docker containers are running
- [ ] VPN connection to Unifonic Kafka is active
- [ ] Vertica database is accessible
- [ ] Data lake directories have proper permissions
- [ ] Network connectivity between containers works
- [ ] Validation script passes all checks

---

##  Expected Results

### **Data Processing**
- Real SMS data from production Kafka topics
- 1-minute processing latency
- Parquet files created in data lake
- Records inserted into Vertica table

### **Monitoring Outputs**
- Streaming query progress in Spark UI
- Data quality metrics in notebook
- Record counts in DBeaver
- File creation in data lake directory

---

##  Migration to Production

Once testing is successful:

1. **Update Configuration**
   - Change data lake to S3 bucket
   - Update Vertica to production cluster
   - Configure production Spark cluster

2. **Deploy Pipeline**
   - Use Kubernetes or Docker Swarm
   - Set up monitoring and alerting
   - Configure backup and recovery

3. **Monitor & Maintain**
   - Set up operational dashboards
   - Configure alerting rules
   - Implement data quality monitoring

---

##  Support

For issues or questions:
1. Check troubleshooting section above
2. Run validation script: `python3 validate_pipeline.py`
3. Review container logs: `docker-compose logs`
4. Check network connectivity between services

---

**Ready to test your real-time SMS pipeline with production data!**
