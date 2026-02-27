"""
Feed Validation Module
======================

Enterprise-grade feed integrity and validation engine for financial
data infrastructure. Provides cross-feed deviation analysis, feed-level
trust scoring, and historical reliability tracking.

This module serves as a Data Integrity Firewall for financial feeds,
ensuring that data flowing into trust scoring and Market Stability Index
(MSI) computation is validated, consistent, and trustworthy.

Cybersecurity Role:
    In financial cybersecurity, data feed manipulation is a primary
    attack vector. Adversaries may compromise a single feed source
    to inject false prices. This module detects such attacks by
    cross-referencing multiple feeds and flagging inconsistencies
    before they propagate into trading decisions.

Components:
    - FeedIntegrityEngine: Core validation engine with feed registration,
      price tracking, cross-feed deviation analysis, reliability scoring,
      and persistent event logging.
"""

from feed_validation.feed_integrity_engine import FeedIntegrityEngine

__all__ = ['FeedIntegrityEngine']
