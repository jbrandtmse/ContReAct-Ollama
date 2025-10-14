# Sprint Change Proposal: Story 2.7 - Add Event Type Filtering

**Date**: 2025-10-14  
**Triggered By**: Story 2.7 post-implementation user testing  
**Scrum Master**: Bob  
**Status**: Pending Approval  

---

## 1. Issue Summary

**Trigger**: During Story 2.7 implementation review, user discovered that conversation log entries for certain event types (particularly LLM_INVOCATION) can be very lengthy and repetitive, making it difficult to navigate and analyze specific aspects of agent behavior.

**Problem Statement**: The current implementation displays ALL events chronologically without filtering capability. For typical 10-cycle runs with multiple tool calls and verbose LLM invocations, users must scroll through hundreds of lines to find specific information.

**Issue Category**: Newly discovered usability requirement (not a technical limitation or blocking issue)

**Evidence**: 
- User feedback: "we need to be able to feature the log by entry type because the log entries for certain types can be very lengthy and repetitive"
- Current implementation processes all events: CYCLE_START, LLM_INVOCATION, TOOL_CALL, CYCLE_END without filtering options
- LLM_INVOCATION events contain full prompt_messages arrays which can be 1000+ characters per cycle

---

## 2. Epic Impact Assessment

### Current Epic (Epic 2: Web Interface & Analysis Tools)

**Story 2.7 Status**: "Ready for Review"

**Impact Analysis**:
- ✅ Story 2.7 is functionally complete per original acceptance criteria
- ⚠️ Enhancement needed before QA sign-off
- ✅ Stories 2.8 (Interactive Charts) and 2.9 (PEI Assessment Script) are not affected
- ✅ No dependencies or blockers introduced

**Epic Continuity**: 
- Epic 2 can proceed normally after this refinement
- No impact on epic timeline or scope
- Enhancement aligns with Epic 2 goal of "rich dashboard for visualizing and analyzing results"

### Future Epics

**No Impact**: This change is isolated to Story 2.7's conversation log display component.

---

## 3. Artifact Conflict & Impact Analysis

### PRD Review (docs/prd/epic-2-web-interface-analysis-tools.md)

**Story 2.7 Acceptance Criteria**:
1. ✅ "The dashboard includes an expandable section implemented with `st.expander`" - SATISFIED
2. ✅ "When expanded, this section displays the raw conversation history" - SATISFIED
3. ⚠️ "The display is formatted for readability" - PARTIALLY SATISFIED (works but could be more readable with filtering)

**Conclusion**: Current implementation technically meets PRD requirements, but filtering significantly enhances "readability" (AC3). No PRD conflicts.

### Architecture Review (docs/architecture/frontend-architecture.md)

**Relevant Patterns**:
- "Raw Log Viewer: st.expander for expandable section" - ✅ Currently implemented
- "Display formatted conversation history" - ✅ Currently implemented
- Streamlit best practices encourage interactive controls for data exploration

**Proposed Enhancement**: Add `st.multiselect` widget for event type filtering - ALIGNS with architecture patterns

**Conclusion**: No architectural conflicts. Enhancement follows established Streamlit component patterns.

### Other Artifacts

**No Impact**:
- Backend architecture unchanged (read-only display logic)
- Data models unchanged (using existing event_type field)
- Testing strategy enhanced (additional test cases)
- Coding standards maintained (type hints, docstrings, error handling)

---

## 4. Recommended Path Forward

**RECOMMENDATION: Direct Adjustment / Integration**

### Rationale

**Why This Approach**:
1. **Minimal Scope**: Changes isolated to single component within Story 2.7
2. **Low Risk**: Pure UI enhancement, no backend or data model changes
3. **High Value**: Significantly improves usability for primary use case (analyzing long conversation logs)
4. **Fast Implementation**: Estimated 2-4 hours (code + tests)
5. **Before QA Sign-off**: Story 2.7 is "Ready for Review" but not yet QA validated, perfect timing for refinement

**Alternatives Considered**:

**Option A: Create Story 2.7.1 (Rejected)**
- Adds process overhead for small enhancement
- Delays Story 2.7 completion unnecessarily
- Better handled as refinement before QA gate

**Option B: Defer to Future Story (Rejected)**
- User identified this as immediate usability issue
- Story 2.7 already open for refinement
- No benefit to deferring

**Option C: Rollback Story 2.7 (Not Applicable)**
- No failed implementation to rollback
- Current code is functional and correct
- Pure additive enhancement

### Feasibility Assessment

**Technical Feasibility**: ✅ HIGH
- Streamlit provides `st.multiselect` widget out-of-box
- DataFrame filtering is trivial: `df[df['event_type'].isin(selected_types)]`
- No external dependencies or API changes needed

**Effort**: ⚠️ LOW (2-4 hours)
- Code changes: ~20 lines
- Test additions: 4-5 new test cases
- Documentation updates: Minor

**Risk**: ✅ MINIMAL
- No impact on existing functionality
- Default behavior (show all) preserves current UX
- Isolated component, easy to rollback if needed

---

## 5. Specific Proposed Edits

### Edit 1: Update Story 2.7 Acceptance Criteria

**File**: `docs/stories/2.7.display-conversation-log.md`

**Section**: Acceptance Criteria

**Change From**:
```markdown
## Acceptance Criteria

1. The dashboard includes an expandable section implemented with `st.expander`
2. When expanded, this section displays the raw conversation history (e.g., thoughts, tool calls, reflections) from the loaded log file
3. The display is formatted for readability
```

**Change To**:
```markdown
## Acceptance Criteria

1. The dashboard includes an expandable section implemented with `st.expander`
2. When expanded, this section displays the raw conversation history (e.g., thoughts, tool calls, reflections) from the loaded log file
3. The display is formatted for readability
4. Users can filter displayed events by event type (CYCLE_START, LLM_INVOCATION, TOOL_CALL, CYCLE_END) using a multiselect control
```

---

### Edit 2: Add Task 7 to Story 2.7 Tasks

**File**: `docs/stories/2.7.display-conversation-log.md`

**Section**: Tasks / Subtasks

**Add After Task 6**:
```markdown
- [ ] **Task 7: Event Type Filtering** (AC: 4)
  - [ ] Add st.multiselect widget for event type selection
  - [ ] Default to all event types selected
  - [ ] Filter DataFrame based on user selection
  - [ ] Maintain chronological order after filtering
  - [ ] Update event counter to show filtered count
```

---

### Edit 3: Update Dev Notes with Filtering Implementation

**File**: `docs/stories/2.7.display-conversation-log.md`

**Section**: Dev Notes > Implementation Details

**Add Before Conversation Log Structure Section**:
```python
### Event Type Filtering

**Add filtering controls** (within expander, before event loop):

```python
# Event type filter
st.markdown("**Filter Event Types:**")
all_event_types = ['CYCLE_START', 'LLM_INVOCATION', 'TOOL_CALL', 'CYCLE_END']
selected_types = st.multiselect(
    "Select event types to display",
    options=all_event_types,
    default=all_event_types,
    key="event_type_filter"
)

# Filter DataFrame
if selected_types:
    filtered_df = df[df['event_type'].isin(selected_types)]
    st.caption(f"Showing {len(filtered_df)} of {len(df)} events")
else:
    filtered_df = pd.DataFrame()  # Empty if nothing selected
    st.warning("Select at least one event type to display")

# Process filtered events chronologically
for idx, row in filtered_df.iterrows():
    # ... existing event processing code ...
```

**Use Cases**:
- View only tool calls: Select TOOL_CALL only
- Skip verbose prompts: Deselect LLM_INVOCATION
- Focus on reflections: Select CYCLE_END only
- See cycle structure: Select CYCLE_START + CYCLE_END
```

---

### Edit 4: Add Filtering Test Cases

**File**: `docs/stories/2.7.display-conversation-log.md`

**Section**: Testing

**Add To Manual Testing Checklist**:
```markdown
8. **test_event_type_filtering**
   - Expand conversation log
   - Verify multiselect widget appears
   - Verify all event types selected by default
   - Deselect LLM_INVOCATION
   - Verify LLM_INVOCATION events hidden
   - Verify other events still visible
   - Verify filtered count displayed

9. **test_filter_combinations**
   - Select only TOOL_CALL events
   - Verify only tool calls shown
   - Select CYCLE_START + CYCLE_END
   - Verify cycle structure visible without details
   - Select no event types
   - Verify warning message displayed

10. **test_filter_preserves_order**
    - Select subset of event types
    - Verify remaining events maintain chronological order
    - Verify cycle numbers correct
    - Verify no events skipped within selected types
```

---

### Edit 5: Update Implementation Code

**File**: `pages/2_📊_results_dashboard.py`

**Section**: Conversation log expander (lines ~177-270)

**Change From**:
```python
with st.expander("💬 Raw Conversation Log", expanded=False):
    st.markdown("### Full Conversation History")
    st.caption("Complete message history and tool interactions from the experimental run")
    
    # Process events chronologically
    for idx, row in df.iterrows():
```

**Change To**:
```python
with st.expander("💬 Raw Conversation Log", expanded=False):
    st.markdown("### Full Conversation History")
    st.caption("Complete message history and tool interactions from the experimental run")
    
    # Event type filter
    st.markdown("**Filter Event Types:**")
    all_event_types = ['CYCLE_START', 'LLM_INVOCATION', 'TOOL_CALL', 'CYCLE_END']
    selected_types = st.multiselect(
        "Select event types to display",
        options=all_event_types,
        default=all_event_types,
        key="event_type_filter"
    )
    
    # Filter DataFrame
    if selected_types:
        filtered_df = df[df['event_type'].isin(selected_types)].copy()
        st.caption(f"📊 Showing {len(filtered_df)} of {len(df)} events")
    else:
        filtered_df = pd.DataFrame()
        st.warning("⚠️ Select at least one event type to display")
    
    st.markdown("---")
    
    # Process filtered events chronologically
    for idx, row in filtered_df.iterrows():
```

---

### Edit 6: Add Unit Tests for Filtering

**File**: `tests/unit/test_results_dashboard.py`

**Section**: Add new test methods to TestConversationLogDataProcessing class

**Add**:
```python
def test_event_type_filtering_single_type(self):
    """Test filtering to show only one event type"""
    df = pd.DataFrame([
        {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
        {'event_type': 'LLM_INVOCATION', 'cycle_number': 1, 'payload': {'prompt_messages': []}},
        {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {'tool_name': 'test'}},
        {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {}},
    ])
    
    selected_types = ['TOOL_CALL']
    filtered = df[df['event_type'].isin(selected_types)]
    
    assert len(filtered) == 1
    assert filtered.iloc[0]['event_type'] == 'TOOL_CALL'

def test_event_type_filtering_multiple_types(self):
    """Test filtering to show multiple event types"""
    df = pd.DataFrame([
        {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
        {'event_type': 'LLM_INVOCATION', 'cycle_number': 1, 'payload': {}},
        {'event_type': 'CYCLE_END', 'cycle_number': 1, 'payload': {}},
    ])
    
    selected_types = ['CYCLE_START', 'CYCLE_END']
    filtered = df[df['event_type'].isin(selected_types)]
    
    assert len(filtered) == 2
    assert 'CYCLE_START' in filtered['event_type'].values
    assert 'CYCLE_END' in filtered['event_type'].values
    assert 'LLM_INVOCATION' not in filtered['event_type'].values

def test_event_type_filtering_preserves_order(self):
    """Test that filtering maintains chronological order"""
    df = pd.DataFrame([
        {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:00'},
        {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:01'},
        {'event_type': 'LLM_INVOCATION', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:02'},
        {'event_type': 'TOOL_CALL', 'cycle_number': 1, 'payload': {}, 'timestamp': '2025-01-01 10:00:03'},
    ])
    
    selected_types = ['TOOL_CALL']
    filtered = df[df['event_type'].isin(selected_types)]
    
    assert len(filtered) == 2
    # Verify order preserved (first tool call before second)
    assert filtered.iloc[0]['timestamp'] == '2025-01-01 10:00:01'
    assert filtered.iloc[1]['timestamp'] == '2025-01-01 10:00:03'

def test_event_type_filtering_empty_selection(self):
    """Test behavior when no event types selected"""
    df = pd.DataFrame([
        {'event_type': 'CYCLE_START', 'cycle_number': 1, 'payload': {}},
    ])
    
    selected_types = []
    filtered = df[df['event_type'].isin(selected_types)]
    
    assert len(filtered) == 0
```

---

### Edit 7: Update Story Status

**File**: `docs/stories/2.7.display-conversation-log.md`

**Section**: Status (top of file)

**Change From**:
```markdown
**Status**: Ready for Review
```

**Change To**:
```markdown
**Status**: In Progress - Adding Event Filtering Enhancement
```

**Note**: Will return to "Ready for Review" after filtering implementation and all tests pass.

---

## 6. PRD MVP Impact

**No Impact**: This enhancement does not affect the MVP scope defined in the PRD. Story 2.7 remains within Epic 2's scope of providing "rich dashboard for visualizing and analyzing results."

**Value Addition**: Filtering capability significantly enhances the analysis tools pillar of Epic 2, making the conversation log more actionable for researchers.

---

## 7. High-Level Action Plan

### Immediate Next Steps

1. **User Approval**: Obtain explicit approval for this Sprint Change Proposal
2. **Assign to Developer**: Hand off to @dev agent with updated Story 2.7
3. **Implementation**: ~2-4 hours
   - Update Story 2.7 documentation (acceptance criteria, tasks, dev notes)
   - Add filtering widget to dashboard page
   - Implement DataFrame filtering logic
   - Add 4 unit tests for filtering behavior
   - Run full test suite (expect 41 tests total)
4. **Validation**: Developer marks Story 2.7 "Ready for Review" again
5. **QA Gate**: Proceed with normal QA validation using updated gate criteria

### Success Criteria

✅ Story 2.7 acceptance criteria updated with AC4 (filtering requirement)  
✅ Multiselect widget added to conversation log expander  
✅ Filtering logic correctly filters DataFrame by selected event types  
✅ Chronological order preserved after filtering  
✅ Filtered event count displayed to user  
✅ 4 new test cases added and passing  
✅ All 41 tests in test_results_dashboard.py pass  
✅ Manual testing confirms filtering works as expected  
✅ Story 2.7 status returned to "Ready for Review"  

### Timeline

- **Documentation Updates**: 30 minutes
- **Code Implementation**: 1-2 hours
- **Test Development**: 1 hour
- **Testing & Validation**: 30 minutes
- **Total**: 3-4 hours (single development session)

---

## 8. Agent Handoff Plan

### Roles Involved

**Scrum Master (Bob)**: 
- ✅ Completed: Change analysis and Sprint Change Proposal
- Next: Obtain user approval, hand off to Developer

**Developer (@dev / James)**:
- Implement all proposed edits (Edit 1-7 above)
- Run test suite and ensure all tests pass
- Mark Story 2.7 "Ready for Review" when complete

**QA Agent** (if applicable):
- Validate Story 2.7 against updated QA gate
- Test filtering functionality manually
- Sign off on story completion

### Handoff Message for Developer

```
@dev - Story 2.7 Enhancement Approved

**Context**: User testing revealed need for event type filtering in conversation log.

**Task**: Implement filtering enhancement per Sprint Change Proposal (see .ai/sprint-change-proposal-story-2.7-filtering.md)

**Specific Changes Required**:
1. Update docs/stories/2.7.display-conversation-log.md (Edits 1-4)
2. Update pages/2_📊_results_dashboard.py (Edit 5)
3. Update tests/unit/test_results_dashboard.py (Edit 6)
4. Update story status after completion (Edit 7)

**Expected Outcome**:
- st.multiselect widget for event type filtering
- Default: all types selected
- Filtered view maintains chronological order
- 4 new passing test cases
- Story 2.7 marked "Ready for Review"

**Estimated Effort**: 2-4 hours

Proceed when ready.
```

---

## 9. Risk Assessment

### Implementation Risks

**Technical Risk**: ✅ MINIMAL
- Streamlit multiselect is well-documented and stable
- DataFrame filtering is straightforward pandas operation
- No external API dependencies

**Testing Risk**: ✅ MINIMAL
- Filtering logic is deterministic and testable
- Existing tests remain valid
- New tests focused on simple filtering scenarios

**Integration Risk**: ✅ MINIMAL
- Changes isolated to single UI component
- No impact on data loading or metrics calculation
- Backward compatible (default shows all events)

### Mitigation Strategies

**If Filtering Performs Poorly**:
- Add caching for filtered DataFrames using st.cache_data
- Unlikely issue: typical run has 50-200 events total

**If Users Confused by Empty Display**:
- Warning message already specified when no types selected
- Default to "all selected" prevents confusion

**Rollback Plan**:
- Remove multiselect widget and filtering logic
- Revert to processing full DataFrame (current behavior)
- Takes <10 minutes to rollback if needed

---

## 10. Conclusion

### Summary

**Issue**: Conversation log display lacks filtering capability, making long logs difficult to analyze.

**Solution**: Add event type filtering using Streamlit multiselect widget.

**Impact**: Isolated enhancement to Story 2.7, no epic or project-level impact.

**Effort**: 2-4 hours implementation time.

**Value**: Significantly improves usability of primary analysis feature.

### Recommendation

**APPROVE this Sprint Change Proposal** and proceed with implementation.

This enhancement:
- ✅ Addresses real user need discovered during testing
- ✅ Has minimal scope and risk
- ✅ Adds significant value to Epic 2 deliverables
- ✅ Can be completed quickly within current sprint
- ✅ Maintains project momentum (no delays or blockers)

### Next Action Required

**User**: Review and approve this proposal, then authorize handoff to @dev agent for implementation.

---

**Document Version**: 1.0  
**Prepared By**: Bob (Scrum Master)  
**Date**: 2025-10-14 07:10 AM PST
