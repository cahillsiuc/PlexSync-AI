"""
Learning System - Learns from user corrections to improve matching
"""
from typing import Dict, Any, List
from models import SyncOperation
from loguru import logger


class LearningSystem:
    """
    Machine learning system that learns from:
    - User corrections
    - Successful matches
    - Failed matches
    - PO type patterns
    - Vendor patterns
    """

    def __init__(self):
        self.patterns: Dict[str, Any] = {
            "vendor_patterns": {},
            "po_type_patterns": {},
            "correction_history": []
        }

    def learn_from_sync_operation(self, sync_op: SyncOperation):
        """
        Learn from a sync operation

        Args:
            sync_op: Completed sync operation
        """
        if not sync_op.success:
            logger.info("Learning from failed sync operation")
            self._learn_from_failure(sync_op)
        else:
            logger.info("Learning from successful sync operation")
            self._learn_from_success(sync_op)

        # Learn from user corrections
        if sync_op.user_corrections:
            self._learn_from_corrections(sync_op)

    def _learn_from_success(self, sync_op: SyncOperation):
        """Learn patterns from successful sync"""
        if sync_op.po_type:
            if sync_op.po_type not in self.patterns["po_type_patterns"]:
                self.patterns["po_type_patterns"][sync_op.po_type] = {
                    "success_count": 0,
                    "total_count": 0
                }
            self.patterns["po_type_patterns"][sync_op.po_type]["success_count"] += 1
            self.patterns["po_type_patterns"][sync_op.po_type]["total_count"] += 1

    def _learn_from_failure(self, sync_op: SyncOperation):
        """Learn from failed sync operations"""
        if sync_op.po_type:
            if sync_op.po_type not in self.patterns["po_type_patterns"]:
                self.patterns["po_type_patterns"][sync_op.po_type] = {
                    "success_count": 0,
                    "total_count": 0
                }
            self.patterns["po_type_patterns"][sync_op.po_type]["total_count"] += 1

    def _learn_from_corrections(self, sync_op: SyncOperation):
        """Learn from user corrections"""
        corrections = sync_op.user_corrections

        # Store correction for pattern analysis
        self.patterns["correction_history"].append({
            "sync_op_id": sync_op.id,
            "corrections": corrections,
            "po_type": sync_op.po_type,
            "vendor_pattern": sync_op.vendor_pattern
        })

        # Update vendor patterns
        if sync_op.vendor_pattern:
            if sync_op.vendor_pattern not in self.patterns["vendor_patterns"]:
                self.patterns["vendor_patterns"][sync_op.vendor_pattern] = {
                    "correction_count": 0,
                    "common_corrections": {}
                }
            self.patterns["vendor_patterns"][sync_op.vendor_pattern]["correction_count"] += 1

    def get_confidence_adjustment(
        self,
        po_type: str,
        vendor_pattern: str
    ) -> float:
        """
        Get confidence adjustment based on learned patterns

        Returns:
            Adjustment factor (-10 to +10)
        """
        adjustment = 0.0

        # Check PO type success rate
        if po_type in self.patterns["po_type_patterns"]:
            pattern = self.patterns["po_type_patterns"][po_type]
            if pattern["total_count"] > 0:
                success_rate = pattern["success_count"] / pattern["total_count"]
                if success_rate > 0.9:
                    adjustment += 5.0
                elif success_rate < 0.5:
                    adjustment -= 5.0

        # Check vendor pattern corrections
        if vendor_pattern in self.patterns["vendor_patterns"]:
            pattern = self.patterns["vendor_patterns"][vendor_pattern]
            if pattern["correction_count"] > 3:
                adjustment -= 3.0

        return adjustment

    def get_recommendations(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendations based on learned patterns

        Args:
            invoice_data: Invoice data to analyze

        Returns:
            Recommendations dictionary
        """
        recommendations = {
            "suggested_po_type": None,
            "confidence_boost": 0.0,
            "warnings": []
        }

        # Analyze vendor pattern
        vendor_name = invoice_data.get("vendor_name", "")
        if vendor_name in self.patterns["vendor_patterns"]:
            pattern = self.patterns["vendor_patterns"][vendor_name]
            if pattern["correction_count"] > 5:
                recommendations["warnings"].append(
                    f"Vendor {vendor_name} has high correction rate"
                )

        return recommendations


# Singleton instance
learning_system = LearningSystem()

