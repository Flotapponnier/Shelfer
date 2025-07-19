"""
Crawl Queue Manager for handling URL queue operations in the web crawler.

This module provides a dedicated class for managing the crawl queue, including
merging new URLs, prioritizing them, and maintaining queue state.
"""

from typing import List, Tuple, Set, Dict, Any
from collections import deque
from urllib.parse import urlparse

from ..utils.domain_utils import is_same_domain
from .url_prioritizer import UrlPrioritizer
from ..utils.utils import logger


class CrawlQueueManager:
    """
    Manages the crawl queue for the web crawler.
    
    This class handles:
    - Queue initialization and state management
    - Merging new URLs with existing queue
    - Prioritizing URLs using the URL prioritizer
    - Filtering URLs based on domain and visited status
    - Queue statistics and monitoring
    """
    
    def __init__(self, domain_url: str, url_prioritizer: UrlPrioritizer = None):
        """
        Initialize the crawl queue manager.
        
        Args:
            domain_url: The target domain URL for validation
            url_prioritizer: Optional URL prioritizer instance (creates new one if not provided)
        """
        self.domain_url = domain_url
        self.url_prioritizer = url_prioritizer or UrlPrioritizer()
        
        # Queue state
        self.queue = deque()  # (url, score) tuples
        self.visited_urls = set()
        self.url_scores = {}  # Track scores for analysis
        
        # Statistics
        self.stats = {
            "urls_added": 0,
            "urls_removed": 0,
            "urls_visited": 0,
            "queue_size_history": [],
            "merge_operations": 0
        }
    
    def add_initial_url(self, url: str, score: float = 0.0) -> None:
        """
        Add the initial URL to start crawling from.
        
        Args:
            url: The URL to add
            score: Initial score for the URL
        """
        self.queue.append((url, score))
        self.stats["urls_added"] += 1
        self._update_queue_stats()
    
    def get_next_batch(self, batch_size: int) -> List[str]:
        """
        Get the next batch of URLs to process.
        
        Args:
            batch_size: Number of URLs to retrieve
            
        Returns:
            List of URLs to process
        """
        batch_urls = []
        batch_scores = []
        batch_contexts = []
        for _ in range(min(batch_size, len(self.queue))):
            if self.queue:
                url, score = self.queue.popleft()
                batch_urls.append(url)
                batch_scores.append(score)
                # Try to get context from url_scores if available
                context = None
                # This is a best effort, as context is not stored in the queue
                # (could be improved by storing context in the queue)
                context = None
                batch_contexts.append(context)
                self.stats["urls_removed"] += 1
        if batch_urls:
            logger.debug(f"📦 Selected batch of {len(batch_urls)} URLs:")
            for i, (url, score, context) in enumerate(zip(batch_urls, batch_scores, batch_contexts)):
                logger.debug(f"   {i+1}. {url} (score: {score}) context={context}")
        else:
            logger.debug(f"📦 No URLs selected for batch (queue empty)")
        self._update_queue_stats()
        return batch_urls
    
    def mark_urls_visited(self, urls: List[str]) -> None:
        """
        Mark URLs as visited.
        
        Args:
            urls: List of URLs to mark as visited
        """
        for url in urls:
            self.visited_urls.add(url)
            self.stats["urls_visited"] += 1
    
    def merge_new_links(self, new_links_with_context: List[Dict[str, Any]]) -> None:
        """
        Merge new links into the queue with prioritization.
        
        Args:
            new_links_with_context: List of link dictionaries with context
        """
        if not new_links_with_context:
            return
        
        logger.debug(f"🔄 Merging {len(new_links_with_context)} new links into queue")
        for link in new_links_with_context[:10]:
            logger.debug(f"[NEW LINK] url={link.get('url')} context={link.get('context')}")
        
        # Prioritize the new links
        prioritized_links = self.url_prioritizer.prioritize_urls(new_links_with_context)
        
        logger.debug(f"📊 Prioritized {len(prioritized_links)} links with scores (showing top 10):")
        for url, score in prioritized_links[:10]:
            context = next((l.get('context') for l in new_links_with_context if l.get('url') == url), None)
            logger.debug(f"   url={url} score={score} context={context}")
        
        # Store URL scores for analysis - update with latest scores
        for url, score in prioritized_links:
            self.url_scores[url] = score
        
        self._merge_and_prioritize_queue(prioritized_links)
        self.stats["merge_operations"] += 1
        self._update_queue_stats()
        logger.debug(f"✅ Queue updated. New size: {self.get_queue_size()}")
    
    def _merge_and_prioritize_queue(self, new_links_with_scores: List[Tuple[str, float]]) -> None:
        """
        Merge new links with the current queue and re-prioritize.
        
        Args:
            new_links_with_scores: List of (url, score) tuples from URL prioritizer
        """
        url_scores = {}
        for url, score in self.queue:
            if url not in url_scores or score > url_scores[url]:
                url_scores[url] = score
        skipped_visited = 0
        skipped_negative = 0
        skipped_domain = 0
        added_new = 0
        updated_existing = 0
        for url, score in new_links_with_scores:
            reason = None
            if url in self.visited_urls:
                skipped_visited += 1
                reason = "visited"
            elif score < 0:
                skipped_negative += 1
                reason = "negative_score"
            elif not is_same_domain(url, self.domain_url):
                skipped_domain += 1
                reason = "wrong_domain"
            if reason:
                logger.debug(f"[FILTERED] url={url} score={score} reason={reason}")
                continue
            if url not in url_scores or score > url_scores[url]:
                url_scores[url] = score
                if url not in [u for u, _ in self.queue]:
                    added_new += 1
                else:
                    updated_existing += 1
        logger.debug(f"🔍 Merge filtering: {skipped_visited} visited, {skipped_negative} negative score, {skipped_domain} wrong domain")
        logger.debug(f"🔍 Merge results: {added_new} new URLs added, {updated_existing} existing URLs updated")
        scored_urls = [(url, score) for url, score in url_scores.items()]
        scored_urls.sort(key=lambda x: x[1], reverse=True)
        self.queue.clear()
        for url, score in scored_urls:
            self.queue.append((url, score))
        logger.debug(f"[QUEUE STATE] Top 10 after merge:")
        for i, (url, score) in enumerate(scored_urls[:10], 1):
            logger.debug(f"   {i}. {url} (score: {score})")
    
    def get_queue_size(self) -> int:
        """
        Get the current queue size.
        
        Returns:
            Number of URLs in the queue
        """
        return len(self.queue)
    
    def is_queue_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if queue is empty, False otherwise
        """
        return len(self.queue) == 0
    
    def get_next_url(self) -> Tuple[str, float]:
        """
        Get the next URL and its score from the queue.
        
        Returns:
            Tuple of (url, score) or (None, 0) if queue is empty
        """
        if self.queue:
            return self.queue[0]
        return (None, 0.0)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current status of the queue.
        
        Returns:
            Dictionary with queue status information
        """
        next_url, next_score = self.get_next_url()
        return {
            "queue_size": self.get_queue_size(),
            "visited_count": len(self.visited_urls),
            "next_url": next_url,
            "next_score": next_score,
            "is_empty": self.is_queue_empty()
        }
    
    def get_top_queue_urls(self, n: int = 10) -> list:
        """
        Return the top n URLs in the queue with their scores.
        """
        return list(self.queue)[:n]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the queue operations.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            **self.stats,
            "current_queue_size": self.get_queue_size(),
            "visited_urls_count": len(self.visited_urls),
            "url_scores_count": len(self.url_scores),
            "queue_size_history": self.stats["queue_size_history"][-10:],  # Last 10 entries
            "access_urls_list": list(self.visited_urls),
            "url_scores": self.url_scores,
            "top_queue_urls": self.get_top_queue_urls(10),
        }
    
    def _update_queue_stats(self) -> None:
        """Update queue size history for monitoring."""
        self.stats["queue_size_history"].append(self.get_queue_size())
    
    def reset_statistics(self) -> None:
        """Reset all statistics."""
        self.stats = {
            "urls_added": 0,
            "urls_removed": 0,
            "urls_visited": 0,
            "queue_size_history": [],
            "merge_operations": 0
        }
        self.url_scores = {}
    
    def clear_queue(self) -> None:
        """Clear the queue and reset visited URLs."""
        self.queue.clear()
        self.visited_urls.clear()
        self._update_queue_stats()
    
    def get_visited_urls(self) -> Set[str]:
        """
        Get the set of visited URLs.
        
        Returns:
            Set of visited URLs
        """
        return self.visited_urls.copy()
    
    def is_url_visited(self, url: str) -> bool:
        """
        Check if a URL has been visited.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL has been visited, False otherwise
        """
        return url in self.visited_urls 