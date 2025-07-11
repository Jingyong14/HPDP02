"""
Malaysian Tourism Sentiment Analysis - Real-Time Pipeline
=======================================================

This main script orchestrates the entire Malaysian tourism sentiment analysis pipeline:
1. Check Docker services (Kafka, ES, Kibana)
2. Initialize dashboard connection
3. Start real-time Reddit producer
4. Start consumer with dual-model sentiment analysis
5. Monitor live sentiment analysis

Features:
- Real-time Kafka streaming ONLY
- Live sentiment analysis with both models
- Real-time log output with original text + labels
- Docker-based service management
- No file fallback - Pure streaming pipeline!

Author: Big Data & NLP Analytics Team
Date: July 8, 2025
"""

import os
import sys
import time
import logging
import subprocess
import threading
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import json
import socket

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/main_pipeline.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class MalaysianTourismRealTimePipeline:
    """Complete Malaysian Tourism Real-Time Sentiment Analysis Pipeline - STREAMING ONLY"""
    
    def __init__(self):
        """Initialize the real-time pipeline"""
        self.pipeline_threads = {}
        self.should_stop = False
        self.dashboard = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def start_docker_services(self) -> bool:
        """Start Docker services using docker-compose"""
        logger.info("🐳 Starting Docker services...")
        
        try:
            # Check if Docker is available
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.error("❌ Docker is not installed or not accessible")
                return False
            
            logger.info("✅ Docker is available")
            
            # Check if docker-compose.yml exists
            if not os.path.exists('docker-compose.yml'):
                logger.error("❌ docker-compose.yml not found in current directory")
                logger.info("💡 Please ensure docker-compose.yml is in the project root")
                return False
            
            # Start Docker Compose services
            logger.info("🚀 Starting Docker Compose services...")
            result = subprocess.run(['docker-compose', 'up', '-d'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info("✅ Docker services started successfully")
                logger.info("⏱️ Waiting for services to be ready...")
                
                # Wait for services to be healthy
                return self.wait_for_services()
            else:
                logger.error(f"❌ Failed to start Docker services: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Docker startup timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Docker startup failed: {e}")
            return False
    
    def wait_for_services(self) -> bool:
        """Wait for all services to be ready"""
        logger.info("🔍 Waiting for services to be ready...")
        
        max_wait = 120  # 2 minutes
        check_interval = 10  # 10 seconds
        elapsed = 0
        
        required_services = {
            'zookeeper': 2181,
            'kafka': 9092,
            'elasticsearch': 9200,
            'kibana': 5601
        }
        
        while elapsed < max_wait:
            all_ready = True
            
            for service, port in required_services.items():
                if self.check_service_running("localhost", port):
                    logger.info(f"✅ {service.capitalize()} is ready on port {port}")
                else:
                    logger.info(f"⏱️ Waiting for {service} on port {port}...")
                    all_ready = False
            
            if all_ready:
                logger.info("✅ All services are ready!")
                return True
            
            time.sleep(check_interval)
            elapsed += check_interval
        
        logger.error("❌ Services failed to start within timeout")
        return False
    
    def check_service_running(self, host: str, port: int) -> bool:
        """Check if a service is running on the given host and port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.error(f"❌ Service check failed for {host}:{port} - {e}")
            return False
    
    def check_docker_services(self) -> bool:
        """Check if Docker services are running"""
        logger.info("🐳 Checking Docker services...")
        
        required_services = {
            'kafka': 9092,
            'elasticsearch': 9200,
            'kibana': 5601,
            'zookeeper': 2181
        }
        
        all_running = True
        for service, port in required_services.items():
            if self.check_service_running("localhost", port):
                logger.info(f"✅ {service.capitalize()} is running on port {port}")
            else:
                logger.error(f"❌ {service.capitalize()} is not running on port {port}")
                all_running = False
        
        return all_running
    
    def start_dashboard_services(self) -> bool:
        """Initialize dashboard connection and create index patterns"""
        logger.info("📊 STEP 2: Initializing Dashboard Connection")
        logger.info("=" * 50)
        
        try:
            from dashboard import MalaysianTourismDashboard
            self.dashboard = MalaysianTourismDashboard()
            
            # Check if Elasticsearch is running
            if not self.check_service_running("localhost", 9200):
                logger.error("❌ Elasticsearch not running")
                return False
            
            logger.info("✅ Elasticsearch detected")
            
            # Setup Elasticsearch client
            if not self.dashboard.setup_elasticsearch_client():
                logger.error("❌ Dashboard connection failed")
                return False
            
            logger.info("✅ Dashboard connection established")
            
            # Create index template
            if self.dashboard.create_index_template():
                logger.info("✅ Index template created")
            else:
                logger.warning("⚠️ Index template creation failed")
            
            # Create index pattern
            if self.create_index_patterns():
                logger.info("✅ Index patterns ready")
            else:
                logger.warning("⚠️ Index patterns creation failed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")
            self.dashboard = None
            return False
    
    def start_realtime_producer(self) -> bool:
        """Start the real-time Reddit producer"""
        logger.info("📡 STEP 3: Starting Real-Time Producer")
        logger.info("=" * 50)
        logger.info("⚠️  STREAMING ONLY - No file saving!")
        
        try:
            # Import producer
            from reddit_tourism_producer import MalaysianTourismProducer
            
            # Create producer with Docker Kafka settings
            producer = MalaysianTourismProducer(
                bootstrap_servers='localhost:9092',  # Docker Kafka
                topic_name='malaysian-tourism-sentiment',
                fetch_interval=30,  # Fetch every 30 seconds
                posts_per_fetch=20  # Fetch 20 posts per cycle
            )
            
            # Start producer in a separate thread
            producer_thread = threading.Thread(
                target=producer.start_streaming,
                daemon=True
            )
            producer_thread.start()
            
            self.pipeline_threads['producer'] = producer_thread
            
            # Wait a bit to ensure producer starts
            time.sleep(3)
            
            if producer_thread.is_alive():
                logger.info("✅ Real-time streaming producer started")
                return True
            else:
                logger.error("❌ Producer thread failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start producer: {e}")
            return False
    
    def start_realtime_consumer(self, dashboard=None):
        """Start the real-time consumer with dashboard integration"""
        logger.info("🔍 STEP 4: Starting Real-Time Consumer")
        logger.info("=" * 50)
        
        try:
            # Import and start consumer with dashboard
            import reddit_tourism_consumer2
            
            # Start consumer in thread with dashboard
            consumer_thread = threading.Thread(
                target=reddit_tourism_consumer2.main,
                args=(dashboard,),
                daemon=True
            )
            consumer_thread.start()
            
            self.pipeline_threads['consumer'] = consumer_thread
            
            # Wait a bit to ensure consumer starts
            time.sleep(3)
            
            if consumer_thread.is_alive():
                logger.info("✅ Real-time streaming consumer started")
                return True
            else:
                logger.error("❌ Consumer thread failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start consumer: {e}")
            return False
    
    def create_index_patterns(self) -> bool:
        """Create Kibana index patterns"""
        logger.info("📊 Creating Kibana index patterns...")
        
        try:
            if not self.dashboard:
                logger.warning("⚠️ No dashboard connection - skipping index pattern creation")
                return False
            
            # Create index pattern using dashboard
            if self.dashboard.create_index_pattern():
                logger.info("✅ Index pattern created successfully")
                return True
            else:
                logger.warning("⚠️ Failed to create index pattern")
                return False
                
        except Exception as e:
            logger.error(f"❌ Index pattern creation failed: {e}")
            return False
    
    def import_kibana_objects(self) -> bool:
        """Import index patterns and dashboards from export.ndjson"""
        logger.info("📊 Importing Kibana index patterns and dashboards...")
        
        try:
            import requests
            
            # Check if export.ndjson exists
            export_file = 'export.ndjson'
            if not os.path.exists(export_file):
                logger.error(f"❌ {export_file} not found in current directory")
                logger.info("💡 Please ensure export.ndjson is in the project root")
                return False
            
            # Wait for Kibana to be ready
            kibana_url = "http://localhost:5601"
            max_wait = 60  # 1 minute
            wait_time = 0
            
            while wait_time < max_wait:
                try:
                    response = requests.get(f"{kibana_url}/api/status", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ Kibana is ready for import")
                        break
                except:
                    pass
                
                logger.info("⏱️ Waiting for Kibana to be ready...")
                time.sleep(5)
                wait_time += 5
            else:
                logger.error("❌ Kibana not ready for import")
                return False
            
            # Read the export file
            with open(export_file, 'r', encoding='utf-8') as f:
                ndjson_content = f.read()
            
            # Import objects using Kibana API
            import_url = f"{kibana_url}/api/saved_objects/_import"
            
            # Prepare the request
            files = {
                'file': ('export.ndjson', ndjson_content, 'application/ndjson')
            }
            
            headers = {
                'kbn-xsrf': 'true'
            }
            
            # Optional: Add overwrite parameter
            params = {
                'overwrite': 'true'  # Overwrite existing objects
            }
            
            logger.info("📤 Uploading index patterns and dashboards to Kibana...")
            
            response = requests.post(
                import_url,
                files=files,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('successCount', 0)
                errors = result.get('errors', [])
                
                logger.info(f"✅ Successfully imported {success_count} Kibana objects")
                
                if errors:
                    logger.warning(f"⚠️ Import warnings: {len(errors)} objects had issues")
                    for error in errors[:3]:  # Show first 3 errors
                        logger.warning(f"  - {error.get('error', {}).get('message', 'Unknown error')}")
                
                # Log what was imported
                success_results = result.get('successResults', [])
                for obj in success_results[:5]:  # Show first 5
                    obj_type = obj.get('meta', {}).get('type', 'unknown')
                    obj_title = obj.get('meta', {}).get('title', 'untitled')
                    logger.info(f"  ✅ {obj_type}: {obj_title}")
                
                return True
            else:
                logger.error(f"❌ Failed to import objects: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Kibana import failed: {e}")
            import traceback
            logger.error(f"Full error: {traceback.format_exc()}")
            return False
    
    def run_realtime_pipeline(self):
        """Run the complete real-time pipeline using Docker"""
        logger.info("🚀 MALAYSIAN TOURISM REAL-TIME SENTIMENT ANALYSIS")
        logger.info("=" * 60)
        logger.info("🎯 Docker-based pipeline:")
        logger.info("   1. Start Docker services (Kafka, ES, Kibana)")
        logger.info("   2. Initialize dashboard connection")
        logger.info("   3. Import index patterns and dashboards from export.ndjson")  # ✅ ONLY METHOD
        logger.info("   4. Start real-time Reddit producer")
        logger.info("   5. Start real-time sentiment consumer")
        logger.info("   6. Monitor live sentiment analysis")
        logger.info("=" * 60)
        
        try:
            # Step 1: Start Docker services
            if not self.start_docker_services():
                logger.error("❌ Failed to start Docker services")
                return False
            
            # Step 2: Initialize dashboard (NO index pattern creation)
            dashboard_ready = self.start_dashboard_connection_only()  # ✅ NEW METHOD
            if dashboard_ready:
                logger.info("✅ Dashboard connection ready")
            else:
                logger.warning("⚠️ Dashboard disabled - continuing without dashboard")
            
            # Step 3: Import ALL Kibana objects from export.ndjson
            logger.info("📋 STEP 3: Importing Index Patterns and Dashboards")
            logger.info("=" * 50)
            
            import_success = self.import_kibana_objects()
            if import_success:
                logger.info("✅ Index patterns and dashboards imported from export.ndjson")
            else:
                logger.error("❌ Import failed - pipeline may not work correctly")
                # You could return False here if import is critical
            
            # Step 4 & 5: Start producer and consumer
            logger.info("📋 STEP 4: Starting Real-Time Producer")
            logger.info("=" * 50)
            
            if not self.start_realtime_producer():
                logger.error("❌ Producer failed to start")
                return False
            
            # Step 5: Start consumer with dashboard
            logger.info("📋 STEP 5: Starting Real-Time Consumer")
            logger.info("=" * 50)
            
            if not self.start_realtime_consumer(dashboard=self.dashboard):
                logger.error("❌ Consumer failed to start")
                return False
            
            logger.info("✅ ALL SERVICES STARTED - Real-time pipeline active!")
            logger.info("🌐 Access URLs:")
            logger.info("   - Kafka UI: http://localhost:8080")
            logger.info("   - Elasticsearch: http://localhost:9200")
            logger.info("   - Kibana: http://localhost:5601")
            logger.info("   - Dashboard: http://localhost:5601/app/dashboards")
            
            # Step 6: Monitor the pipeline
            self.monitor_pipeline()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return False
        finally:
            logger.info("🧹 Pipeline cleanup completed")
    
    def cleanup_docker_services(self):
        """Clean up Docker services"""
        logger.info("🧹 Cleaning up Docker services...")
        
        try:
            result = subprocess.run(['docker-compose', 'down'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                logger.info("✅ Docker services stopped")
            else:
                logger.warning(f"⚠️ Docker cleanup warning: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ Docker cleanup failed: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.should_stop = True
        self.cleanup_docker_services()
        sys.exit(0)
    
    def monitor_pipeline(self):
        """Monitor the running pipeline"""
        logger.info("📊 PIPELINE MONITORING - Press Ctrl+C to stop")
        logger.info("=" * 50)
        
        try:
            while not self.should_stop:
                time.sleep(10)  # Check every 10 seconds
                
                # Check if threads are still alive
                producer_alive = self.pipeline_threads.get('producer', {}).is_alive() if 'producer' in self.pipeline_threads else False
                consumer_alive = self.pipeline_threads.get('consumer', {}).is_alive() if 'consumer' in self.pipeline_threads else False
                
                if not producer_alive:
                    logger.warning("⚠️ Producer thread stopped")
                if not consumer_alive:
                    logger.warning("⚠️ Consumer thread stopped")
                
                # Log status every minute
                if int(time.time()) % 60 == 0:
                    logger.info(f"📊 Pipeline status: Producer={producer_alive}, Consumer={consumer_alive}")
                
        except KeyboardInterrupt:
            logger.info("🛑 Pipeline stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")

    def start_dashboard_connection_only(self) -> bool:
        """Initialize dashboard connection WITHOUT creating index patterns (they come from NDJSON)"""
        logger.info("📊 STEP 2: Initializing Dashboard Connection")
        logger.info("=" * 50)
        
        try:
            from dashboard import MalaysianTourismDashboard
            self.dashboard = MalaysianTourismDashboard()
            
            # Check if Elasticsearch is running
            if not self.check_service_running("localhost", 9200):
                logger.error("❌ Elasticsearch not running")
                return False
            
            logger.info("✅ Elasticsearch detected")
            
            # Setup Elasticsearch client
            if not self.dashboard.setup_elasticsearch_client():
                logger.error("❌ Dashboard connection failed")
                return False
            
            logger.info("✅ Dashboard connection established")
            
            # ✅ FIXED: Only create index template, NOT index patterns
            if self.dashboard.create_index_template():
                logger.info("✅ Index template created")
            else:
                logger.warning("⚠️ Index template creation failed")
            
            # ❌ REMOVED: Don't create index patterns here - they come from NDJSON
            # if self.create_index_patterns():
            #     logger.info("✅ Index patterns ready")
            # else:
            #     logger.warning("⚠️ Index patterns creation failed")
            
            logger.info("ℹ️  Index patterns will be imported from export.ndjson")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")
            self.dashboard = None
            return False
    
def main():
    """Main entry point"""
    logger.info("🎯 STARTING MALAYSIAN TOURISM SENTIMENT ANALYSIS PIPELINE")
    logger.info("=" * 60)
    
    try:
        # Create and run pipeline
        pipeline = MalaysianTourismRealTimePipeline()
        success = pipeline.run_realtime_pipeline()
        
        if success:
            logger.info("✅ Pipeline completed successfully!")
            return 0
        else:
            logger.error("❌ Pipeline failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Pipeline interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
