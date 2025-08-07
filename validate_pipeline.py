#!/usr/bin/env python3

"""
Real-Time SMS Pipeline Validation Script
This script validates the setup and configuration before running the pipeline
"""

import os
import socket
import subprocess
import sys
import time
from datetime import datetime

class PipelineValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def log_error(self, message):
        self.errors.append(message)
        print(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        print(f"✅ {message}")
        
    def check_directories(self):
        """Check if required directories exist"""
        print("\n📁 Checking directories...")
        
        required_dirs = [
            "/home/homar/spark-kafka-stream/data_lake",
            "/home/homar/spark-kafka-stream/checkpoints",
            "/home/homar/spark-kafka-stream/scripts"
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                self.log_success(f"Directory exists: {directory}")
            else:
                self.log_error(f"Directory missing: {directory}")
                
    def check_docker_containers(self):
        """Check if Docker containers are running"""
        print("\n🐳 Checking Docker containers...")
        
        required_containers = [
            "spark-master",
            "ci-vertica-db", 
            "dbeaver-client",
            "pg-db"
        ]
        
        try:
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                   capture_output=True, text=True)
            running_containers = result.stdout.strip().split('\n')
            
            for container in required_containers:
                if container in running_containers:
                    self.log_success(f"Container running: {container}")
                else:
                    self.log_error(f"Container not running: {container}")
                    
        except Exception as e:
            self.log_error(f"Failed to check Docker containers: {e}")
            
    def check_network_connectivity(self):
        """Check network connectivity between containers"""
        print("\n🌐 Checking network connectivity...")
        
        # Test Spark to Vertica connectivity
        try:
            result = subprocess.run([
                'docker', 'exec', 'spark-master', 
                'ping', '-c', '1', 'ci-vertica-db'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_success("Spark can reach Vertica container")
            else:
                self.log_error("Spark cannot reach Vertica container")
        except Exception as e:
            self.log_error(f"Failed to test network connectivity: {e}")
            
    def check_ports(self):
        """Check if required ports are accessible"""
        print("\n🔌 Checking port accessibility...")
        
        ports_to_check = [
            (8888, "Jupyter"),
            (8978, "DBeaver"), 
            (15433, "Vertica"),
            (5445, "PostgreSQL"),
            (4040, "Spark UI")
        ]
        
        for port, service in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            try:
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    self.log_success(f"{service} accessible on port {port}")
                else:
                    self.log_warning(f"{service} not accessible on port {port}")
            except Exception as e:
                self.log_warning(f"Failed to check {service} on port {port}: {e}")
            finally:
                sock.close()
                
    def check_vertica_status(self):
        """Check Vertica database status"""
        print("\n🗄️  Checking Vertica database...")
        
        try:
            result = subprocess.run([
                'docker', 'exec', 'ci-vertica-db',
                '/opt/vertica/bin/vsql', '-U', 'customer_insights', 
                '-d', 'customer_insights', '-c', 'SELECT 1;'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_success("Vertica database is ready")
            else:
                self.log_warning("Vertica database might still be initializing")
        except Exception as e:
            self.log_warning(f"Could not check Vertica status: {e}")
            
    def check_kafka_connectivity(self):
        """Check Kafka connectivity (basic test)"""
        print("\n📡 Checking Kafka connectivity...")
        
        # This is a basic check - actual Kafka connectivity requires VPN
        kafka_server = "strimzi-kafka-cluster-oci-preprod-kafka-bootstrap.strimzi-kafka-preprod:9092"
        
        try:
            # Try to resolve the hostname
            import socket
            socket.gethostbyname(kafka_server.split(':')[0])
            self.log_success("Kafka hostname can be resolved")
        except socket.gaierror:
            self.log_warning("Cannot resolve Kafka hostname - ensure VPN is connected")
            
    def check_notebook_files(self):
        """Check if notebook files exist"""
        print("\n📋 Checking notebook files...")
        
        notebook_path = "/home/homar/spark-kafka-stream/scripts/realtime_sms_pipeline.ipynb"
        
        if os.path.exists(notebook_path):
            self.log_success("Pipeline notebook found in scripts directory")
        else:
            self.log_error("Pipeline notebook not found in scripts directory")
            
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("📊 VALIDATION REPORT")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("🎉 ALL CHECKS PASSED!")
            print("🚀 Your pipeline is ready for testing!")
            
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
            print("\n🔧 Please fix the errors before running the pipeline")
            
        print("\n📋 Next Steps:")
        if not self.errors:
            print("1. Ensure VPN connection to Unifonic Kafka")
            print("2. Open Jupyter: http://localhost:8888")
            print("3. Run the realtime_sms_pipeline.ipynb notebook")
            print("4. Monitor results in DBeaver: http://localhost:8978")
        else:
            print("1. Fix the errors listed above")
            print("2. Run this validation script again")
            print("3. Ensure all Docker containers are running")
            
        return len(self.errors) == 0

def main():
    print("🔍 Real-Time SMS Pipeline Validation")
    print("====================================")
    print(f"⏰ Timestamp: {datetime.now()}")
    
    validator = PipelineValidator()
    
    # Run all validation checks
    validator.check_directories()
    validator.check_docker_containers()
    validator.check_network_connectivity()
    validator.check_ports()
    validator.check_vertica_status()
    validator.check_kafka_connectivity()
    validator.check_notebook_files()
    
    # Generate report
    success = validator.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
