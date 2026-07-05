"""Voice learning and style analysis for AI documentation co-pilot.

This module analyzes existing documentation patterns in a dbt project to enable
the AI co-pilot to match the team's documentation style, terminology, and voice.
"""

from __future__ import annotations

import typing as t
from collections import Counter
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from dbt.contracts.graph.nodes import ResultNode

    from dbt_osmosis.core.dbt_protocols import YamlRefactorContextProtocol

_COMMON_PHRASE_STOP_WORDS = frozenset({"the", "a", "an", "of", "in", "and", "or", "for"})
_IMPERATIVE_VERBS = frozenset({"contains", "represents", "stores", "holds", "tracks", "records"})
_PASSIVE_PATTERNS = frozenset({"is used to", "is a", "contains a", "represents a"})
_TECH_TERMS = frozenset({
    "id",
    "key",
    "fk",
    "pk",
    "timestamp",
    "json",
    "uuid",
    "integer",
    "varchar",
})

__all__ = [
    "ProjectStyleProfile",
    "analyze_project_documentation_style",
    "extract_style_examples",
    "find_similar_documented_nodes",
]


@dataclass
class ProjectStyleProfile:
    """Profile of documentation style patterns in a dbt project.

    Attributes:
        description_length_stats: Statistics about description lengths
        common_phrases: Frequently used phrases in descriptions
        terminology_preferences: Preferred terminology patterns
        sentence_structure: Patterns in sentence construction
        tone_markers: Indicators of documentation tone
    """

    description_length_stats: dict[str, float] = field(default_factory=dict)
    common_phrases: list[tuple[str, int]] = field(default_factory=list)
    terminology_preferences: dict[str, str] = field(default_factory=dict)
    sentence_structure: dict[str, float] = field(default_factory=dict)
    tone_markers: dict[str, int] = field(default_factory=dict)

    # Raw samples for few-shot learning
    model_description_samples: list[str] = field(default_factory=list)
    column_description_samples: list[str] = field(default_factory=list)

    def to_prompt_context(self, max_examples: int = 3) -> str:
        """Convert style profile to prompt context for LLM.

        Args:
            max_examples: Maximum number of examples to include

        Returns:
            Formatted string for LLM prompt
        """
        sections = []

        # Style guidelines
        if self.description_length_stats:
            avg_len = self.description_length_stats.get("avg_length", 0)
            sections.append(
                f"- Target description length: ~{int(avg_len)} words "
                f"(range: {int(self.description_length_stats.get('min_length', 0))}-"
                f"{int(self.description_length_stats.get('max_length', 0))})"
            )

        if self.common_phrases:
            top_phrases = [phrase for phrase, _ in self.common_phrases[:5]]
            sections.append(f"- Common phrases: {', '.join(top_phrases)}")

        if self.terminology_preferences:
            sections.append("- Terminology preferences:")
            for preferred, alternative in list(self.terminology_preferences.items())[:3]:
                sections.append(f"  - Use '{preferred}' instead of '{alternative}'")

        # Few-shot examples
        if self.model_description_samples:
            sections.append("\n# Model Description Examples:")
            for i, example in enumerate(self.model_description_samples[:max_examples], 1):
                sections.append(f"{i}. {example}")

        if self.column_description_samples:
            sections.append("\n# Column Description Examples:")
            for i, example in enumerate(self.column_description_samples[:max_examples], 1):
                sections.append(f"{i}. {example}")

        return "\n".join(sections) if sections else "No style information available."


def _analyze_description_lengths(
    descriptions: list[str],
) -> dict[str, float]:
    """Analyze length statistics of descriptions.

    Args:
        descriptions: List of description strings

    Returns:
        Dictionary with length statistics
    """
    if not descriptions:
        return {}

    word_counts = [len(d.split()) for d in descriptions if d and d.strip()]

    if not word_counts:
        return {}

    return {
        "avg_length": sum(word_counts) / len(word_counts),
        "min_length": min(word_counts),
        "max_length": max(word_counts),
        "median_length": sorted(word_counts)[len(word_counts) // 2],
    }


def _extract_common_phrases(
    descriptions: list[str],
    min_frequency: int = 2,
) -> list[tuple[str, int]]:
    """Extract frequently used phrases from descriptions.

    Args:
        descriptions: List of description strings
        min_frequency: Minimum occurrence count to include

    Returns:
        List of (phrase, count) tuples sorted by frequency
    """
    if not descriptions:
        return []

    phrases: Counter[str] = Counter()
    for phrase in _iter_common_phrase_candidates(descriptions):
        phrases[phrase] += 1

    # Return most common phrases above threshold
    return [(p, c) for p, c in phrases.most_common(20) if c >= min_frequency]


def _iter_common_phrase_candidates(descriptions: list[str]) -> t.Iterator[str]:
    for desc in descriptions:
        if not desc or not desc.strip():
            continue
        words = desc.lower().split()
        for n in [2, 3, 4]:
            yield from _iter_informative_ngrams(words, n)


def _iter_informative_ngrams(words: list[str], n: int) -> t.Iterator[str]:
    for i in range(len(words) - n + 1):
        phrase = " ".join(words[i : i + n])
        if _is_informative_phrase(phrase):
            yield phrase


def _is_informative_phrase(phrase: str) -> bool:
    return not any(word in _COMMON_PHRASE_STOP_WORDS for word in phrase.split())


def _detect_terminology_patterns(
    descriptions: list[str],
    column_names: list[str] | None = None,
) -> dict[str, str]:
    """Detect terminology preferences from descriptions.

    Args:
        descriptions: List of description strings
        column_names: Optional list of column names for context

    Returns:
        Dictionary mapping preferred terms to alternatives
    """
    terminology: dict[str, str] = {}

    if not descriptions:
        return terminology

    # Common terminology variations to detect
    variations = [
        ("user", "customer", "client", "account"),
        ("id", "identifier", "key"),
        ("email", "email address", "e-mail"),
        ("timestamp", "datetime", "created at", "updated at"),
        ("foreign key", "reference", "ref"),
        ("primary key", "main id", "unique identifier"),
    ]

    all_text = " ".join(descriptions).lower()

    for preferred, *alts in variations:
        preferred_count = all_text.count(preferred)
        for alt in alts:
            alt_count = all_text.count(alt)
            if preferred_count > alt_count and preferred_count >= 2:
                terminology[preferred] = alt

    return terminology


def _detect_tone_markers(descriptions: list[str]) -> dict[str, int]:
    """Detect tone indicators in descriptions.

    Args:
        descriptions: List of description strings

    Returns:
        Dictionary mapping tone markers to counts
    """
    markers = {
        "imperative": 0,  # e.g., "contains", "represents", "stores"
        "passive": 0,  # e.g., "is used to", "contains a"
        "concise": 0,  # short descriptions
        "detailed": 0,  # longer descriptions with multiple clauses
        "technical": 0,  # includes technical terms
    }

    for desc in descriptions:
        if not desc or not desc.strip():
            continue

        _count_description_tone_markers(markers, desc)

    return markers


def _count_description_tone_markers(markers: dict[str, int], desc: str) -> None:
    word_count = len(desc.split())
    desc_lower = desc.lower()

    if word_count <= 5:
        markers["concise"] += 1
    elif word_count >= 15:
        markers["detailed"] += 1

    if any(verb in desc_lower for verb in _IMPERATIVE_VERBS):
        markers["imperative"] += 1
    if any(pattern in desc_lower for pattern in _PASSIVE_PATTERNS):
        markers["passive"] += 1
    if any(term in desc_lower for term in _TECH_TERMS):
        markers["technical"] += 1


def analyze_project_documentation_style(
    context: YamlRefactorContextProtocol,
    max_nodes: int = 50,
    max_columns_per_node: int = 10,
) -> ProjectStyleProfile:
    """Analyze documentation style across a dbt project.

    Args:
        context: The YamlRefactorContext instance
        max_nodes: Maximum number of nodes to analyze
        max_columns_per_node: Maximum columns to analyze per node

    Returns:
        ProjectStyleProfile with discovered patterns
    """
    model_descriptions, column_descriptions, column_names = _collect_documentation_samples(
        context, max_nodes, max_columns_per_node
    )
    return _build_style_profile(model_descriptions, column_descriptions, column_names)


def _collect_documentation_samples(
    context: YamlRefactorContextProtocol,
    max_nodes: int,
    max_columns_per_node: int,
) -> tuple[list[str], list[str], list[str]]:
    from dbt_osmosis.core.node_filters import _iter_candidate_nodes

    model_descriptions: list[str] = []
    column_descriptions: list[str] = []
    column_names: list[str] = []

    for analyzed_count, (_, node) in enumerate(_iter_candidate_nodes(context)):
        if analyzed_count >= max_nodes:
            break

        # Collect model description
        if node.description and node.description not in context.placeholders:
            model_descriptions.append(node.description)

        # Collect column descriptions
        for i, (col_name, col) in enumerate(node.columns.items()):
            if i >= max_columns_per_node:
                break
            if col.description and col.description not in context.placeholders:
                column_descriptions.append(col.description)
                column_names.append(col_name)

    return model_descriptions, column_descriptions, column_names


def _build_style_profile(
    model_descriptions: list[str],
    column_descriptions: list[str],
    column_names: list[str],
) -> ProjectStyleProfile:
    profile = ProjectStyleProfile()

    # Analyze lengths
    all_descriptions = model_descriptions + column_descriptions
    if all_descriptions:
        profile.description_length_stats = _analyze_description_lengths(all_descriptions)

    # Extract common phrases
    if column_descriptions:
        profile.common_phrases = _extract_common_phrases(column_descriptions)

    # Detect terminology patterns
    if column_descriptions:
        profile.terminology_preferences = _detect_terminology_patterns(
            column_descriptions, column_names
        )

    # Detect tone
    if all_descriptions:
        profile.tone_markers = _detect_tone_markers(all_descriptions)

    # Store samples for few-shot learning
    profile.model_description_samples = model_descriptions[:10]
    profile.column_description_samples = column_descriptions[:20]

    return profile


def find_similar_documented_nodes(
    context: YamlRefactorContextProtocol,
    target_node: ResultNode,
    max_results: int = 5,
) -> list[tuple[ResultNode, float]]:
    """Find nodes with similar structure/context that have good documentation.

    Args:
        context: The YamlRefactorContext instance
        target_node: The node to find similar nodes for
        max_results: Maximum number of similar nodes to return

    Returns:
        List of (node, similarity_score) tuples
    """
    from dbt_osmosis.core.node_filters import _iter_candidate_nodes

    # Get target node features
    target_col_count = len(target_node.columns)
    target_has_description = bool(target_node.description)

    # Simple similarity based on column count overlap and documentation quality
    similarities: list[tuple[ResultNode, float]] = []

    for _, node in _iter_candidate_nodes(context):
        if node.unique_id == target_node.unique_id:
            continue

        # Only consider well-documented nodes
        documented_cols = [
            c
            for c in node.columns.values()
            if c.description and c.description not in context.placeholders
        ]
        if len(documented_cols) < len(node.columns) / 2:
            continue

        # Calculate similarity score
        score = 0.0

        # Column count similarity (0-0.3)
        col_diff = abs(len(node.columns) - target_col_count)
        col_similarity = max(0, 1 - (col_diff / max(target_col_count, len(node.columns))))
        score += col_similarity * 0.3

        # Documentation quality (0-0.7)
        doc_ratio = len(documented_cols) / len(node.columns) if node.columns else 0
        score += doc_ratio * 0.7

        if target_has_description and node.description:
            # Bonus if both have model descriptions
            score += 0.1

        similarities.append((node, score))

    # Sort by similarity and return top results
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:max_results]


def extract_style_examples(
    context: YamlRefactorContextProtocol,
    target_node: ResultNode | None = None,
    max_examples: int = 3,
) -> dict[str, list[str]]:
    """Extract style examples for use in LLM prompts.

    Args:
        context: The YamlRefactorContext instance
        target_node: Optional target node to find similar examples for
        max_examples: Maximum examples per category

    Returns:
        Dictionary with example lists by category
    """
    if target_node:
        return _targeted_style_examples(context, target_node, max_examples)

    return _project_style_examples(context, max_examples)


def _empty_style_examples() -> dict[str, list[str]]:
    return {
        "model_descriptions": [],
        "column_descriptions": [],
    }


def _targeted_style_examples(
    context: YamlRefactorContextProtocol,
    target_node: ResultNode,
    max_examples: int,
) -> dict[str, list[str]]:
    examples = _empty_style_examples()
    for node, _ in find_similar_documented_nodes(context, target_node, max_examples):
        _append_node_style_examples(examples, context, node)
    return examples


def _append_node_style_examples(
    examples: dict[str, list[str]],
    context: YamlRefactorContextProtocol,
    node: ResultNode,
) -> None:
    if node.description and node.description not in context.placeholders:
        examples["model_descriptions"].append(f"# {node.name}\n{node.description}")

    for col_name, col in list(node.columns.items())[:3]:
        if col.description and col.description not in context.placeholders:
            examples["column_descriptions"].append(f"- {col_name}: {col.description}")


def _project_style_examples(
    context: YamlRefactorContextProtocol,
    max_examples: int,
) -> dict[str, list[str]]:
    profile = analyze_project_documentation_style(context, max_nodes=20)
    return {
        "model_descriptions": [
            f"# Example {i}\n{desc}"
            for i, desc in enumerate(profile.model_description_samples[:max_examples], 1)
        ],
        "column_descriptions": [
            f"- {desc}" for desc in profile.column_description_samples[:max_examples]
        ],
    }
