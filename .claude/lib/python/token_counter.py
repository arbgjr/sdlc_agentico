#!/usr/bin/env python3
"""
Token Budget Monitoring and Enforcement

Tracks context token usage and enforces budget limits to prevent overflow.
Based on OpenClaw pattern: cache-ttl pruning, context monitoring.

Usage:
    from token_counter import TokenBudget

    budget = TokenBudget()
    status = budget.get_status()
    budget.warn_if_approaching_limit()
"""

import os
import json
import tiktoken
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Token usage breakdown"""
    total: int
    bootstrap_files: int
    tool_schemas: int
    conversation_history: int
    skills_metadata: int
    agents_metadata: int
    corpus: int


class TokenBudget:
    """Token budget monitoring and enforcement"""

    def __init__(self, config_path: str = ".claude/settings.json"):
        self.config = self._load_config(config_path)
        self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4/Claude encoding

    def _load_config(self, config_path: str) -> Dict:
        """Load token budget configuration"""
        try:
            with open(config_path, "r") as f:
                settings = json.load(f)
                return settings.get("sdlc", {}).get("token_budget", {
                    "enabled": True,
                    "global_max": 200000,
                    "per_agent_max": 50000,
                    "orchestrator_max": 80000,
                    "warning_threshold": 0.8,
                })
        except Exception:
            return {
                "enabled": True,
                "global_max": 200000,
                "warning_threshold": 0.8,
            }

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def get_file_tokens(self, file_path: str) -> int:
        """Count tokens in a file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.count_tokens(content)
        except Exception:
            return 0

    def get_directory_tokens(self, directory: str, pattern: str = "**/*.md") -> int:
        """Count tokens in all files matching pattern"""
        total = 0
        base_path = Path(directory)

        if not base_path.exists():
            return 0

        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                total += self.get_file_tokens(str(file_path))

        return total

    def estimate_tool_schemas(self) -> int:
        """
        Estimate tokens used by tool schemas.
        Based on OpenClaw analysis: ~2,500 tokens for complex tools
        """
        # Rough estimate based on available tools
        tools_count = 20  # Approximate number of tools
        avg_tokens_per_tool = 150  # Conservative estimate
        return tools_count * avg_tokens_per_tool

    def get_bootstrap_tokens(self) -> int:
        """
        Calculate tokens from bootstrap files (agents, skills, orchestrator).
        OpenClaw recommendation: < 5KB each file
        """
        total = 0

        # Orchestrator
        orchestrator_path = ".claude/agents/orchestrator.md"
        if os.path.exists(orchestrator_path):
            total += self.get_file_tokens(orchestrator_path)

        # Skills metadata (not full SKILL.md, just discovery metadata)
        # NOTE: With just-in-time loading, this should be much smaller
        skills_dir = ".claude/skills"
        if os.path.exists(skills_dir):
            # Estimate: 100 tokens per skill metadata × 30 skills = 3,000 tokens
            total += 3000  # Conservative estimate for metadata only

        return total

    def get_corpus_tokens(self) -> int:
        """
        Estimate tokens from corpus that might be loaded.
        With just-in-time loading, this should be minimal.
        """
        # Conservative estimate: Recent ADRs and patterns
        total = 0

        corpus_path = Path(".agentic_sdlc/corpus")
        if corpus_path.exists():
            # Count only recent decisions (last 10)
            decisions_dir = corpus_path / "nodes" / "decisions"
            if decisions_dir.exists():
                decision_files = sorted(decisions_dir.glob("*.yml"),
                                       key=lambda p: p.stat().st_mtime,
                                       reverse=True)[:10]
                for file_path in decision_files:
                    total += self.get_file_tokens(str(file_path))

        return min(total, 10000)  # Cap at 10K tokens

    def get_current_usage(self) -> TokenUsage:
        """Get current token usage breakdown"""
        return TokenUsage(
            total=0,  # Calculated below
            bootstrap_files=self.get_bootstrap_tokens(),
            tool_schemas=self.estimate_tool_schemas(),
            conversation_history=0,  # Unknown without Claude API access
            skills_metadata=3000,  # Estimated above
            agents_metadata=2000,  # Rough estimate
            corpus=self.get_corpus_tokens(),
        )

    def get_status(self) -> Dict:
        """Get token budget status"""
        usage = self.get_current_usage()

        # Calculate total (without conversation history)
        known_usage = (
            usage.bootstrap_files +
            usage.tool_schemas +
            usage.skills_metadata +
            usage.agents_metadata +
            usage.corpus
        )

        global_max = self.config["global_max"]
        warning_threshold = self.config["warning_threshold"]

        # Estimate conversation history (assume 20% of budget)
        estimated_conversation = int(global_max * 0.2)
        total_estimated = known_usage + estimated_conversation

        percentage_used = (total_estimated / global_max) * 100
        is_warning = (total_estimated / global_max) >= warning_threshold

        return {
            "enabled": self.config.get("enabled", True),
            "budget": {
                "global_max": global_max,
                "per_agent_max": self.config.get("per_agent_max", 50000),
                "orchestrator_max": self.config.get("orchestrator_max", 80000),
            },
            "usage": {
                "known_usage": known_usage,
                "estimated_conversation": estimated_conversation,
                "total_estimated": total_estimated,
                "percentage": round(percentage_used, 1),
            },
            "breakdown": {
                "bootstrap_files": usage.bootstrap_files,
                "tool_schemas": usage.tool_schemas,
                "skills_metadata": usage.skills_metadata,
                "agents_metadata": usage.agents_metadata,
                "corpus": usage.corpus,
                "conversation_history": estimated_conversation,
            },
            "status": "WARNING" if is_warning else "OK",
            "recommendations": self._get_recommendations(usage, known_usage, global_max),
        }

    def _get_recommendations(self, usage: TokenUsage, known_usage: int, global_max: int) -> List[str]:
        """Generate recommendations for reducing token usage"""
        recommendations = []

        # Check orchestrator size
        orchestrator_tokens = self.get_file_tokens(".claude/agents/orchestrator.md")
        if orchestrator_tokens > 5000:  # OpenClaw: 5KB limit per file
            recommendations.append(
                f"⚠️ orchestrator.md is {orchestrator_tokens:,} tokens "
                f"(target: <5,000). Apply progressive disclosure pattern."
            )

        # Check if approaching limit
        percentage = (known_usage / global_max) * 100
        if percentage > 60:
            recommendations.append(
                f"⚠️ Known usage at {percentage:.1f}%. Consider implementing "
                f"just-in-time skill loading."
            )

        # Check bootstrap size
        if usage.bootstrap_files > 15000:
            recommendations.append(
                f"⚠️ Bootstrap files use {usage.bootstrap_files:,} tokens "
                f"(target: <10,000). Split large files into reference/*.md"
            )

        if not recommendations:
            recommendations.append("✅ Token usage is healthy")

        return recommendations

    def warn_if_approaching_limit(self) -> None:
        """Print warning if approaching token limit"""
        status = self.get_status()

        if not status["enabled"]:
            return

        if status["status"] == "WARNING":
            print(f"\n⚠️  TOKEN BUDGET WARNING", flush=True)
            print(f"Current usage: {status['usage']['total_estimated']:,} / {status['budget']['global_max']:,} tokens", flush=True)
            print(f"Percentage: {status['usage']['percentage']}%", flush=True)
            print(f"\nRecommendations:", flush=True)
            for rec in status["recommendations"]:
                print(f"  {rec}", flush=True)
            print()


def main():
    """CLI entrypoint for token budget monitoring"""
    import sys

    budget = TokenBudget()
    status = budget.get_status()

    # Print status
    print(f"\n📊 TOKEN BUDGET STATUS\n")
    print(f"Budget: {status['budget']['global_max']:,} tokens (global max)")
    print(f"Per-agent max: {status['budget']['per_agent_max']:,} tokens")
    print(f"Orchestrator max: {status['budget']['orchestrator_max']:,} tokens")
    print()

    print(f"Known Usage: {status['usage']['known_usage']:,} tokens")
    print(f"Estimated Total: {status['usage']['total_estimated']:,} tokens ({status['usage']['percentage']}%)")
    print(f"Status: {status['status']}")
    print()

    print(f"Breakdown:")
    for key, value in status['breakdown'].items():
        label = key.replace('_', ' ').title()
        print(f"  {label}: {value:,} tokens")
    print()

    print(f"Recommendations:")
    for rec in status['recommendations']:
        print(f"  {rec}")
    print()

    # Exit with warning code if approaching limit
    if status['status'] == 'WARNING':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
