"""
Malaysian Tourism Sentiment Analysis Dashboard
=============================================

This dashboard module integrates Elasticsearch and Kibana for real-time
sentiment analysis visualization of Malaysian tourism data.

Features:
- Elasticsearch data indexing from consumer
- Kibana dashboard auto-creation
- Real-time sentiment histogram
- Automatic service management
- Time-based filtering and analytics

Author: Big Data & NLP Analytics Team
Date: July 4, 2025
"""

import os
import sys
import json
import time
import logging
import requests
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MalaysianTourismDashboard:
    """Elasticsearch + Kibana dashboard for Malaysian tourism sentiment analysis"""
    
    def __init__(self, 
                 elasticsearch_host: str = "localhost:9200",
                 kibana_host: str = "localhost:5601",
                 index_name: str = "malaysian-tourism-sentiment"):
        """Initialize dashboard with Elasticsearch and Kibana configuration"""
        
        self.elasticsearch_host = elasticsearch_host
        self.kibana_host = kibana_host
        self.index_name = index_name
        
        # Service management
        self.services = {}
        self.running = False
        
        # Elasticsearch client
        self.es = None
        
        # Dashboard configuration
        self.dashboard_config = {
            'refresh_interval': 30,  # seconds
            'data_retention_days': 30,
            'max_documents': 10000
        }
        
        logger.info(f"✅ Dashboard initialized")
        logger.info(f"📊 Elasticsearch: {elasticsearch_host}")
        logger.info(f"📊 Kibana: {kibana_host}")
        logger.info(f"📊 Index: {index_name}")
    
    def find_elasticsearch_installation(self) -> Optional[str]:
        """Find Elasticsearch installation directory"""
        possible_locations = [
            os.environ.get('ELASTICSEARCH_HOME'),
            'C:\\Users\\venus\\Downloads\\elasticsearch\\elasticsearch-7.17.20',
            'C:\\elasticsearch',
            'C:\\Program Files\\Elastic\\Elasticsearch',
            '/usr/share/elasticsearch',
            '/opt/elasticsearch',
            str(Path.home() / 'elasticsearch')
        ]
        
        for location in possible_locations:
            if location and Path(location).exists():
                bin_dir = Path(location) / 'bin'
                if bin_dir.exists():
                    if os.name == 'nt':
                        es_script = bin_dir / 'elasticsearch.bat'
                    else:
                        es_script = bin_dir / 'elasticsearch'
                    
                    if es_script.exists():
                        logger.info(f"✅ Elasticsearch found at: {location}")
                        return str(location)
        
        logger.error("❌ Elasticsearch installation not found")
        return None
    
    def find_kibana_installation(self) -> Optional[str]:
        """Find Kibana installation directory"""
        possible_locations = [
            os.environ.get('KIBANA_HOME'),
            'C:\\Users\\venus\\Downloads\\kibana\\kibana-7.17.20-windows-x86_64',
            'C:\\kibana',
            'C:\\Program Files\\Elastic\\Kibana',
            '/usr/share/kibana',
            '/opt/kibana',
            str(Path.home() / 'kibana')
        ]
        
        for location in possible_locations:
            if location and Path(location).exists():
                bin_dir = Path(location) / 'bin'
                if bin_dir.exists():
                    if os.name == 'nt':
                        kibana_script = bin_dir / 'kibana.bat'
                    else:
                        kibana_script = bin_dir / 'kibana'
                    
                    if kibana_script.exists():
                        logger.info(f"✅ Kibana found at: {location}")
                        return str(location)
        
        logger.error("❌ Kibana installation not found")
        return None
    
    def check_service_running(self, host: str, port: int) -> bool:
        """Check if a service is running on given host:port with HTTP check for web services"""
        try:
            if port in [9200, 5601]:  # Elasticsearch and Kibana are HTTP services
                import requests
                response = requests.get(f"http://{host}:{port}", timeout=5)
                return response.status_code == 200
            else:
                # For other services, use socket check
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(3)
                    result = s.connect_ex((host.split(':')[0], port))
                    return result == 0
        except Exception as e:
            logger.debug(f"Service check failed for {host}:{port}: {e}")
            return False
    
    def start_elasticsearch(self) -> bool:
        """Start Elasticsearch service with improved startup process"""
        logger.info("🔧 Starting Elasticsearch...")
        
        # Check if already running
        if self.check_service_running("localhost", 9200):
            logger.info("✅ Elasticsearch already running on port 9200")
            return True
        
        # Find installation
        es_home = self.find_elasticsearch_installation()
        if not es_home:
            logger.error("❌ Elasticsearch installation not found")
            return False
        
        try:
            bin_dir = Path(es_home) / 'bin'
            if os.name == 'nt':
                es_script = bin_dir / 'elasticsearch.bat'
            else:
                es_script = bin_dir / 'elasticsearch'
            
            logger.info(f"🚀 Starting Elasticsearch: {es_script}")
            
            # Set environment variables for Elasticsearch
            env = os.environ.copy()
            env['ES_HOME'] = str(es_home)
            env['ES_PATH_CONF'] = str(Path(es_home) / 'config')
            
            # For Java 17+ compatibility
            env['ES_JAVA_OPTS'] = '-Xms512m -Xmx1g'
            
            # Start Elasticsearch with proper environment
            es_process = subprocess.Popen(
                [str(es_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                cwd=str(es_home),
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            self.services['elasticsearch'] = es_process
            
            # Monitor startup with real-time output
            logger.info("⏱️ Waiting for Elasticsearch to start...")
            max_wait = 180  # 3 minutes
            startup_detected = False
            
            for i in range(max_wait):
                # Check if process is still running
                if es_process.poll() is not None:
                    # Process died, get error output
                    remaining_output = es_process.stdout.read()
                    logger.error(f"❌ Elasticsearch process died!")
                    logger.error(f"Final output: {remaining_output}")
                    return False
                
                # Read any available output
                try:
                    import select
                    if hasattr(select, 'select'):
                        ready, _, _ = select.select([es_process.stdout], [], [], 0.1)
                        if ready:
                            line = es_process.stdout.readline()
                            if line:
                                logger.info(f"📋 ES: {line.strip()}")
                                # Look for startup indicators
                                if "started" in line.lower() or "green" in line.lower():
                                    startup_detected = True
                except:
                    pass
                
                # Check if service is responding
                if self.check_service_running("localhost", 9200):
                    logger.info("✅ Elasticsearch started successfully")
                    return True
                
                # Progress feedback
                if i % 15 == 0 and i > 0:
                    logger.info(f"⏳ Still waiting... ({i}/{max_wait} seconds)")
                
                time.sleep(1)
            
            logger.error("❌ Elasticsearch failed to start within timeout")
            return False
        
        except Exception as e:
            logger.error(f"❌ Failed to start Elasticsearch: {e}")
            return False
    
    def start_kibana(self) -> bool:
        """Start Kibana service"""
        logger.info("🔧 Starting Kibana...")
        
        # Check if already running
        if self.check_service_running("localhost", 5601):
            logger.info("✅ Kibana already running on port 5601")
            return True
        
        # Find installation
        kibana_home = self.find_kibana_installation()
        if not kibana_home:
            logger.error("❌ Kibana installation not found")
            return False
        
        try:
            bin_dir = Path(kibana_home) / 'bin'
            if os.name == 'nt':
                kibana_script = bin_dir / 'kibana.bat'
            else:
                kibana_script = bin_dir / 'kibana'
            
            logger.info(f"🚀 Starting Kibana: {kibana_script}")
            
            # Start Kibana
            kibana_process = subprocess.Popen(
                [str(kibana_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(kibana_home)
            )
            
            self.services['kibana'] = kibana_process
            
            # Wait for Kibana to start
            logger.info("⏱️ Waiting for Kibana to start...")
            max_wait = 120  # 2 minutes
            
            for i in range(max_wait):
                if self.check_service_running("localhost", 5601):
                    logger.info("✅ Kibana started successfully")
                    return True
                time.sleep(1)
            
            logger.error("❌ Kibana failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start Kibana: {e}")
            return False
    
    def setup_elasticsearch_client(self) -> bool:
        """Setup Elasticsearch client connection with proper v7.x configuration"""
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔧 Setting up Elasticsearch client (attempt {attempt + 1}/{max_retries})")
                
                # Use proper Elasticsearch v7.x configuration
                from elasticsearch import Elasticsearch
                
                # Proper configuration with scheme specified
                self.es = Elasticsearch(
                    hosts=[{
                        'host': 'localhost',
                        'port': 9200,
                        'scheme': 'http'
                    }]
                )
                
                # Test connection with ping
                if self.es.ping():
                    logger.info("✅ Elasticsearch client connected")
                    
                    # Try to get basic info
                    try:
                        info = self.es.info()
                        logger.info(f"📊 Elasticsearch version: {info.get('version', {}).get('number', 'unknown')}")
                        return True
                    except Exception as e:
                        logger.warning(f"⚠️ Info check failed: {e}")
                        return True  # Connection works, info can fail
                else:
                    logger.warning(f"❌ Elasticsearch ping failed (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
        
            except Exception as e:
                logger.warning(f"❌ Elasticsearch client setup failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

        logger.error("❌ All Elasticsearch connection attempts failed")
        return False
    
    def create_index_template(self) -> bool:
        """Create Elasticsearch index template for sentiment data (v7.x compatible)"""
        try:
            # Use v7.x template format
            template_body = {
                "index_patterns": [f"{self.index_name}-*"],
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index.refresh_interval": "5s"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "sentiment_label": {"type": "keyword"},
                        "confidence_score": {"type": "float"},
                        "sentiment_score": {"type": "float"},
                        "original_text": {"type": "text"},
                        "processed_text": {"type": "text"},
                        "method_used": {"type": "keyword"},
                        "content_type": {"type": "keyword"},
                        "is_malaysia_related": {"type": "boolean"},
                        "title": {"type": "text"},
                        "subreddit": {"type": "keyword"},
                        "author": {"type": "keyword"},
                        "score": {"type": "integer"},
                        "text_length": {"type": "integer"}
                    }
                }
            }
            
            # Use v7.x template API with body parameter
            self.es.indices.put_template(
                name=f"{self.index_name}-template",
                body=template_body
            )
            
            logger.info(f"✅ Index template created: {self.index_name}-template")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create index template: {e}")
            return False
    
    def index_document(self, document: Dict) -> bool:
        """Index a single document to Elasticsearch"""
        try:
            if not self.es:
                return False
                
            # Add timestamp if not present
            if '@timestamp' not in document:
                document['@timestamp'] = datetime.now().isoformat()
            
            # Index document
            response = self.es.index(
                index=f"{self.index_name}-{datetime.now().strftime('%Y.%m.%d')}",
                body=document,
                refresh=True
            )
            
            return response.get('result') in ['created', 'updated']
            
        except Exception as e:
            logger.error(f"❌ Failed to index document: {e}")
            return False
    
    def create_kibana_dashboard(self) -> bool:
        """Create Kibana dashboard with sentiment histogram (v7.x compatible)"""
        try:
            # Check if Kibana is running first
            if not self.check_service_running('localhost', 5601):
                logger.warning("⚠️ Kibana not running - skipping dashboard creation")
                return False
            
            # Kibana 7.x dashboard configuration - each object on separate line
            dashboard_objects = [
                {
                    "id": "sentiment-histogram",
                    "type": "visualization",
                    "attributes": {
                        "title": "Malaysian Tourism Sentiment Distribution",
                        "type": "histogram",
                        "params": {
                            "grid": {"categoryLines": False, "style": {"color": "#eee"}},
                            "categoryAxes": [{
                                "id": "CategoryAxis-1",
                                "type": "category",
                                "position": "bottom",
                                "show": True,
                                "style": {},
                                "scale": {"type": "linear"},
                                "labels": {"show": True, "truncate": 100},
                                "title": {}
                            }],
                            "valueAxes": [{
                                "id": "ValueAxis-1",
                                "name": "LeftAxis-1",
                                "type": "value",
                                "position": "left",
                                "show": True,
                                "style": {},
                                "scale": {"type": "linear", "mode": "normal"},
                                "labels": {"show": True, "rotate": 0, "filter": False, "truncate": 100},
                                "title": {"text": "Count"}
                            }],
                            "seriesParams": [{
                                "show": True,
                                "type": "histogram",
                                "mode": "stacked",
                                "data": {"label": "Count", "id": "1"},
                                "valueAxis": "ValueAxis-1",
                                "drawLinesBetweenPoints": True,
                                "showCircles": True
                            }],
                            "addTooltip": True,
                            "addLegend": True,
                            "legendPosition": "right",
                            "times": [],
                            "addTimeMarker": False
                        },
                        "aggs": [
                            {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                            {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {
                                "field": "sentiment_label",
                                "size": 10,
                                "order": "desc",
                                "orderBy": "1"
                            }}
                        ]
                    }
                },
                {
                    "id": "sentiment-dashboard",
                    "type": "dashboard",
                    "attributes": {
                        "title": "Malaysian Tourism Sentiment Dashboard",
                        "panelsJSON": json.dumps([{
                            "gridData": {"x": 0, "y": 0, "w": 24, "h": 15, "i": "1"},
                            "panelIndex": "1",
                            "embeddableConfig": {},
                            "panelRefName": "panel_1"
                        }]),
                        "references": [{
                            "name": "panel_1",
                            "type": "visualization",
                            "id": "sentiment-histogram"
                        }]
                    }
                }
            ]
            
            # Convert to NDJSON format - each object on a separate line
            ndjson_content = '\n'.join(json.dumps(obj) for obj in dashboard_objects)
            
            # Debug: Save NDJSON to file for inspection
            with open('debug_dashboard.ndjson', 'w') as f:
                f.write(ndjson_content)
            logger.info("🔍 Dashboard NDJSON saved to debug_dashboard.ndjson")
            
            # Create dashboard via Kibana API (v7.x compatible)
            kibana_url = f"http://{self.kibana_host}/api/saved_objects/_import"
            
            # Use multipart form data for v7.x with proper NDJSON
            import requests
            
            files = {
                'file': ('dashboard.ndjson', ndjson_content, 'application/x-ndjson')
            }
            
            logger.info(f"🚀 Sending dashboard to: {kibana_url}")
            response = requests.post(
                kibana_url,
                headers={'kbn-xsrf': 'true'},
                files=files,
                timeout=30
            )
            
            logger.info(f"📊 Response status: {response.status_code}")
            logger.info(f"📊 Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Kibana dashboard created successfully")
                logger.info(f"📊 Dashboard available at: http://{self.kibana_host}/app/dashboards#/view/sentiment-dashboard")
                return True
            else:
                logger.warning(f"⚠️ Dashboard creation failed: {response.status_code}")
                logger.warning(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create Kibana dashboard: {e}")
            return False
    
    def start_services(self) -> bool:
        """Start dashboard services using Docker"""
        logger.info("🐳 STARTING DASHBOARD SERVICES WITH DOCKER")
        logger.info("=" * 50)
        
        try:
            # Check if Docker services are already running
            status = self.check_docker_services_status()
            
            if status['elasticsearch'] and status['kibana']:
                logger.info("✅ Docker services already running")
            else:
                # Start Docker services
                if not self.start_docker_services():
                    logger.error("❌ Failed to start Docker services")
                    return False
            
            # Setup Elasticsearch client
            if not self.setup_elasticsearch_client():
                logger.error("❌ Failed to connect to Elasticsearch")
                return False
            
            # Create index template
            if not self.create_index_template():
                logger.warning("⚠️ Failed to create index template")
            
            logger.info("✅ Dashboard services ready")
            logger.info(f"🌐 Elasticsearch: http://localhost:9200")
            logger.info(f"🌐 Kibana: http://localhost:5601")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start services: {e}")
            return False
    
    def start_docker_services(self) -> bool:
        """Start Elasticsearch and Kibana using Docker Compose"""
        logger.info("🐳 Starting Docker services (Elasticsearch + Kibana)")
        logger.info("=" * 50)
        
        try:
            import subprocess
            import time
            
            # Check if Docker is installed
            try:
                subprocess.run(['docker', '--version'], check=True, capture_output=True)
                logger.info("✅ Docker is installed")
            except subprocess.CalledProcessError:
                logger.error("❌ Docker is not installed or not in PATH")
                return False
            
            # Check if docker-compose.yml exists
            if not os.path.exists('docker-compose.yml'):
                logger.error("❌ docker-compose.yml not found")
                logger.info("💡 Please create docker-compose.yml in project root")
                return False
            
            # Start services
            logger.info("🚀 Starting Docker Compose services...")
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker services started")
                logger.info("⏱️ Waiting for services to be ready...")
                
                # Wait for services to be healthy
                self.wait_for_docker_services()
                return True
            else:
                logger.error(f"❌ Failed to start Docker services: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Docker startup failed: {e}")
            return False

    def wait_for_docker_services(self) -> bool:
        """Wait for Docker services to be healthy"""
        import time
        
        max_wait = 180  # 3 minutes
        check_interval = 10  # 10 seconds
        elapsed = 0
        
        logger.info("🔍 Waiting for services to be healthy...")
        
        while elapsed < max_wait:
            try:
                # Check Elasticsearch health
                es_healthy = self.check_service_running("localhost", 9200)
                kibana_healthy = self.check_service_running("localhost", 5601)
                
                if es_healthy and kibana_healthy:
                    logger.info("✅ All services are healthy")
                    return True
                
                if es_healthy:
                    logger.info("✅ Elasticsearch is healthy")
                else:
                    logger.info("⏱️ Waiting for Elasticsearch...")
                
                if kibana_healthy:
                    logger.info("✅ Kibana is healthy")
                else:
                    logger.info("⏱️ Waiting for Kibana...")
                
                time.sleep(check_interval)
                elapsed += check_interval
                
            except Exception as e:
                logger.warning(f"⚠️ Health check error: {e}")
                time.sleep(check_interval)
                elapsed += check_interval
        
        logger.error("❌ Services failed to become healthy within timeout")
        return False

    def stop_docker_services(self) -> bool:
        """Stop Docker services"""
        logger.info("🛑 Stopping Docker services...")
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['docker-compose', 'down'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker services stopped")
                return True
            else:
                logger.error(f"❌ Failed to stop Docker services: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Docker stop failed: {e}")
            return False

    def check_docker_services_status(self) -> Dict[str, bool]:
        """Check status of Docker services"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['docker-compose', 'ps', '--services', '--filter', 'status=running'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n')
                return {
                    'elasticsearch': 'elasticsearch' in running_services,
                    'kibana': 'kibana' in running_services,
                    'docker_available': True
                }
            else:
                return {
                    'elasticsearch': False,
                    'kibana': False,
                    'docker_available': False
                }
                
        except Exception as e:
            logger.error(f"❌ Docker status check failed: {e}")
            return {
                'elasticsearch': False,
                'kibana': False,
                'docker_available': False
            }

    def debug_elasticsearch_startup(self) -> Dict[str, Any]:
        """Debug Elasticsearch startup issues"""
        debug_info = {
            'java_version': 'unknown',
            'java_home': os.environ.get('JAVA_HOME', 'not_set'),
            'path_contains_java': False,
            'elasticsearch_home': None,
            'elasticsearch_config': None,
            'port_9200_open': False,
            'elasticsearch_process_running': False
        }
        
        try:
            # Check Java version
            java_result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if java_result.returncode == 0:
                debug_info['java_version'] = java_result.stderr.split('\n')[0] if java_result.stderr else 'found'
            else:
                debug_info['java_version'] = 'not_found'
        except:
            debug_info['java_version'] = 'not_found'
        
        # Check if java is in PATH
        debug_info['path_contains_java'] = any('java' in path.lower() for path in os.environ.get('PATH', '').split(os.pathsep))
        
        # Check Elasticsearch installation
        debug_info['elasticsearch_home'] = self.find_elasticsearch_installation()
        
        # Check if port 9200 is open
        debug_info['port_9200_open'] = self.check_service_running('localhost', 9200)
        
        # Check if Elasticsearch process is running
        if 'elasticsearch' in self.services:
            process = self.services['elasticsearch']
            debug_info['elasticsearch_process_running'] = process.poll() is None
        
        return debug_info

    def test_kibana_saved_objects(self) -> Dict[str, Any]:
        """Test Kibana saved objects creation and verify data"""
        logger.info("🧪 Testing Kibana saved objects...")
        
        test_results = {
            'kibana_running': False,
            'api_accessible': False,
            'dashboard_created': False,
            'saved_objects_found': [],
            'index_pattern_exists': False,
            'test_data_indexed': False,
            'visualization_data': {},
            'errors': []
        }
        
        try:
            # Step 1: Check if Kibana is running
            if not self.check_service_running('localhost', 5601):
                test_results['errors'].append("Kibana not running on port 5601")
                logger.error("❌ Kibana not running")
                return test_results
            
            test_results['kibana_running'] = True
            logger.info("✅ Kibana is running")
            
            # Step 2: Test Kibana API accessibility
            try:
                import requests
                response = requests.get(f"http://{self.kibana_host}/api/status", timeout=10)
                if response.status_code == 200:
                    test_results['api_accessible'] = True
                    logger.info("✅ Kibana API accessible")
                else:
                    test_results['errors'].append(f"Kibana API returned {response.status_code}")
            except Exception as e:
                test_results['errors'].append(f"Kibana API error: {e}")
                logger.error(f"❌ Kibana API error: {e}")
            
            # Step 3: Create test data in Elasticsearch
            test_data = [
                {
                    'sentiment_label': 'positive',
                    'confidence_score': 0.85,
                    'sentiment_score': 0.8,
                    'original_text': 'Malaysia is a beautiful country to visit!',
                    'processed_text': 'malaysia beautiful country visit',
                    'method_used': 'naive_bayes',
                    'content_type': 'post',
                    'is_malaysia_related': True,
                    'title': 'Best places to visit in Malaysia',
                    'subreddit': 'malaysia',
                    'author': 'test_user',
                    'score': 10,
                    'text_length': 42
                },
                {
                    'sentiment_label': 'negative',
                    'confidence_score': 0.75,
                    'sentiment_score': -0.6,
                    'original_text': 'Traffic in Kuala Lumpur is terrible',
                    'processed_text': 'traffic kuala lumpur terrible',
                    'method_used': 'lstm',
                    'content_type': 'comment',
                    'is_malaysia_related': True,
                    'title': 'KL traffic issues',
                    'subreddit': 'malaysia',
                    'author': 'test_user2',
                    'score': 5,
                    'text_length': 35
                },
                {
                    'sentiment_label': 'neutral',
                    'confidence_score': 0.65,
                    'sentiment_score': 0.1,
                    'original_text': 'Information about Malaysian visa requirements',
                    'processed_text': 'information malaysian visa requirements',
                    'method_used': 'naive_bayes',
                    'content_type': 'post',
                    'is_malaysia_related': True,
                    'title': 'Visa info',
                    'subreddit': 'travel',
                    'author': 'test_user3',
                    'score': 8,
                    'text_length': 44
                }
            ]
            
            # Index test data
            indexed_count = 0
            for doc in test_data:
                if self.index_document(doc):
                    indexed_count += 1
            
            if indexed_count > 0:
                test_results['test_data_indexed'] = True
                logger.info(f"✅ {indexed_count} test documents indexed")
            else:
                test_results['errors'].append("Failed to index test data")
                logger.error("❌ Failed to index test data")
            
            # Wait for data to be available
            import time
            time.sleep(2)
            
            # Step 4: Create dashboard and test
            dashboard_created = self.create_kibana_dashboard()
            test_results['dashboard_created'] = dashboard_created
            
            if dashboard_created:
                logger.info("✅ Dashboard creation attempted")
            else:
                test_results['errors'].append("Dashboard creation failed")
                logger.error("❌ Dashboard creation failed")
            
            # Step 5: Check saved objects
            saved_objects = self.get_saved_objects()
            test_results['saved_objects_found'] = saved_objects
            
            if saved_objects:
                logger.info(f"✅ Found {len(saved_objects)} saved objects")
                for obj in saved_objects:
                    logger.info(f"📋 {obj['type']}: {obj['id']} - {obj.get('title', 'No title')}")
            else:
                test_results['errors'].append("No saved objects found")
                logger.warning("⚠️ No saved objects found")
            
            # Step 6: Test index pattern
            index_pattern_exists = self.check_index_pattern()
            test_results['index_pattern_exists'] = index_pattern_exists
            
            if index_pattern_exists:
                logger.info("✅ Index pattern exists")
            else:
                logger.warning("⚠️ Index pattern not found")
            
            # Step 7: Test visualization data
            viz_data = self.get_visualization_data()
            test_results['visualization_data'] = viz_data
            
            if viz_data:
                logger.info("✅ Visualization data retrieved")
                logger.info(f"📊 Data summary: {viz_data}")
            else:
                test_results['errors'].append("No visualization data found")
                logger.warning("⚠️ No visualization data found")
            
            # Step 8: Generate test report
            self.generate_test_report(test_results)
            
            return test_results
            
        except Exception as e:
            test_results['errors'].append(f"Test failed: {e}")
            logger.error(f"❌ Test failed: {e}")
            return test_results

    def get_saved_objects(self) -> List[Dict]:
        """Get all saved objects from Kibana"""
        try:
            import requests
            response = requests.get(
                f"http://{self.kibana_host}/api/saved_objects/_find",
                headers={'kbn-xsrf': 'true'},
                params={'type': ['dashboard', 'visualization', 'index-pattern']},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                saved_objects = []
                
                for obj in data.get('saved_objects', []):
                    saved_objects.append({
                        'id': obj.get('id'),
                        'type': obj.get('type'),
                        'title': obj.get('attributes', {}).get('title', 'No title'),
                        'created_at': obj.get('created_at'),
                        'updated_at': obj.get('updated_at')
                    })
                
                return saved_objects
            else:
                logger.error(f"❌ Failed to get saved objects: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting saved objects: {e}")
            return []

    def check_index_pattern(self) -> bool:
        """Check if index pattern exists in Kibana"""
        try:
            import requests
            response = requests.get(
                f"http://{self.kibana_host}/api/saved_objects/_find",
                headers={'kbn-xsrf': 'true'},
                params={'type': 'index-pattern', 'search': f'{self.index_name}*'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return len(data.get('saved_objects', [])) > 0
            else:
                logger.error(f"❌ Failed to check index pattern: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking index pattern: {e}")
            return False

    def create_index_pattern(self) -> bool:
        """Create index pattern in Kibana"""
        try:
            import requests
            pattern_data = {
                "attributes": {
                    "title": f"{self.index_name}-*",
                    "timeFieldName": "@timestamp"
                }
            }
            
            response = requests.post(
                f"http://{self.kibana_host}/api/saved_objects/index-pattern/{self.index_name}-pattern",
                headers={'kbn-xsrf': 'true', 'Content-Type': 'application/json'},
                json=pattern_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Index pattern created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create index pattern: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating index pattern: {e}")
            return False

    def get_visualization_data(self) -> Dict:
        """Get data for visualization testing"""
        try:
            if not self.es:
                return {}
            
            # Get sentiment distribution
            response = self.es.search(
                index=f"{self.index_name}-*",
                size=0,
                aggs={
                    "sentiment_distribution": {
                        "terms": {
                            "field": "sentiment_label",
                            "size": 10
                        }
                    },
                    "method_distribution": {
                        "terms": {
                            "field": "method_used",
                            "size": 10
                        }
                    },
                    "avg_confidence": {
                        "avg": {
                            "field": "confidence_score"
                        }
                    }
                }
            )
            
            if 'aggregations' in response:
                aggs = response['aggregations']
                return {
                    'sentiment_distribution': {
                        bucket['key']: bucket['doc_count'] 
                        for bucket in aggs.get('sentiment_distribution', {}).get('buckets', [])
                    },
                    'method_distribution': {
                        bucket['key']: bucket['doc_count'] 
                        for bucket in aggs.get('method_distribution', {}).get('buckets', [])
                    },
                    'avg_confidence': aggs.get('avg_confidence', {}).get('value', 0),
                    'total_documents': response.get('hits', {}).get('total', {}).get('value', 0)
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting visualization data: {e}")
            return {}

    def generate_test_report(self, test_results: Dict) -> None:
        """Generate detailed test report"""
        logger.info("📋 KIBANA SAVED OBJECTS TEST REPORT")
        logger.info("=" * 50)
        
        # Summary
        passed_tests = sum(1 for key, value in test_results.items() 
                          if key != 'errors' and isinstance(value, bool) and value)
        total_tests = sum(1 for key, value in test_results.items() 
                         if key != 'errors' and isinstance(value, bool))
        
        logger.info(f"📊 Tests passed: {passed_tests}/{total_tests}")
        
        # Save report to file
        import json
        from datetime import datetime
        report_file = f"kibana_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")

    def test_complete_pipeline(self) -> Dict[str, Any]:
        """Complete pipeline test including data flow"""
        logger.info("🔬 COMPLETE PIPELINE TEST")
        logger.info("=" * 50)
        
        # Test saved objects
        test_results = self.test_kibana_saved_objects()
        
        # Test index pattern creation if needed
        if not test_results['index_pattern_exists']:
            logger.info("🔧 Creating index pattern...")
            if self.create_index_pattern():
                test_results['index_pattern_exists'] = True
                logger.info("✅ Index pattern created")
            else:
                logger.error("❌ Failed to create index pattern")
        
        # Test dashboard access
        if test_results['dashboard_created']:
            logger.info("🌐 Testing dashboard access...")
            dashboard_url = f"http://{self.kibana_host}/app/dashboards#/view/sentiment-dashboard"
            try:
                import requests
                response = requests.get(dashboard_url, timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Dashboard is accessible")
                    test_results['dashboard_accessible'] = True
                else:
                    logger.warning(f"⚠️ Dashboard returned {response.status_code}")
                    test_results['dashboard_accessible'] = False
            except Exception as e:
                logger.error(f"❌ Dashboard access error: {e}")
                test_results['dashboard_accessible'] = False
        
        return test_results

    def import_kibana_objects(self, ndjson_file_path: str = "export.ndjson") -> bool:
        """Import index patterns and dashboards from NDJSON file"""
        logger.info(f"📥 Importing Kibana objects from {ndjson_file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(ndjson_file_path):
                logger.error(f"❌ NDJSON file not found: {ndjson_file_path}")
                return False
            
            # Read the NDJSON file
            with open(ndjson_file_path, 'r', encoding='utf-8') as f:
                ndjson_content = f.read()
            
            # Import via Kibana API
            import_url = f"http://{self.kibana_host}/api/saved_objects/_import"
            
            headers = {
                'kbn-xsrf': 'true',
                'Content-Type': 'application/json'
            }
            
            # Add overwrite parameter to replace existing objects
            params = {
                'overwrite': 'true'
            }
            
            response = requests.post(
                import_url,
                headers=headers,
                params=params,
                data=ndjson_content,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success_count = result.get('successCount', 0)
                error_count = len(result.get('errors', []))
                
                logger.info(f"✅ Kibana import completed:")
                logger.info(f"   📊 Successfully imported: {success_count} objects")
                
                if error_count > 0:
                    logger.warning(f"   ⚠️ Errors: {error_count}")
                    for error in result.get('errors', []):
                        logger.warning(f"   ❌ {error.get('type')}: {error.get('error', {}).get('message')}")
                
                return success_count > 0
            else:
                logger.error(f"❌ Kibana import failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ NDJSON import failed: {e}")
            import traceback
            logger.error(f"Full error: {traceback.format_exc()}")
            return False

    def setup_complete_dashboard(self) -> bool:
        """Complete dashboard setup with NDJSON import"""
        logger.info("📊 Setting up complete dashboard configuration...")
        
        try:
            # Step 1: Setup Elasticsearch client
            if not self.setup_elasticsearch_client():
                logger.error("❌ Elasticsearch setup failed")
                return False
            
            # Step 2: Create index template
            if self.create_index_template():
                logger.info("✅ Index template created")
            else:
                logger.warning("⚠️ Index template creation failed")
            
            # Step 3: Import NDJSON objects (index patterns + dashboards)
            if self.import_kibana_objects():
                logger.info("✅ Dashboard objects imported from NDJSON")
                return True
            else:
                logger.warning("⚠️ NDJSON import failed - trying manual index pattern creation")
                
                # Fallback to manual creation
                if self.create_index_pattern():
                    logger.info("✅ Fallback index pattern created")
                    return True
                else:
                    logger.error("❌ Both NDJSON import and manual creation failed")
                    return False
            
        except Exception as e:
            logger.error(f"❌ Dashboard setup failed: {e}")
            return False
def integrate_with_consumer():
    """Integration function to modify consumer for Elasticsearch"""
    logger.info("🔧 Integrating dashboard with consumer...")
    
    # This function would be called from the consumer
    # to send data to both CSV and Elasticsearch
    
    dashboard = MalaysianTourismDashboard()
    
    # Start dashboard services
    if dashboard.start_services():
        logger.info("✅ Dashboard services ready for data")
        return dashboard
    else:
        logger.error("❌ Dashboard services failed to start")
        return None

# Consumer integration helper
def send_to_elasticsearch(dashboard: MalaysianTourismDashboard, processed_message: Dict) -> bool:
    """Send processed message to Elasticsearch"""
    if not dashboard or not dashboard.es:
        return False
    
    try:
        # Extract data for Elasticsearch
        sentiment_analysis = processed_message.get('sentiment_analysis', {})
        final_sentiment = sentiment_analysis.get('final_sentiment', {})
        
        # Create document for Elasticsearch
        doc = {
            'sentiment_label': final_sentiment.get('label', 'unknown'),
            'confidence_score': final_sentiment.get('confidence', 0.0),
            'sentiment_score': final_sentiment.get('score', 0.0),
            'original_text': processed_message.get('original_content', ''),
            'processed_text': sentiment_analysis.get('preprocessing', {}).get('combined_processed', ''),
            'method_used': final_sentiment.get('method', 'unknown'),
            'content_type': processed_message.get('content_type', 'unknown'),
            'is_malaysia_related': processed_message.get('is_malaysia_related', False),
            'title': processed_message.get('title', ''),
            'subreddit': processed_message.get('subreddit', ''),
            'author': processed_message.get('author', ''),
            'score': processed_message.get('score', 0),
            'text_length': len(processed_message.get('content', ''))
        }
        
        # Index document
        return dashboard.index_document(doc)
        
    except Exception as e:
        logger.error(f"❌ Failed to send to Elasticsearch: {e}")
        return False

def main():
    """Main function for testing dashboard"""
    try:
        print("📊 Malaysian Tourism Dashboard - Elasticsearch + Kibana")
        print("=" * 60)
        
        dashboard = MalaysianTourismDashboard()
        
        # Start services
        if dashboard.start_services():
            print("✅ Dashboard services started successfully!")
            print(f"📊 Elasticsearch: http://localhost:9200")
            print(f"📊 Kibana: http://localhost:5601")
            print("🎯 Ready to receive sentiment data!")
            
            # Keep running
            try:
                while True:
                    stats = dashboard.get_dashboard_stats()
                    print(f"📊 Dashboard stats: {stats}")
                    time.sleep(30)
            except KeyboardInterrupt:
                print("\n🛑 Stopping dashboard services...")
                dashboard.stop_services()
                print("✅ Dashboard stopped")
        else:
            print("❌ Failed to start dashboard services")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Dashboard failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())