"""Claim flagging — re-export of score_evidence.score_all for plan compatibility."""

from .score_evidence import score_all as flag_claims

__all__ = ["flag_claims"]
