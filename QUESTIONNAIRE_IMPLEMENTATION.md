# Questionnaire Implementation

This document describes the questionnaire functionality implemented in the `questionnaire` branch.

## Overview

The questionnaire system enables researchers to collect participant feedback at two key points in the user study:
1. **Pre-Activity Questionnaire**: Completed once immediately after login, before the moodboard setup
2. **Post-Activity Questionnaire**: Completed after each of the three model testing activities

## User Flow

```
Login → Pre-Activity Questionnaire → Moodboard → Select Model → Chat & Generate → Image Gallery → Post-Activity Questionnaire → Select Model → Chat & Generate → Image Gallery → Post-Activity Questionnaire → Select Model → Chat & Generate → Image Gallery → Post-Activity Questionnaire → Study Complete
```

### Flow Details

1. **Login** (`index.html`) - User authenticates with email
2. **Pre-Activity Questionnaire** (`pre-activity-questionnaire.html`) - One-time demographic and background questions
3. **Moodboard** (`moodboard.html`) - User uploads reference images (optional)
4. **Model Selection** (`select-model.html`) - User manually selects next model to test
5. **Ideation & Generate** (`ideation.html`) - User interacts with AI model (or uses notes in unaided mode) to generate prompts
6. **Image Gallery** (`gallery.html`) - User views generated images
7. **Post-Activity Questionnaire** (`post-activity-questionnaire.html`) - Feedback about the specific model just tested
8. Steps 4-7 repeat for 3 different models (determined by randomized order assigned to participant)
9. **Study Complete** (`study-complete.html`) - Thank you page with option to start new session

## Database Schema

### QuestionnaireResponse Model

```python
class QuestionnaireResponse(Base):
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key → users.id)
    session_id: Integer (Foreign Key → sessions.id, nullable for pre-activity)
    questionnaire_type: String ('pre-activity' or 'post-activity')
    responses: Text (JSON string of question-answer pairs)
    created_at: DateTime
```

## API Endpoints

### Submit Questionnaire
**POST** `/api/questionnaire/submit`

Request body:
```json
{
  "user_id": 1,
  "session_id": 5,  // Optional for pre-activity
  "questionnaire_type": "pre-activity",  // or "post-activity"
  "responses": {
    "question_1": "answer_1",
    "question_2": "answer_2"
  }
}
```

Response:
```json
{
  "success": true,
  "response_id": 1,
  "message": "Questionnaire submitted successfully"
}
```

### Get User Questionnaires
**GET** `/api/questionnaire/user/{user_id}?questionnaire_type=pre-activity&session_id=5`

Response:
```json
{
  "success": true,
  "responses": [...]
}
```

### Check Questionnaire Completion
**POST** `/api/questionnaire/check`

Request body:
```json
{
  "user_id": 1,
  "questionnaire_type": "pre-activity",
  "session_id": 5  // Optional
}
```

Response:
```json
{
  "completed": true,
  "response_id": 1
}
```

## Frontend Components

### Storage Utilities (storage.js)

New methods added:
- `setPreActivityCompleted(completed)` - Track pre-activity completion
- `getPreActivityCompleted()` - Check if pre-activity completed
- `getActivityCount()` - Get number of models tested (0-3)
- `incrementActivityCount()` - Increment after each post-activity questionnaire
- `resetActivityTracking()` - Reset for new study session

### API Client (api.js)

New methods added:
- `submitQuestionnaire(payload)` - Submit questionnaire responses
- `getQuestionnaireResponses(userId, type, sessionId)` - Retrieve responses
- `checkQuestionnaireCompletion(userId, type, sessionId)` - Check completion status

## Questionnaire Content

### Pre-Activity Questionnaire (Boilerplate)

1. **Age Range** (Required, Radio)
   - 18-24
   - 25-34
   - 35-44
   - 45+

2. **AI Tool Experience** (Required, Radio)
   - No experience
   - Beginner
   - Intermediate
   - Advanced

3. **Design Background** (Required, Radio)
   - Professional designer
   - Design student
   - Hobbyist/Enthusiast
   - No design background

4. **Expectations** (Optional, Text area)
   - Open-ended response

### Post-Activity Questionnaire (Boilerplate)

1. **Satisfaction** (Required, 5-point Likert scale)
   - 1 (Very dissatisfied) to 5 (Very satisfied)

2. **Ease of Use** (Required, 5-point Likert scale)
   - 1 (Very difficult) to 5 (Very easy)

3. **Usefulness** (Required, 5-point Likert scale)
   - 1 (Not useful) to 5 (Very useful)

4. **Would Reuse** (Required, Radio)
   - Definitely yes
   - Probably yes
   - Maybe
   - Probably not
   - Definitely not

5. **Additional Feedback** (Optional, Text area)
   - Open-ended response

## Progress Tracking

The progress indicator shows participants where they are in the study:

- **Pre-Activity**: 1 of 4 questionnaires (25%)
- **Post-Activity 1**: 2 of 4 questionnaires (50%)
- **Post-Activity 2**: 3 of 4 questionnaires (75%)
- **Post-Activity 3**: 4 of 4 questionnaires (100%)

## Key Features

### Duplicate Prevention
- Pre-activity questionnaire checks if already completed and redirects to model selection
- Post-activity questionnaire checks if completed for the current session

### Activity Count Tracking
- Automatically increments after each post-activity questionnaire
- Used to determine when study is complete (3 activities)
- Updates progress bar and button text accordingly

### Manual Model Selection
- Participants manually select each model (no automatic progression)
- Supports randomized model order assignment by researchers
- Helps control for learning effects

### Study Completion
- After 3rd post-activity questionnaire, redirects to completion page
- Completion page offers:
  - Start new study session (resets tracking, keeps user logged in)
  - Logout

## Customization

To update questionnaire content, edit:
- `frontend/pre-activity-questionnaire.html` - Pre-activity questions
- `frontend/post-activity-questionnaire.html` - Post-activity questions

The form structure uses standard HTML inputs, making it easy to:
- Add/remove questions
- Change question types (radio, checkbox, textarea, etc.)
- Modify response options
- Update styling

## Testing Checklist

- [ ] User can complete pre-activity questionnaire
- [ ] Pre-activity redirects to model selection after submission
- [ ] Cannot submit pre-activity twice
- [ ] User can complete post-activity questionnaire after each session
- [ ] Post-activity questionnaire tracks correct session
- [ ] Activity count increments correctly (1, 2, 3)
- [ ] Progress indicator updates correctly
- [ ] Study completes after 3rd post-activity questionnaire
- [ ] Can start new study session from completion page
- [ ] Data persists correctly in database
- [ ] All required fields are validated
- [ ] Optional fields work correctly

## Future Enhancements

Potential improvements:
- Export questionnaire data to CSV/Excel
- Admin panel to view aggregated responses
- Configurable questionnaires (JSON-based definitions)
- Conditional questions based on previous answers
- Response validation (e.g., min/max text length)
- Time tracking for questionnaire completion
- Multi-language support
