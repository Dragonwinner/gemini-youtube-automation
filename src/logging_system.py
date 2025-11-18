# FILE: src/logging_system.py
# Comprehensive logging system with rotation and monitoring

import logging
import logging.handlers
import os
import json
from pathlib import Path
from datetime import datetime
import traceback

class NewsLogger:
    """
    Centralized logging system with:
    - Rotating log files
    - Structured logging
    - Performance metrics
    - Error tracking
    """
    
    def __init__(self, log_dir="logs", app_name="news_automation"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.app_name = app_name
        
        # Setup loggers
        self.logger = self._setup_logger()
        self.metrics_logger = self._setup_metrics_logger()
        self.error_logger = self._setup_error_logger()
        
        # Metrics tracking
        self.metrics = {
            'bulletins_produced': 0,
            'videos_uploaded': 0,
            'errors': 0,
            'api_calls': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def _setup_logger(self):
        """Setup main application logger with rotation."""
        logger = logging.getLogger(f"{self.app_name}.main")
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{self.app_name}.log',
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_metrics_logger(self):
        """Setup metrics logger for performance tracking."""
        logger = logging.getLogger(f"{self.app_name}.metrics")
        logger.setLevel(logging.INFO)
        
        # Daily rotating file handler
        handler = logging.handlers.TimedRotatingFileHandler(
            self.log_dir / 'metrics.log',
            when='midnight',
            interval=1,
            backupCount=30  # Keep 30 days
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        return logger
    
    def _setup_error_logger(self):
        """Setup dedicated error logger."""
        logger = logging.getLogger(f"{self.app_name}.errors")
        logger.setLevel(logging.ERROR)
        
        # Error file handler
        handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=10
        )
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        return logger
    
    def info(self, message, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message, exception=None, **kwargs):
        """Log error message with optional exception."""
        self.metrics['errors'] += 1
        
        if exception:
            error_details = {
                'message': message,
                'exception': str(exception),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            self.error_logger.error(json.dumps(error_details, indent=2))
        else:
            self.error_logger.error(message, extra=kwargs)
        
        self.logger.error(message, extra=kwargs)
    
    def log_metric(self, metric_name, value, **metadata):
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            metadata: Additional metadata
        """
        metric_data = {
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        self.metrics_logger.info(json.dumps(metric_data))
        
        # Update internal metrics
        if metric_name == 'bulletin_produced':
            self.metrics['bulletins_produced'] += 1
        elif metric_name == 'video_uploaded':
            self.metrics['videos_uploaded'] += 1
        elif metric_name == 'api_call':
            self.metrics['api_calls'] += 1
    
    def log_bulletin_production(self, bulletin_id, category, duration, success=True):
        """Log news bulletin production."""
        self.log_metric(
            'bulletin_produced',
            1,
            bulletin_id=bulletin_id,
            category=category,
            duration_seconds=duration,
            success=success
        )
    
    def log_video_upload(self, video_id, title, size_mb, upload_time):
        """Log video upload."""
        self.log_metric(
            'video_uploaded',
            1,
            video_id=video_id,
            title=title,
            size_mb=size_mb,
            upload_time_seconds=upload_time
        )
    
    def log_api_call(self, api_name, endpoint, duration, success=True):
        """Log external API call."""
        self.log_metric(
            'api_call',
            1,
            api=api_name,
            endpoint=endpoint,
            duration_ms=duration,
            success=success
        )
    
    def get_metrics_summary(self):
        """Get summary of logged metrics."""
        self.metrics['uptime'] = str(datetime.now() - datetime.fromisoformat(self.metrics['start_time']))
        return self.metrics.copy()
    
    def save_metrics_snapshot(self):
        """Save current metrics to file."""
        snapshot_file = self.log_dir / f'metrics_snapshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        try:
            with open(snapshot_file, 'w') as f:
                json.dump(self.get_metrics_summary(), f, indent=2)
            
            self.info(f"Metrics snapshot saved: {snapshot_file}")
        except Exception as e:
            self.error(f"Failed to save metrics snapshot: {e}")
    
    def log_stream_health(self, is_healthy, bitrate=None, dropped_frames=None):
        """Log stream health status."""
        health_data = {
            'healthy': is_healthy,
            'bitrate': bitrate,
            'dropped_frames': dropped_frames,
            'timestamp': datetime.now().isoformat()
        }
        
        self.metrics_logger.info(f"STREAM_HEALTH: {json.dumps(health_data)}")
        
        if not is_healthy:
            self.warning("Stream unhealthy", **health_data)
    
    def log_system_stats(self):
        """Log system resource usage."""
        try:
            import psutil
            
            stats = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.now().isoformat()
            }
            
            self.metrics_logger.info(f"SYSTEM_STATS: {json.dumps(stats)}")
            
            # Warn if resources are high
            if stats['cpu_percent'] > 80:
                self.warning(f"High CPU usage: {stats['cpu_percent']}%")
            if stats['memory_percent'] > 80:
                self.warning(f"High memory usage: {stats['memory_percent']}%")
                
        except ImportError:
            self.debug("psutil not installed, skipping system stats")
        except Exception as e:
            self.error(f"Failed to log system stats: {e}")
    
    def cleanup_old_logs(self, days=30):
        """Remove log files older than specified days."""
        try:
            import time
            
            now = time.time()
            cutoff = now - (days * 86400)
            
            removed = 0
            for log_file in self.log_dir.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    removed += 1
            
            if removed > 0:
                self.info(f"Cleaned up {removed} old log files")
                
        except Exception as e:
            self.error(f"Failed to cleanup old logs: {e}")
