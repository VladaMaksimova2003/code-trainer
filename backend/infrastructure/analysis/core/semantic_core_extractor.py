"""Deprecated alias — use CoreDetectionPipeline."""
from infrastructure.analysis.core.core_detection_pipeline import CoreDetectionPipeline

SemanticCoreExtractor = CoreDetectionPipeline

__all__ = ["CoreDetectionPipeline", "SemanticCoreExtractor"]
