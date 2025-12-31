"""
Reciprocal Rank Fusion (RRF) implementation.
Combines rankings from multiple retrievers without raw score mixing.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    retrieval_results: List[List[Dict[str, Any]]],
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combine multiple retrieval result lists using Reciprocal Rank Fusion.
    
    RRF formula: score(d) = Σ 1 / (k + rank(d))
    where rank(d) is the rank of document d in each retriever's results.
    
    Args:
        retrieval_results: List of retrieval result lists from different retrievers.
                          Each result should have a 'chunk_id' field.
        k: RRF constant (default: 60, standard value from literature)
    
    Returns:
        Fused and re-ranked list of results, sorted by RRF score descending.
    """
    
    if not retrieval_results:
        return []
    
    # Dictionary to accumulate RRF scores
    rrf_scores: Dict[str, float] = {}
    document_map: Dict[str, Dict[str, Any]] = {}
    
    # Process each retriever's results
    for retriever_results in retrieval_results:
        for rank, result in enumerate(retriever_results, start=1):
            chunk_id = result.get("chunk_id")
            
            if not chunk_id:
                logger.warning("Result missing chunk_id, skipping")
                continue
            
            # Calculate RRF score contribution from this retriever
            rrf_contribution = 1.0 / (k + rank)
            
            # Accumulate score
            if chunk_id in rrf_scores:
                rrf_scores[chunk_id] += rrf_contribution
            else:
                rrf_scores[chunk_id] = rrf_contribution
                document_map[chunk_id] = result
    
    # Sort by RRF score descending
    sorted_chunk_ids = sorted(
        rrf_scores.keys(),
        key=lambda cid: rrf_scores[cid],
        reverse=True
    )
    
    # Build final ranked list
    fused_results = []
    for chunk_id in sorted_chunk_ids:
        result = document_map[chunk_id].copy()
        result["rrf_score"] = rrf_scores[chunk_id]
        fused_results.append(result)
    
    logger.info(f"RRF fusion: {len(retrieval_results)} retrievers → {len(fused_results)} unique results")
    
    return fused_results
