import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
import sys
from typing import Dict, List, Any, Tuple
import time
import random

class LLMLensMonitor:
    def __init__(self):
        self.daily_tracking = {
            "posts": [],
            "theorist_usage": {
                "mediaTheory": {"count": 0, "last_used": {}},
                "criticalTheory": {"count": 0, "last_used": {}},
                "technologyStudies": {"count": 0, "last_used": {}},
                "philosophyOthers": {"count": 0, "last_used": {}}
            },
            "total_posts": 0
        }
        self.weekly_tracking = {
            "mediaTheory": 0,
            "criticalTheory": 0,
            "technologyStudies": 0,
            "philosophyOthers": 0
        }
        self.last_post_time = None
        self.theorists = {
            "Foucault", "Haraway", "Butler", "Derrida", "Simondon",
            "McLuhan", "Virilio", "Ihde", "Latour", "Braidotti",
            "Kittler", "Bergson", "Bateson", "Benjamin", "Wiener",
            "Prigogine", "Dennett", "Stiegler", "Deleuze", "Chun"
        }
        self.target_accounts = {
            "DeepMind", "AnthropicAI", "OpenAI", "GoogleAI", "StabilityAI"
        }

    def parse_timestamp(self, log_line: str) -> datetime:
        """Extract timestamp from log line if present."""
        timestamp_match = re.search(r'\[(.*?)\]', log_line)
        if timestamp_match:
            try:
                return datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        return datetime.now()

    def analyze_tweet_content(self, content: str) -> Dict[str, Any]:
        """Analyze tweet content for theorists, concepts, and targets."""
        mentioned_theorists = [t for t in self.theorists if t in content]
        mentioned_targets = [t for t in self.target_accounts if t in content]

        # Simple concept extraction (could be enhanced)
        concepts = re.findall(r'(?:framework|theory|concept|principle|approach)s?\b', content.lower())

        return {
            "theorists_cited": mentioned_theorists,
            "target_mentioned": mentioned_targets,
            "key_concepts": list(set(concepts)),
            "type": "reply" if content.startswith("@") else "original"
        }

    def process_log_line(self, line: str):
        """Process a single log line."""
        # Strip ANSI escape codes
        line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)

        # Check for tweet actions
        if "Received response from generateText for tweet actions:" in line:
            actions = line.split("tweet actions:", 1)[1].strip()
            current_time = self.parse_timestamp(line)

            # Update post tracking
            self.daily_tracking["posts"].append({
                "timestamp": current_time.isoformat(),
                "actions": actions,
                "type": "action_decision"
            })

        # Check for successful posts
        elif "Successfully posted" in line:
            if "quote tweet" in line:
                post_type = "quote"
            elif "reply tweet" in line:
                post_type = "reply"
            else:
                post_type = "original"

            current_time = self.parse_timestamp(line)
            self.daily_tracking["posts"].append({
                "timestamp": current_time.isoformat(),
                "type": post_type
            })
            self.daily_tracking["engagement"]["post_types"][post_type] = self.daily_tracking["engagement"]["post_types"].get(post_type, 0) + 1

        # Check for likes
        elif "Liked tweet" in line:
            tweet_id = re.search(r'Liked tweet (\d+)', line)
            if tweet_id:
                current_time = self.parse_timestamp(line)
                self.daily_tracking["posts"].append({
                    "timestamp": current_time.isoformat(),
                    "tweet_id": tweet_id.group(1),
                    "type": "like"
                })
                self.daily_tracking["engagement"]["post_types"]["like"] = self.daily_tracking["engagement"]["post_types"].get("like", 0) + 1

        # Check for generated content
        elif any(x in line for x in ["Generated quote tweet content:", "Generated reply tweet content:", "quote tweet content:", "reply tweet content:"]):
            # Extract content after the colon, handling both formats
            content = line.split("content:", 1)[1].strip()
            if content and self.daily_tracking["posts"]:
                # Find the last post that doesn't have content
                for post in reversed(self.daily_tracking["posts"]):
                    if post["type"] in ["quote", "reply"] and "content" not in post:
                        post["content"] = content
                        analysis = self.analyze_tweet_content(content)
                        post.update(analysis)
                        break

        # Check for next scheduled tweet
        elif "Next tweet scheduled in" in line:
            minutes = re.search(r'in (\d+) minutes', line)
            if minutes:
                self.daily_tracking["timing"]["next_scheduled_post"] = int(minutes.group(1))

    def generate_report(self) -> Dict[str, Any]:
        """Generate the monitoring report."""
        # Get the last 5 posts with content
        recent_posts = [p for p in self.daily_tracking["posts"] if "content" in p][-5:]

        report = {
            "summary": {
                "total_posts": len([p for p in self.daily_tracking["posts"] if p["type"] not in ["action_decision"]]),
                "next_post_in": self.daily_tracking["timing"]["next_scheduled_post"],
                "recent_activity": [
                    {
                        "type": post["type"],
                        "content": post["content"],
                        "theorists": post.get("theorists_cited", []),
                        "targets": post.get("target_mentioned", [])
                    }
                    for post in recent_posts
                ]
            },
            "daily_tracking": self.daily_tracking,
            "repetition_alerts": {
                "theorist_frequency": self.analyze_theorist_frequency(),
                "target_interaction_frequency": self.analyze_target_frequency()
            },
            "weekly_metrics": self.calculate_weekly_metrics()
        }
        return report

    def analyze_theorist_frequency(self) -> Dict[str, Any]:
        """Analyze frequency of theorist citations."""
        theorist_counts = defaultdict(lambda: {"last_7_days": 0, "consecutive_posts": False})

        for i, post in enumerate(self.daily_tracking["posts"]):
            if "theorists_cited" not in post:
                continue

            for theorist in post["theorists_cited"]:
                theorist_counts[theorist]["last_7_days"] += 1
                if i > 0 and "theorists_cited" in self.daily_tracking["posts"][i-1]:
                    if theorist in self.daily_tracking["posts"][i-1]["theorists_cited"]:
                        theorist_counts[theorist]["consecutive_posts"] = True

        return dict(theorist_counts)

    def analyze_target_frequency(self) -> Dict[str, Any]:
        """Analyze frequency of target account interactions."""
        target_counts = defaultdict(int)
        for post in self.daily_tracking["posts"]:
            if "target_mentioned" in post:
                for target in post["target_mentioned"]:
                    target_counts[target] += 1

        return {
            target: {
                "last_24_hours": count,
                "consecutive": self.check_consecutive_interactions(target)
            }
            for target, count in target_counts.items()
        }

    def check_consecutive_interactions(self, target: str) -> bool:
        """Check if there are consecutive interactions with a target."""
        for i in range(len(self.daily_tracking["posts"]) - 1):
            current = self.daily_tracking["posts"][i].get("target_mentioned", [])
            next_post = self.daily_tracking["posts"][i+1].get("target_mentioned", [])
            if target in current and target in next_post:
                return True
        return False

    def calculate_weekly_metrics(self) -> Dict[str, Any]:
        """Calculate weekly metrics."""
        all_theorists = set()
        all_concepts = set()

        for post in self.daily_tracking["posts"]:
            if "theorists_cited" in post:
                all_theorists.update(post["theorists_cited"])
            if "key_concepts" in post:
                all_concepts.update(post["key_concepts"])

        total_posts = len([p for p in self.daily_tracking["posts"] if p["type"] not in ["action_decision"]])

        return {
            "unique_theorists": len(all_theorists),
            "unique_concepts": len(all_concepts),
            "avg_post_interval": sum(self.daily_tracking["timing"]["post_intervals"]) / len(self.daily_tracking["timing"]["post_intervals"]) if self.daily_tracking["timing"]["post_intervals"] else 0,
            "engagement_distribution": {
                k: f"{(v/total_posts)*100:.0f}%" if total_posts > 0 else "0%"
                for k, v in self.daily_tracking["engagement"]["post_types"].items()
            } if total_posts > 0 else {}
        }

    def can_use_theorist(self, theorist: str, category: str) -> bool:
        """Check if a theorist can be used based on distribution rules."""
        current_time = time.time()

        # Check cooldown period
        last_used = self.daily_tracking["theorist_usage"][category]["last_used"].get(theorist, 0)
        if current_time - last_used < 48 * 3600:  # 48 hours in seconds
            return False

        # Check category distribution
        total_posts = self.daily_tracking["total_posts"]
        if total_posts > 0:
            category_usage = self.daily_tracking["theorist_usage"][category]["count"] / total_posts
            target_ratio = {
                "mediaTheory": 0.35,
                "criticalTheory": 0.35,
                "technologyStudies": 0.25,
                "philosophyOthers": 0.05
            }[category]

            if category_usage >= target_ratio + 0.05:  # Allow 5% margin
                return False

        return True

    def record_theorist_usage(self, theorist: str, category: str):
        """Record usage of a theorist."""
        self.daily_tracking["theorist_usage"][category]["count"] += 1
        self.daily_tracking["theorist_usage"][category]["last_used"][theorist] = time.time()
        self.daily_tracking["total_posts"] += 1
        self.weekly_tracking[category] += 1

    def get_recommended_theorist(self) -> Tuple[str, str]:
        """Get a recommended theorist based on current distribution."""
        # Calculate current distributions
        total_posts = self.daily_tracking["total_posts"]
        if total_posts == 0:
            # If no posts yet, prioritize PRIMARY categories
            categories = ["mediaTheory", "criticalTheory"]
            category = random.choice(categories)
            theorists = {
                "mediaTheory": ["McLuhan", "Kittler", "Chun", "Hayles"],
                "criticalTheory": ["Benjamin", "Virilio", "Braidotti", "Haraway"]
            }[category]
            return random.choice(theorists), category

        # Calculate which category needs more representation
        distributions = {
            cat: self.daily_tracking["theorist_usage"][cat]["count"] / total_posts
            for cat in self.daily_tracking["theorist_usage"]
        }

        target_ratios = {
            "mediaTheory": 0.35,
            "criticalTheory": 0.35,
            "technologyStudies": 0.25,
            "philosophyOthers": 0.05
        }

        # Find the category that's furthest below its target
        category = min(
            distributions.keys(),
            key=lambda k: distributions[k] - target_ratios[k]
        )

        # Get available theorists from that category
        theorists = {
            "mediaTheory": ["McLuhan", "Kittler", "Chun", "Hayles"],
            "criticalTheory": ["Benjamin", "Virilio", "Braidotti", "Haraway"],
            "technologyStudies": ["Simondon", "Latour", "Ihde", "Stiegler"],
            "philosophyOthers": ["Deleuze", "Derrida", "Foucault", "Wittgenstein", "Wiener", "Bateson", "Prigogine"]
        }[category]

        # Filter out recently used theorists
        available_theorists = [
            t for t in theorists
            if self.can_use_theorist(t, category)
        ]

        if not available_theorists:
            # If no theorists available in preferred category, try others
            for cat in target_ratios:
                if cat != category:
                    available_theorists = [
                        t for t in theorists[cat]
                        if self.can_use_theorist(t, cat)
                    ]
                    if available_theorists:
                        return random.choice(available_theorists), cat

        return random.choice(available_theorists), category

    def get_weekly_balance_report(self) -> Dict[str, float]:
        """Get report on weekly category balance."""
        total = sum(self.weekly_tracking.values())
        if total == 0:
            return {cat: 0.0 for cat in self.weekly_tracking}

        return {
            cat: count / total
            for cat, count in self.weekly_tracking.items()
        }

    def reset_weekly_tracking(self):
        """Reset weekly tracking counters."""
        self.weekly_tracking = {
            "mediaTheory": 0,
            "criticalTheory": 0,
            "technologyStudies": 0,
            "philosophyOthers": 0
        }

def main():
    if len(sys.argv) != 2:
        print("Usage: python monitor.py <log_file>")
        sys.exit(1)

    monitor = LLMLensMonitor()

    # Read and process log file
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        for line in f:
            monitor.process_log_line(line)

    # Generate and output report
    report = monitor.generate_report()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()