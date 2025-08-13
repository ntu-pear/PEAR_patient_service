import logging
import threading
import queue
import time
from typing import Dict, Any, Optional
from datetime import datetime

from .rabbitmq_client import RabbitMQClient

logger = logging.getLogger(__name__)

class PublishRequest:
    """Encapsulates a publish request"""
    def __init__(self, exchange: str, routing_key: str, message: Dict[str, Any]):
        self.exchange = exchange
        self.routing_key = routing_key
        self.message = message
        self.timestamp = datetime.utcnow()
        

class ProducerManager:
    """
    Manages RabbitMQ connection for all producers.
    Maintains a persistent connection and processes publish requests from a queue.
    """
    
    def __init__(self, service_name: str = "producer-manager", testing: bool = False):
        self.client = RabbitMQClient(service_name)
        self.publish_queue = queue.Queue(maxsize=1000)
        self.is_running = False
        self.producer_thread = None
        self.exchanges = set()  # Track declared exchanges
        self.testing = testing                  # When pytesting, threads will be daemon to prevent pytest hanging
        
    def declare_exchange(self, exchange: str, exchange_type: str = 'topic'):
        """Declare an exchange (idempotent)"""
        try:
            self.client.ensure_connection()
            self.client.channel.exchange_declare(
                exchange=exchange,
                exchange_type=exchange_type,
                durable=True
            )
            self.exchanges.add(exchange)
            logger.info(f"Declared exchange: {exchange}")
        except Exception as e:
            logger.error(f"Failed to declare exchange {exchange}: {str(e)}")
            raise
    
    def start_producer(self):
        """Start the producer manager service"""
        if self.is_running:
            logger.warning("Producer manager is already running")
            return
        
        self.is_running = True
        self.producer_thread = threading.Thread(target=self._producer_loop, daemon=self.testing)
        self.producer_thread.start()
        logger.info("Producer manager started")
    
    def _producer_loop(self):
        """Main loop that maintains connection and processes publish requests"""
        logger.info("Starting producer loop...")
        
        # Initial connection
        if not self.client.connect():
            logger.error("Failed initial connection")
            self.is_running = False
            return
        
        last_heartbeat = time.time()
        heartbeat_interval = 15  # Send heartbeat every 15 seconds
        
        while self.is_running:
            try:
                # Process publish requests with timeout to allow heartbeats
                try:
                    request = self.publish_queue.get(timeout=1.0)
                    self._process_publish_request(request)
                except queue.Empty:
                    pass
                
                # Send heartbeat if needed
                current_time = time.time()
                if current_time - last_heartbeat > heartbeat_interval:
                    self._send_heartbeat()
                    last_heartbeat = current_time
                    
            except Exception as e:
                logger.error(f"Error in producer loop: {str(e)}")
                self._handle_connection_error()
        
        logger.info("Producer loop ended")
        self._cleanup()
    
    def _process_publish_request(self, request: PublishRequest):
        """Process a single publish request"""
        try:
            # Ensure connection is active
            self.client.ensure_connection()
            
            # Ensure exchange is declared
            if request.exchange not in self.exchanges:
                self.declare_exchange(request.exchange)
            
            # Publish the message
            success = self.client.publish(
                exchange=request.exchange,
                routing_key=request.routing_key,
                message=request.message
            )
            
            if success:
                logger.debug(f"Published to {request.exchange}/{request.routing_key}")
            else:
                logger.error(f"Failed to publish to {request.exchange}/{request.routing_key}")
                
        except Exception as e:
            logger.error(f"Error processing publish request: {str(e)}")
            raise
    
    def _send_heartbeat(self):
        """Send heartbeat to keep connection alive"""
        try:
            if self.client.connection and not self.client.connection.is_closed:
                self.client.connection.process_data_events(time_limit=0)
                logger.debug("Heartbeat sent")
        except Exception as e:
            logger.error(f"Heartbeat failed: {str(e)}")
            raise
    
    def _handle_connection_error(self):
        """Handle connection errors and attempt reconnection"""
        logger.warning("Handling connection error...")
        
        max_retries = 5
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{max_retries}")
                
                # Close existing connection
                if self.client:
                    self.client.close()
                
                # Reconnect
                if self.client.connect():
                    # Re-declare exchanges
                    for exchange in self.exchanges:
                        self.client.channel.exchange_declare(
                            exchange=exchange,
                            exchange_type='topic',
                            durable=True
                        )
                    logger.info("Successfully reconnected")
                    return
                    
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logger.error("Failed to reconnect after all attempts")
        self.is_running = False
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.client:
                self.client.close()
            logger.info("Producer cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def publish(self, exchange: str, routing_key: str, message: Dict[str, Any]) -> bool:
        """
        Queue a message for publishing.
        
        Args:
            exchange: The exchange to publish to
            routing_key: The routing key
            message: The message to publish
            
        Returns:
            bool: True if successfully queued, False otherwise
        """
        if not self.is_running:
            logger.error("Producer manager is not running")
            return False
        
        try:
            request = PublishRequest(exchange, routing_key, message)
            self.publish_queue.put_nowait(request)
            return True
        except queue.Full:
            logger.error("Publish queue is full")
            return False
        except Exception as e:
            logger.error(f"Error queuing message: {str(e)}")
            return False
    
    def stop_producer(self, timeout: int = 10):
        """Stop the producer manager gracefully"""
        if not self.is_running:
            logger.warning("Producer manager is not running")
            return
        
        logger.info("Stopping producer manager...")
        self.is_running = False
        
        if self.producer_thread and self.producer_thread.is_alive():
            self.producer_thread.join(timeout=timeout)
            
            if self.producer_thread.is_alive():
                logger.warning("Producer thread did not stop within timeout")
        
        logger.info("Producer manager stopped")


# Singleton instance
_producer_manager = None
_lock = threading.Lock()

def get_producer_manager(*, testing: bool = False) -> ProducerManager:
    """Get or create the singleton producer manager"""
    global _producer_manager
    
    with _lock:
        if _producer_manager is None:
            _producer_manager = ProducerManager(testing=testing)
            _producer_manager.start_producer()
            logger.info("Created and started producer manager")
        
        return _producer_manager

def stop_producer_manager():
    """Stop the singleton producer manager"""
    global _producer_manager
    
    with _lock:
        if _producer_manager:
            _producer_manager.stop_producer()
            _producer_manager = None
            logger.info("Stopped producer manager")
