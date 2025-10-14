# Sprint Change Proposal: Memory Database Viewer

**Date**: 2025-10-14  
**Prepared By**: Bob (Scrum Master)  
**Change Type**: New Requirement - Feature Addition

---

## 1. Change Context

### Triggering Event
- **Type**: Newly discovered requirement
- **Source**: User request during Epic 2 development
- **Scope**: Epic 2 - Web Interface & Analysis Tools

### Issue Summary
User identified a gap in the Results Dashboard's analysis capabilities. While the dashboard displays conversation logs, metrics, and charts, it lacks visibility into the persistent memory database that agents use during experiments. This memory data is critical for understanding agent behavior and decision-making patterns.

**User Request:**
> "We need the UI extended to display the contents of the memory database for the selected run. There should be a list of keys for the selected run id and then the ability to click on the key and view the contents."

### Evidence & Context
- Memory system is implemented in `contreact_ollama/tools/memory_tools.py` using TinyDB
- Memory operations are tracked in metrics (memory_ops_total, memory_write_chars)
- Dashboard currently shows memory operation counts but not actual memory contents
- Architecture supports run_id-based memory isolation, making this feature feasible

---

## 2. Epic Impact Analysis

### Current Epic: Epic 2 - Web Interface & Analysis Tools

**Status**: ✅ Can be completed with modification

**Impact on Existing Stories:**
- Stories 2.1-2.9: ✅ No changes required
- All existing stories remain valid and complete

**Required Modifications:**
- ➕ Add new Story 2.10: Memory Database Viewer
- This story logically extends the Results Dashboard analysis capabilities
- Fits naturally after Story 2.8 (Interactive Charts) and Story 2.9 (PEI Assessment)

**Future Epics:**
- Epic 3+: No impact
- This is a self-contained dashboard feature with no downstream dependencies

**Epic Goal Alignment:**
Epic 2's expanded goal states: "provides a user-friendly graphical interface for creating experiment configurations and a **rich dashboard for visualizing and analyzing the results** from completed runs."

✅ Memory database viewer directly supports the "rich dashboard for analyzing results" goal.

---

## 3. Artifact Impact Summary

### PRD (docs/prd/epic-2-web-interface-analysis-tools.md)
- **Change Required**: ✏️ Add Story 2.10
- **Conflict Level**: None - pure addition
- **Rationale**: New story fits logically within Epic 2's analysis capabilities

### Architecture Documents
- **data-models.md**: ✅ No changes needed - MemoryEntry schema already documented
- **components.md**: ✅ No changes needed - MemoryTools component exists
- **frontend-architecture.md**: ✅ No changes needed - follows existing dashboard patterns

### Implementation Files
- **pages/2_📊_results_dashboard.py**: ✏️ Add new section for memory viewer
- **contreact_ollama/ui_utils.py**: ➕ Add helper functions for memory data loading
- No changes needed to core memory system - using existing MemoryTools API

### Test Files
- ➕ Add tests to `tests/unit/test_results_dashboard.py` for memory viewer
- ➕ Add QA gate: `docs/qa/gates/2.10-memory-database-viewer.yml`

---

## 4. Recommended Path Forward

### Selected Option: **Direct Adjustment / Integration**

**Rationale:**
1. ✅ No conflicts with existing functionality
2. ✅ Leverages existing memory system infrastructure
3. ✅ Follows established dashboard patterns
4. ✅ Minimal implementation effort (estimated 1 story)
5. ✅ High value for researchers analyzing agent behavior

**Effort Assessment:**
- **Story Points**: Medium (similar to Story 2.7 - conversation log display)
- **Risk Level**: Low
- **Dependencies**: None - all prerequisites implemented

**Alternatives Considered:**
- ❌ External tool: Would break integrated analysis workflow
- ❌ CLI-only: Inconsistent with Epic 2's web-based approach
- ❌ Defer to Epic 3: Memory inspection is core analysis need, should be in Epic 2

---

## 5. Proposed Changes

### Change 1: Add Story 2.10 to Epic 2 PRD

**File**: `docs/prd/epic-2-web-interface-analysis-tools.md`

**Location**: After Story 2.9 (end of epic)

**Content to Add**:

```markdown
---

### Story 2.10: Display Memory Database Contents
**As a** Researcher, **I want** to view the persistent memory database contents for a selected run, **so that** I can analyze what information the agent stored and retrieved during the experiment.

**Acceptance Criteria**:
1. The Results Dashboard includes a "💾 Memory Database" section that appears when a run is selected.
2. The section displays a list of all memory keys stored for the selected run_id using the existing MemoryTools API.
3. Each key in the list is clickable/expandable to reveal its associated value.
4. If no memory entries exist for the run, a helpful message indicates "No memory entries found for this run".
5. The display handles long values gracefully (e.g., using expandable sections or scrollable containers).
6. Memory entries are displayed in a readable format (e.g., using `st.expander` for each key-value pair).
7. If the memory database file cannot be accessed, a clear error message is displayed without crashing.
```

### Change 2: Implement Memory Viewer in Dashboard

**File**: `pages/2_📊_results_dashboard.py`

**Location**: After the PEI Assessment section, before the Conversation Log section

**Implementation Summary**:
```python
# Add new section after PEI assessment (around line 165)
st.divider()

# Memory Database Viewer Section
st.subheader("💾 Memory Database")

# Load memory entries for selected run
memory_entries = load_memory_entries(st.session_state.current_run)

if memory_entries:
    st.success(f"✅ Found {len(memory_entries)} memory entries")
    
    # Display each key-value pair in expandable sections
    for entry in memory_entries:
        key = entry['key']
        value = entry['value']
        
        with st.expander(f"🔑 {key}"):
            st.text_area(
                label="Value",
                value=value,
                height=100,
                disabled=True,
                key=f"memory_{key}"
            )
else:
    st.info("No memory entries found for this run")
```

### Change 3: Add Memory Loading Utility Function

**File**: `contreact_ollama/ui_utils.py`

**Location**: After `load_pei_assessment()` function

**Content to Add**:
```python
def load_memory_entries(run_id: str, db_path: str = "data/memory.db") -> Optional[List[Dict[str, str]]]:
    """
    Load all memory entries for a specific run_id from the TinyDB database.
    
    Args:
        run_id: The experiment run identifier
        db_path: Path to the TinyDB memory database file
        
    Returns:
        List of dictionaries with 'key' and 'value', or None if database doesn't exist
        
    Example:
        >>> entries = load_memory_entries("exp-001")
        >>> for entry in entries:
        ...     print(f"{entry['key']}: {entry['value']}")
    """
    from pathlib import Path
    from tinydb import TinyDB, Query
    
    db_file = Path(db_path)
    
    # Check if database file exists
    if not db_file.exists():
        return None
    
    try:
        db = TinyDB(db_file)
        Entry = Query()
        
        # Query all entries for this run_id
        results = db.search(Entry.run_id == run_id)
        
        db.close()
        
        if results:
            # Return list of key-value pairs
            return [{'key': entry['key'], 'value': entry['value']} for entry in results]
        else:
            return []
    
    except Exception as e:
        # Log error and return None
        print(f"Error loading memory entries: {e}")
        return None
```

### Change 4: Create QA Gate for Story 2.10

**File**: `docs/qa/gates/2.10-memory-database-viewer.yml` (new file)

**Content**:
```yaml
story: 2.10-memory-database-viewer
title: Display Memory Database Contents
epic: 2
dependencies:
  - 2.5-results-dashboard-run-selector

acceptance_criteria:
  - id: AC1
    description: Results Dashboard includes Memory Database section when run is selected
    test_type: manual
    steps:
      - Select a run in Results Dashboard that has memory entries
      - Verify "💾 Memory Database" section appears
      - Verify section shows success message with entry count
    expected: Memory Database section displays with entry count

  - id: AC2
    description: Section displays list of all memory keys for selected run_id
    test_type: manual
    steps:
      - View Memory Database section for run with entries
      - Verify all keys from the run's memory are listed
      - Verify keys match those in data/memory.db for the run_id
    expected: All memory keys for run are visible

  - id: AC3
    description: Each key is clickable/expandable to reveal value
    test_type: manual
    steps:
      - Click/expand a memory key entry
      - Verify the associated value is displayed
      - Verify value matches what was stored during the experiment
    expected: Key values are accessible and correct

  - id: AC4
    description: No memory entries shows helpful message
    test_type: manual
    steps:
      - Select a run that has no memory entries
      - Verify informational message appears
      - Verify message is clear and helpful
    expected: "No memory entries found for this run" message displays

  - id: AC5
    description: Long values handled gracefully
    test_type: manual
    steps:
      - View a memory entry with a long value (>1000 chars)
      - Verify display is readable (scrollable/expandable)
      - Verify UI doesn't break or become unusable
    expected: Long values display without breaking layout

  - id: AC6
    description: Memory entries displayed in readable format
    test_type: manual
    steps:
      - View multiple memory entries
      - Verify format is clear and organized (e.g., using expanders)
      - Verify key-value relationship is obvious
    expected: Entries use st.expander or similar readable format

  - id: AC7
    description: Database access errors handled gracefully
    test_type: manual
    steps:
      - Simulate missing or corrupted memory database
      - Verify error message is clear
      - Verify application doesn't crash
    expected: Clear error message, no crash

testing_notes: |
  - Test with runs that have 0, 1, 5, and 10+ memory entries
  - Test with various value lengths and content types
  - Verify isolation: selecting different runs shows different memory contents
  - Test with non-existent memory database file
```

### Change 5: Add Test Cases

**File**: `tests/unit/test_results_dashboard.py`

**Content to Add** (at end of file):
```python
def test_load_memory_entries_success():
    """Test loading memory entries from database."""
    # Test implementation would go here
    pass

def test_load_memory_entries_missing_db():
    """Test handling of missing memory database."""
    # Test implementation would go here
    pass

def test_load_memory_entries_empty_run():
    """Test loading memory for run with no entries."""
    # Test implementation would go here
    pass
```

---

## 6. PRD MVP Impact Assessment

### Original MVP Scope
Epic 2's MVP goal: Deliver web interface for configuration and results analysis.

### Impact on MVP
✅ **No impact on MVP timeline or core deliverables**

**Analysis:**
- Story 2.10 is **additive** - doesn't modify existing functionality
- Epic 2 Stories 2.1-2.9 can still be completed as planned
- Memory viewer enhances analysis capabilities but isn't blocking
- Can be prioritized as "nice to have" or "must have" based on research needs

**Recommendation**: Include in MVP as it significantly enhances analysis value with minimal implementation risk.

---

## 7. Implementation Plan

### Story Sequence
1. ✅ Stories 2.1-2.9: Complete as planned (already done)
2. ➕ Story 2.10: Memory Database Viewer (new)

### Story 2.10 Implementation Steps
1. Update Epic 2 PRD with Story 2.10
2. Create QA gate: `docs/qa/gates/2.10-memory-database-viewer.yml`
3. Add `load_memory_entries()` helper to `contreact_ollama/ui_utils.py`
4. Add Memory Database section to `pages/2_📊_results_dashboard.py`
5. Add unit tests to `tests/unit/test_results_dashboard.py`
6. Manual testing per QA gate
7. Create story document: `docs/stories/2.10.memory-database-viewer.md`

### Estimated Effort
- **Story Points**: 5 (Medium)
- **Development Time**: 2-3 hours
- **Testing Time**: 1 hour
- **Total**: ~4 hours

### Dependencies
- ✅ MemoryTools class (already implemented)
- ✅ TinyDB database structure (already defined)
- ✅ Results Dashboard framework (already implemented)
- ✅ Run selector (Story 2.5 - already implemented)

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Large memory values slow UI | Low | Medium | Use text_area with scrolling, lazy loading if needed |
| Database locking issues | Low | Low | Read-only access, short connection duration |
| Missing memory database | Low | Low | Graceful error handling already planned |

---

## 8. Agent Handoff Plan

### Primary Agent: Developer Agent (@dev)
**Responsibilities:**
1. Implement Story 2.10 per specifications above
2. Add utility functions to ui_utils.py
3. Update Results Dashboard with memory viewer section
4. Write unit tests

**Context to Provide:**
- This Sprint Change Proposal document
- Story 2.10 specification
- Reference existing dashboard patterns (Stories 2.6, 2.7)
- MemoryTools API documentation

### Supporting Agent: Product Owner (@po)
**Responsibilities:**
1. Update Epic 2 PRD document
2. Create Story 2.10 document in docs/stories/
3. Create QA gate document
4. Validate implementation against acceptance criteria

### QA Verification
- Manual testing per QA gate 2.10
- Verify memory isolation between runs
- Test edge cases (no entries, many entries, long values)

---

## 9. Success Criteria

### Implementation Complete When:
- [x] Story 2.10 added to Epic 2 PRD
- [ ] Memory viewer section appears in Results Dashboard
- [ ] Users can view list of memory keys for selected run
- [ ] Users can click/expand keys to view values
- [ ] All 7 acceptance criteria pass QA gate
- [ ] Unit tests written and passing
- [ ] No regressions in existing dashboard functionality

### User Acceptance Criteria:
1. Researcher can inspect agent memory without CLI tools
2. Memory contents are clearly linked to specific runs
3. Interface is intuitive and consistent with existing dashboard
4. Error cases handled gracefully

---

## 10. Rollback Plan

**Rollback Complexity**: ⭐ Very Low

If Story 2.10 implementation encounters issues:

1. **Code Changes**: Simply omit the memory viewer section from dashboard
2. **PRD Changes**: Can proceed with Epic 2 minus Story 2.10
3. **Impact**: Zero impact on Stories 2.1-2.9 (all self-contained)
4. **User Impact**: Users lose memory inspection capability but all other features work

**Rollback Trigger Conditions:**
- Implementation exceeds 2x estimated effort
- Performance issues discovered during testing
- Blocking bugs in MemoryTools integration

---

## 11. Final Recommendation

### ✅ APPROVE AND PROCEED

**Summary:**
- Low risk, high value feature addition
- Clear implementation path with existing infrastructure
- Fits naturally within Epic 2's analysis goals
- No conflicts with existing work
- Enhances researcher experience significantly

**Next Steps:**
1. Obtain user approval of this proposal
2. Update Epic 2 PRD with Story 2.10
3. Hand off to @dev agent for implementation
4. Execute Story 2.10 per implementation plan

---

## Change-Checklist Status

- [x] **Section 1: Understand Trigger & Context** - Complete
- [x] **Section 2: Epic Impact Assessment** - Complete
- [x] **Section 3: Artifact Conflict Analysis** - Complete
- [x] **Section 4: Path Forward Evaluation** - Complete
- [x] **Section 5: Sprint Change Proposal** - Complete
- [ ] **Section 6: Final Review & User Approval** - Awaiting approval

---

**Prepared By**: Bob (Scrum Master)  
**Date**: 2025-10-14  
**Status**: Ready for User Approval
