"""
Cost monitoring and tracking for AletheiaCodex.

Tracks AI API usage costs and provides alerts when limits are exceeded.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from google.cloud import firestore

from .cost_config import (
    CostLimits,
    AlertThresholds,
    calculate_cost,
    check_limit_exceeded,
    get_alert_level,
    get_cost_config
)

logger = logging.getLogger(__name__)


class CostMonitor:
    """
    Monitors and tracks AI API usage costs.
    """
    
    def __init__(self, project_id: str = "aletheia-codex-prod"):
        """
        Initialize cost monitor.
        
        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.firestore_client = firestore.Client(project=project_id)
        logger.info("Initialized CostMonitor")
    
    async def log_usage(
        self,
        user_id: str,
        provider: str,
        model: str,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log AI API usage.
        
        Args:
            user_id: User ID
            provider: AI provider name (e.g., 'gemini')
            model: Model name
            operation: Operation type (e.g., 'extract_entities')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Cost in USD
            document_id: Optional document ID
            metadata: Optional additional metadata
            
        Returns:
            Usage log document ID
        """
        try:
            usage_log = {
                'user_id': user_id,
                'provider': provider,
                'model': model,
                'operation': operation,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'cost': cost,
                'document_id': document_id,
                'metadata': metadata or {},
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            # Store in Firestore
            doc_ref = self.firestore_client.collection('usage_logs').add(usage_log)
            log_id = doc_ref[1].id
            
            logger.info(f"Logged usage: {operation} for user {user_id}, cost: ${cost:.6f}")
            
            # Check cost alerts
            await self.check_cost_alerts(user_id)
            
            return log_id
            
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
            raise
    
    async def get_usage_summary(
        self,
        user_id: str,
        timeframe: str = 'daily'
    ) -> Dict[str, Any]:
        """
        Get usage summary for a timeframe.
        
        Args:
            user_id: User ID
            timeframe: Timeframe ('daily', 'weekly', 'monthly')
            
        Returns:
            Usage summary dictionary
        """
        try:
            # Calculate start date
            now = datetime.utcnow()
            if timeframe == 'daily':
                start_date = now - timedelta(days=1)
            elif timeframe == 'weekly':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'monthly':
                start_date = now - timedelta(days=30)
            else:
                raise ValueError(f"Invalid timeframe: {timeframe}")
            
            # Query usage logs
            logs = self.firestore_client.collection('usage_logs') \
                .where('user_id', '==', user_id) \
                .where('timestamp', '>=', start_date) \
                .stream()
            
            # Aggregate data
            total_cost = 0.0
            total_tokens = 0
            operation_counts = {}
            
            for log in logs:
                data = log.to_dict()
                total_cost += data.get('cost', 0.0)
                total_tokens += data.get('total_tokens', 0)
                
                operation = data.get('operation', 'unknown')
                operation_counts[operation] = operation_counts.get(operation, 0) + 1
            
            summary = {
                'user_id': user_id,
                'timeframe': timeframe,
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'operation_counts': operation_counts
            }
            
            logger.info(f"Usage summary for {user_id} ({timeframe}): ${total_cost:.6f}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get usage summary: {e}")
            raise
    
    async def check_cost_alerts(self, user_id: str) -> Dict[str, Any]:
        """
        Check if cost limits are exceeded and send alerts.
        
        Args:
            user_id: User ID
            
        Returns:
            Alert status dictionary
        """
        try:
            # Get cost configuration
            config = get_cost_config(user_id)
            limits = config['limits']
            thresholds = config['thresholds']
            
            # Get usage for different timeframes
            daily_usage = await self.get_usage_summary(user_id, 'daily')
            weekly_usage = await self.get_usage_summary(user_id, 'weekly')
            monthly_usage = await self.get_usage_summary(user_id, 'monthly')
            
            # Check each limit
            alerts = {
                'daily': get_alert_level(daily_usage['total_cost'], limits.daily, thresholds),
                'weekly': get_alert_level(weekly_usage['total_cost'], limits.weekly, thresholds),
                'monthly': get_alert_level(monthly_usage['total_cost'], limits.monthly, thresholds)
            }
            
            # Log alerts
            for timeframe, level in alerts.items():
                if level != 'none':
                    logger.warning(f"Cost alert for {user_id} ({timeframe}): {level}")
                    await self._send_alert(user_id, timeframe, level, 
                                          daily_usage if timeframe == 'daily' else
                                          weekly_usage if timeframe == 'weekly' else
                                          monthly_usage)
            
            return {
                'user_id': user_id,
                'alerts': alerts,
                'usage': {
                    'daily': daily_usage['total_cost'],
                    'weekly': weekly_usage['total_cost'],
                    'monthly': monthly_usage['total_cost']
                },
                'limits': {
                    'daily': limits.daily,
                    'weekly': limits.weekly,
                    'monthly': limits.monthly
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to check cost alerts: {e}")
            raise
    
    async def _send_alert(
        self,
        user_id: str,
        timeframe: str,
        level: str,
        usage: Dict[str, Any]
    ):
        """
        Send cost alert notification.
        
        Args:
            user_id: User ID
            timeframe: Timeframe ('daily', 'weekly', 'monthly')
            level: Alert level ('warning', 'critical', 'emergency')
            usage: Usage summary
        """
        try:
            alert = {
                'user_id': user_id,
                'timeframe': timeframe,
                'level': level,
                'cost': usage['total_cost'],
                'tokens': usage['total_tokens'],
                'timestamp': firestore.SERVER_TIMESTAMP,
                'acknowledged': False
            }
            
            # Store alert in Firestore
            self.firestore_client.collection('cost_alerts').add(alert)
            
            logger.info(f"Cost alert sent: {level} for {user_id} ({timeframe})")
            
            # TODO: Implement email/notification sending
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def get_cost_estimate(
        self,
        text: str,
        operations: list = None
    ) -> Dict[str, float]:
        """
        Estimate cost for processing text.
        
        Args:
            text: Input text
            operations: List of operations to estimate
            
        Returns:
            Cost estimate dictionary
        """
        if operations is None:
            operations = ['extract_entities', 'detect_relationships']
        
        # Simple token estimation (4 chars per token)
        input_tokens = len(text) // 4
        
        estimates = {}
        total = 0.0
        
        for operation in operations:
            # Estimate output tokens based on operation
            if operation == 'extract_entities':
                output_tokens = 500  # ~50 tokens per entity, ~10 entities
            elif operation == 'detect_relationships':
                output_tokens = 150  # ~30 tokens per relationship, ~5 relationships
            else:
                output_tokens = 200
            
            cost = calculate_cost(input_tokens, output_tokens)
            estimates[operation] = cost
            total += cost
        
        estimates['total'] = total
        
        return estimates


# Convenience function
def create_cost_monitor(project_id: str = "aletheia-codex-prod") -> CostMonitor:
    """
    Create a CostMonitor instance.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        CostMonitor instance
    """
    return CostMonitor(project_id)