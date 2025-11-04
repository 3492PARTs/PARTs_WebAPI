# Complex Integration Testing Guide

This guide explains the complex integration tests in `test_complex_integration_scenarios.py` and how to create similar tests for other modules.

## Overview

Complex integration tests go beyond simple unit tests by testing:
- **Multiple components working together** (e.g., forms with conditional logic and flows)
- **End-to-end workflows** (e.g., user submits attendance → mentor approves → system records)
- **Data relationships across modules** (e.g., correlating responses across different form types)
- **Complex business logic** (e.g., cascading question conditions, permission hierarchies)

## Test Categories

### 1. Complex Form Workflows (`TestComplexFormWorkflows`)

These tests validate the form builder system with advanced features:

#### Test: `test_question_with_cascading_conditions`
**Purpose:** Validate that conditional questions can be chained together (A → B → C).

**What it tests:**
- Question A conditions Question B with a specific value
- Question B conditions Question C with another value
- All three questions are properly retrieved and parsed
- Conditional relationships are correctly maintained in both directions

**Key assertions:**
```python
# Question A has Question B as a conditional child
assert question_b.id in parsed_a['conditional_question_id_set']

# Question B has both parent (A) and child (C) relationships
assert parsed_b['conditional_on_questions'][0]['conditional_on'] == question_a.id
assert question_c.id in parsed_b['conditional_question_id_set']
```

**Real-world scenario:** 
A scouting form where showing "What type of robot?" depends on answering "yes" to "Do you have a robot?", and showing "Robot's name?" depends on selecting "competition" as the robot type.

#### Test: `test_form_response_validation_with_required_fields`
**Purpose:** Ensure the `save_question` utility properly handles all question properties.

**What it tests:**
- Creating questions with various field types
- Setting required fields, coordinates (x, y), dimensions (width, height)
- Handling special properties like icons and multipliers

**Key assertions:**
```python
assert created_question.required == 'y'
assert created_question.x == 10
assert created_question.icon == 'star'
```

**Real-world scenario:**
Team admin building a custom evaluation form with positioned questions for a visual layout.

#### Test: `test_flow_based_question_routing`
**Purpose:** Validate that flows can route users through different question paths.

**What it tests:**
- Creating multiple flows (student flow vs mentor flow)
- Assigning different questions to each flow
- Querying questions by flow membership

**Key assertions:**
```python
# Questions in flows should be excluded from "not in flow" query
questions_not_in_flow = get_questions(form_typ='onboard', not_in_flow=True)
assert len(questions_not_in_flow) == 0

# All questions should appear in general query
all_questions = get_questions(form_typ='onboard')
assert len(all_questions) == 3
```

**Real-world scenario:**
Onboarding process where students and mentors follow different paths through the form.

### 2. Complex TBA Integration (`TestComplexTBAIntegration`)

These tests validate The Blue Alliance API integration:

#### Test: `test_sync_season_with_multiple_events_and_matches`
**Purpose:** Test retrieving multiple events for a team in a season.

**What it tests:**
- Mocking TBA API responses for multiple events
- Parsing event data correctly
- Handling optional event filtering

**Mocking pattern:**
```python
@patch('tba.util.requests.get')
def test_sync_season_with_multiple_events_and_matches(self, mock_get):
    mock_response = Mock()
    mock_response.text = json.dumps([...])
    mock_get.return_value = mock_response
```

**Real-world scenario:**
Team 3492 viewing all their competition events for the 2024 season.

#### Test: `test_get_events_with_filtering`
**Purpose:** Test filtering out specific events from the retrieved list.

**What it tests:**
- Getting events with an ignore list
- Ensuring ignored events return minimal data
- Other events are fully retrieved

**Key assertions:**
```python
# Should return 3 events, but event2 should have minimal data
assert len(events) == 3
assert events[0]['event_cd'] == '2024event1'  # Full data
assert events[1] == {'event_cd': '2024event2'}  # Ignored event
```

**Real-world scenario:**
Team filtering out practice events to focus on official competitions.

#### Test: `test_match_retrieval_with_alliance_data`
**Purpose:** Validate parsing match data with alliance information.

**What it tests:**
- Retrieving matches for a team at an event
- Parsing alliance data (red vs blue)
- Identifying which alliance the team is on

**Real-world scenario:**
Scouting team viewing all their matches to plan scouting assignments.

### 3. Complex User Auth Workflows (`TestComplexUserAuthWorkflows`)

These tests validate authentication and permission systems:

#### Test: `test_multi_level_permission_hierarchy`
**Purpose:** Test that permission groups work correctly with inheritance.

**What it tests:**
- Creating groups with different permission levels (Viewer, Editor, Admin)
- Assigning users to groups
- Verifying permission checks at each level
- Understanding that `has_access` returns True if user has ANY of the listed permissions

**Permission hierarchy:**
- Viewer: view only
- Editor: view + edit
- Admin: view + edit + admin

**Key assertions:**
```python
# Viewer can only view
assert has_access(viewer.id, 'view_user_profile')
assert not has_access(viewer.id, 'admin_users')

# has_access with list returns True if user has AT LEAST ONE permission
assert has_access(editor.id, ['view_user_profile', 'admin_users'])  # True because editor has view
```

**Real-world scenario:**
Team member management with different access levels for students, mentors, and administrators.

#### Test: `test_access_response_with_complex_error_handling`
**Purpose:** Test the `access_response` wrapper with error scenarios.

**What it tests:**
- Function executes successfully when user has permission
- Function is not called when user lacks permission
- Exceptions are caught and error logs are created

**Real-world scenario:**
API endpoint that requires specific permissions and handles errors gracefully.

### 4. Complex Attendance Workflows (`TestComplexAttendanceWorkflows`)

These tests validate meeting and attendance tracking:

#### Test: `test_meeting_creation_and_queries`
**Purpose:** Test creating and querying meetings.

**What it tests:**
- Creating multiple meetings for a season
- Querying meetings by season
- Ordering meetings chronologically

**Real-world scenario:**
Team scheduling weekly meetings and workshops.

#### Test: `test_bulk_meeting_creation`
**Purpose:** Test bulk operations for efficiency.

**What it tests:**
- Creating 10 meetings using `bulk_create`
- Querying meetings by date range
- Verifying count matches expected

**Real-world scenario:**
Importing a semester schedule all at once.

### 5. Complex Data Aggregation (`TestComplexDataAggregation`)

These tests validate data analysis and correlation:

#### Test: `test_question_aggregate_setup`
**Purpose:** Test setting up aggregation relationships.

**What it tests:**
- Creating aggregate types (average, sum, etc.)
- Linking multiple questions to an aggregate
- Querying the relationship

**Real-world scenario:**
Creating a "Total Score" aggregate that sums multiple scoring questions.

#### Test: `test_cross_form_data_correlation`
**Purpose:** Test correlating data across different form types.

**What it tests:**
- Creating pre and post survey forms
- Recording responses to both
- Querying responses chronologically
- Comparing answers across forms

**Real-world scenario:**
Analyzing learning outcomes by comparing pre-survey and post-survey responses.

## Best Practices for Complex Tests

### 1. Use Real Models, Not Just Mocks
```python
# Good: Use actual Django models
question = Question.objects.create(
    question_typ=question_type,
    form_typ=form_type,
    question="Test question",
    active='y'
)

# Avoid: Over-mocking when testing integration
# mock_question = Mock(id=1, question="Test")  # Too simplified
```

### 2. Test Realistic Workflows
```python
# Good: Test a complete user journey
# 1. User creates a question
# 2. User adds conditional logic
# 3. User saves the question
# 4. System retrieves the question with conditions

# Avoid: Testing individual functions in isolation when testing integration
```

### 3. Use Descriptive Test Names
```python
# Good
def test_question_with_cascading_conditions(self):
    """Test complex scenario where question A conditions B which conditions C."""

# Avoid
def test_question(self):
    """Test question."""
```

### 4. Mock External Dependencies
```python
# Good: Mock external API calls
@patch('tba.util.requests.get')
def test_sync_season(self, mock_get):
    mock_get.return_value.text = json.dumps([...])

# Avoid: Making real API calls in tests
```

### 5. Assert on Business Logic, Not Implementation
```python
# Good: Test the outcome
assert len(parsed_a['conditional_question_id_set']) == 1
assert question_b.id in parsed_a['conditional_question_id_set']

# Avoid: Testing internal implementation details
# assert parsed_a._internal_cache is not None
```

### 6. Use Fixtures for Common Setup
```python
# Good: Use existing fixtures from conftest.py
def test_with_user(self, test_user):
    assert test_user.username == "testuser"

# Create fixtures for complex scenarios
@pytest.fixture
def form_with_conditions():
    # Setup complex form structure
    return form
```

### 7. Group Related Tests in Classes
```python
# Good
@pytest.mark.django_db
class TestComplexFormWorkflows:
    """Complex integration tests for form builder."""
    
    def test_cascading_conditions(self):
        pass
    
    def test_flow_routing(self):
        pass
```

## Running Complex Tests

```bash
# Run just the complex integration tests
poetry run pytest tests/test_complex_integration_scenarios.py -v

# Run a specific test class
poetry run pytest tests/test_complex_integration_scenarios.py::TestComplexFormWorkflows -v

# Run a specific test
poetry run pytest tests/test_complex_integration_scenarios.py::TestComplexFormWorkflows::test_question_with_cascading_conditions -v

# Run with verbose output and show print statements
poetry run pytest tests/test_complex_integration_scenarios.py -v -s

# Run without coverage for speed during development
poetry run pytest tests/test_complex_integration_scenarios.py --no-cov
```

## Adding New Complex Tests

When adding new complex integration tests:

1. **Identify the workflow:** What user journey or business process are you testing?
2. **Map the components:** What models, utilities, and views are involved?
3. **Create realistic data:** Use actual model instances that reflect real usage
4. **Test happy path first:** Ensure the primary workflow works
5. **Add edge cases:** Test boundary conditions, empty states, and error scenarios
6. **Mock external dependencies:** Don't call real APIs or send real emails
7. **Document the test:** Explain what real-world scenario it represents

Example template:
```python
def test_my_complex_workflow(self):
    """
    Test [describe the business workflow].
    
    This test validates:
    - [Key aspect 1]
    - [Key aspect 2]
    - [Key aspect 3]
    
    Real-world scenario: [Describe when this happens]
    """
    # Setup: Create necessary data
    
    # Test: Execute the workflow
    
    # Verify: Check the outcomes
    assert expected_outcome
```

## Coverage Impact

These complex integration tests significantly improve coverage in:
- `form/util.py`: Testing question retrieval and parsing logic
- `tba/util.py`: Testing TBA API integration
- `general/security.py`: Testing permission and access control
- `attendance/models.py`: Testing meeting management
- Form models: Testing relationships between questions, flows, and aggregates

The tests focus on **high-value code paths** that are critical to the application's functionality.

## Troubleshooting

### Test fails with "TypeError: Model() got unexpected keyword arguments"
**Cause:** Using incorrect field names for the model.

**Solution:** Check the actual model definition in `src/[app]/models.py`:
```bash
cd src && grep -A 10 "class MyModel" myapp/models.py
```

### Test fails with import errors
**Cause:** Trying to import a model or function that doesn't exist.

**Solution:** Verify the import path:
```bash
cd src && grep -r "class MyClass" .
```

### Mock not being used
**Cause:** Patching the wrong path or not using the mock decorator correctly.

**Solution:** Patch where the function is used, not where it's defined:
```python
# If views.py imports tba.util.get_events
# Patch in views, not util
@patch('myapp.views.get_events')  # Good
# @patch('tba.util.get_events')   # Might not work
```

## Contributing

When contributing complex tests:
1. Follow the existing patterns in `test_complex_integration_scenarios.py`
2. Add documentation explaining the business workflow
3. Ensure tests pass independently: `pytest tests/test_complex_integration_scenarios.py::TestClass::test_method`
4. Don't break existing tests: `poetry run pytest --no-cov -x`
5. Update this guide if you introduce new testing patterns

## Questions?

- Review existing complex tests for patterns
- Check `TESTING.md` for general testing guidelines
- Reach out to team maintainers for help
