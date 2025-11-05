# Moodboard Feature Implementation

## Overview
Added a moodboard feature that allows participants to collect reference images before starting their design ideation activities. This provides a way to establish visual context and inspiration for the study.

## User Flow
1. **Login** (index.html) → User enters email
2. **Moodboard** (moodboard.html) → User uploads reference images ⭐ NEW
3. **Model Selection** (select-model.html) → User selects LLM model
4. **Chat** (chat.html) → User conducts ideation session
5. **Gallery** (gallery.html) → User views generated images

## Features

### Drag & Drop Interface
- Drag images directly from desktop into the upload area
- Click to browse and select multiple images
- Visual feedback with drag-over states
- Real-time image preview in a responsive grid layout

### File Management
- Support for PNG, JPG, JPEG, GIF, WebP formats
- Maximum file size: 10MB per image
- Upload progress indicator
- Individual image deletion with confirmation
- "Clear All" option to remove all images
- Images persist across sessions (tied to user account)

### User Experience
- Clean, modern UI consistent with existing app design
- Hover effects on image cards
- Delete button appears on hover
- Image count display
- Responsive grid layout (2-5 columns depending on screen size)
- Loading states and error handling

## Technical Implementation

### Backend Changes

#### 1. Database Model (`backend/models.py`)
```python
class MoodboardImage(Base):
    """Stores reference images uploaded by users"""
    - user_id: Links to User
    - image_path: File storage location
    - original_filename: Original name of uploaded file
    - created_at: Timestamp
```

#### 2. API Routes (`backend/routes/moodboard.py`)
- `POST /api/moodboard/upload` - Upload image with validation
- `GET /api/moodboard/<user_id>` - Retrieve all user's images
- `GET /api/moodboard/image/<image_id>` - Serve image file
- `DELETE /api/moodboard/image/<image_id>` - Delete single image
- `DELETE /api/moodboard/clear/<user_id>` - Delete all user images

#### 3. File Storage
- Images stored in: `data/moodboard/user_<id>/`
- Unique filename generation using UUID to prevent conflicts
- Organized by user ID for easy management

#### 4. Blueprint Registration (`backend/app.py`)
- Registered `moodboard_bp` with Flask application

### Frontend Changes

#### 1. New Page (`frontend/moodboard.html`)
- Drag-and-drop upload zone
- Image grid display
- Upload progress tracking
- Delete functionality
- Navigation to model selection

#### 2. API Client Updates (`frontend/js/api.js`)
Added methods:
- `uploadMoodboardImage(userId, file)`
- `getMoodboard(userId)`
- `deleteMoodboardImage(imageId)`
- `clearMoodboard(userId)`

#### 3. Navigation Flow (`frontend/index.html`)
- Updated to redirect to `moodboard.html` after login instead of `select-model.html`

## File Structure
```
data/
└── moodboard/
    └── user_<id>/
        ├── <uuid>.png
        ├── <uuid>.jpg
        └── ...
```

## Validation & Security

### File Validation
- File type checking (only images allowed)
- File size limit (10MB maximum)
- Secure filename generation
- User authentication required

### Error Handling
- Invalid file type alerts
- File size exceeded warnings
- Upload failure feedback
- Network error handling

## Database Migration
The new `MoodboardImage` model will be automatically created when the application starts. The database initialization in `backend/database.py` handles creating new tables.

## Testing Checklist

- [ ] Upload single image
- [ ] Upload multiple images at once
- [ ] Drag and drop from desktop
- [ ] Delete individual image
- [ ] Clear all images
- [ ] Navigate to model selection
- [ ] Return to moodboard (images persist)
- [ ] Test file type validation
- [ ] Test file size validation
- [ ] Test on mobile/responsive views

## Future Enhancements (Optional)

1. **Image Annotations**: Allow users to add notes to images
2. **Image Ordering**: Drag to reorder images
3. **Collections**: Group images into categories
4. **Export Moodboard**: Download moodboard as PDF
5. **Admin View**: See all user moodboards in admin panel
6. **Image Compression**: Auto-compress large images
7. **Reference in Chat**: Allow users to reference moodboard images during chat

## Notes

- Moodboard is optional - users can skip directly to model selection if desired
- Images are stored permanently unless user deletes them
- Each user has their own moodboard tied to their account
- Images do not expire and can be accessed across sessions
- The moodboard serves as visual inspiration but is not directly integrated into the LLM prompts (this could be a future enhancement)
