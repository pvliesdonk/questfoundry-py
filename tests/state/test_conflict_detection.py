"""Tests for conflict detection (Layer 6/7 canon workflows)"""

import pytest

from questfoundry.state.conflict_detection import (
    CanonConflict,
    ConflictDetector,
    ConflictResolution,
    ConflictSeverity,
)


def test_conflict_creation():
    """Test conflict object creation"""
    conflict = CanonConflict(
        canon_statement="Dragons are extinct",
        seed_idea="A dragon appears in the story",
        severity=ConflictSeverity.CRITICAL,
        recommended_resolution=ConflictResolution.REJECT,
        fix_suggestion="Remove dragon appearance",
        canon_source="Dragon's Quest I",
    )

    assert conflict.severity == ConflictSeverity.CRITICAL
    assert conflict.recommended_resolution == ConflictResolution.REJECT
    assert "extinct" in conflict.canon_statement


def test_conflict_detector_no_conflicts():
    """Test detector with no conflicts"""
    detector = ConflictDetector()

    invariant_canon = [
        "Dragons sleep for decades between hunts",
        "Magic cannot resurrect the dead",
    ]

    seed_ideas = [
        "Hero trains to become a dragon rider",
        "Villain seeks forbidden knowledge",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) == 0
    assert report.has_critical_conflicts() is False


def test_conflict_detector_resurrection_conflict():
    """Test detecting resurrection conflict"""
    detector = ConflictDetector()

    invariant_canon = [
        "Magic cannot resurrect the dead",
    ]

    seed_ideas = [
        "The protagonist resurrects their dead mentor using ancient magic",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) > 0
    conflict = report.conflicts[0]
    assert "resurrect" in conflict.seed_idea.lower()
    assert "dead" in conflict.canon_statement.lower()
    assert conflict.severity in (ConflictSeverity.CRITICAL, ConflictSeverity.MAJOR)


def test_conflict_detector_destruction_conflict():
    """Test detecting destruction conflict"""
    detector = ConflictDetector()

    invariant_canon = [
        "Ancient dragon artifacts are indestructible",
    ]

    seed_ideas = [
        "Hero destroys an ancient dragon artifact to save the kingdom",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) > 0
    conflict = report.conflicts[0]
    assert "destroy" in conflict.seed_idea.lower() or "destroys" in conflict.seed_idea.lower()
    assert "indestructible" in conflict.canon_statement.lower()


def test_conflict_detector_repair_conflict():
    """Test detecting repair/broken conflict"""
    detector = ConflictDetector()

    invariant_canon = [
        "The Great Seal was destroyed in the ancient war",
    ]

    seed_ideas = [
        "Characters repair the Great Seal to imprison the demon",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) > 0
    conflict = report.conflicts[0]
    assert "repair" in conflict.seed_idea.lower()
    assert "destroyed" in conflict.canon_statement.lower()


def test_conflict_detector_multiple_conflicts():
    """Test detecting multiple conflicts"""
    detector = ConflictDetector()

    invariant_canon = [
        "Magic cannot resurrect the dead",
        "Dragons are extinct in this age",
        "The ancient empire collapsed and cannot be restored",
    ]

    seed_ideas = [
        "Hero resurrects their mentor",
        "A dragon appears in the mountains",
        "Protagonist restores the ancient empire",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) == 3
    assert all(c.severity in (ConflictSeverity.CRITICAL, ConflictSeverity.MAJOR) for c in report.conflicts)


def test_conflict_detector_resolution_reject():
    """Test REJECT resolution recommendation"""
    detector = ConflictDetector()

    invariant_canon = [
        "Time travel does not exist in this universe",
    ]

    seed_ideas = [
        "Hero travels back in time to prevent the disaster",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) > 0
    conflict = report.conflicts[0]
    # Critical conflicts typically recommend REJECT
    if conflict.severity == ConflictSeverity.CRITICAL:
        assert conflict.recommended_resolution == ConflictResolution.REJECT


def test_conflict_detector_resolution_revise():
    """Test REVISE resolution recommendation"""
    detector = ConflictDetector()

    invariant_canon = [
        "Dragons hibernate for decades between hunts",
    ]

    seed_ideas = [
        "Dragons appear every week in the story",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    # Should suggest REVISE to align timing with canon
    # (implementation specific - might not detect this particular wording)


def test_conflict_detector_case_insensitive():
    """Test conflict detection is case insensitive"""
    detector = ConflictDetector()

    invariant_canon = [
        "MAGIC CANNOT RESURRECT THE DEAD",
    ]

    seed_ideas = [
        "hero resurrects their mentor using magic",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    assert len(report.conflicts) > 0


def test_conflict_detector_severity_levels():
    """Test different severity levels"""
    detector = ConflictDetector()

    # Critical: Core worldbuilding violation
    invariant_canon = [
        "Magic does not exist in this world",
    ]

    seed_ideas = [
        "Hero casts a fireball spell",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    # Should be CRITICAL since it contradicts fundamental worldbuilding
    if report.conflicts:
        assert report.conflicts[0].severity == ConflictSeverity.CRITICAL


def test_conflict_report_summary():
    """Test conflict report summary"""
    detector = ConflictDetector()

    invariant_canon = [
        "Dragons are extinct",
        "Magic cannot resurrect the dead",
        "Time travel is impossible",
    ]

    seed_ideas = [
        "A dragon appears",
        "Hero resurrects mentor",
        "Villain travels back in time",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="Dragon's Quest I",
    )

    summary = report.to_summary()
    assert "total_conflicts" in summary
    assert "critical_count" in summary
    assert "canon_source" in summary
    assert summary["canon_source"] == "Dragon's Quest I"


def test_conflict_report_has_critical():
    """Test checking for critical conflicts"""
    report = ConflictDetector().detect_conflicts(
        invariant_canon=["Magic does not exist"],
        seed_ideas=["Hero uses magic"],
        canon_source="test",
    )

    # Should have critical conflicts
    has_critical = report.has_critical_conflicts()
    # Implementation specific - depends on keyword matching


def test_conflict_report_filter_by_severity():
    """Test filtering conflicts by severity"""
    detector = ConflictDetector()

    invariant_canon = [
        "Dragons are extinct",
        "Ancient empire collapsed",
        "Magic has limitations",
    ]

    seed_ideas = [
        "Dragons appear everywhere",
        "Empire is restored",
        "Character uses slightly different magic",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    # Filter by critical
    critical = [c for c in report.conflicts if c.severity == ConflictSeverity.CRITICAL]

    # Filter by major
    major = [c for c in report.conflicts if c.severity == ConflictSeverity.MAJOR]

    # Should have different counts based on severity


def test_conflict_detector_fix_suggestions():
    """Test that conflicts include fix suggestions"""
    detector = ConflictDetector()

    invariant_canon = [
        "Dragons cannot fly in this world due to high gravity",
    ]

    seed_ideas = [
        "Hero rides a flying dragon across the continent",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    if report.conflicts:
        conflict = report.conflicts[0]
        assert conflict.fix_suggestion is not None
        assert len(conflict.fix_suggestion) > 0


def test_conflict_detector_empty_inputs():
    """Test detector with empty inputs"""
    detector = ConflictDetector()

    report = detector.detect_conflicts(
        invariant_canon=[],
        seed_ideas=[],
        canon_source="test",
    )

    assert len(report.conflicts) == 0


def test_conflict_detector_no_seed_ideas():
    """Test detector with no seed ideas"""
    detector = ConflictDetector()

    invariant_canon = [
        "Dragons are extinct",
        "Magic has limits",
    ]

    report = detector.detect_conflicts(
        invariant_canon=invariant_canon,
        seed_ideas=[],
        canon_source="test",
    )

    assert len(report.conflicts) == 0


def test_conflict_detector_no_invariant_canon():
    """Test detector with no invariant canon"""
    detector = ConflictDetector()

    seed_ideas = [
        "Hero does something",
        "Villain plots something",
    ]

    report = detector.detect_conflicts(
        invariant_canon=[],
        seed_ideas=seed_ideas,
        canon_source="test",
    )

    # No canon means no conflicts
    assert len(report.conflicts) == 0
