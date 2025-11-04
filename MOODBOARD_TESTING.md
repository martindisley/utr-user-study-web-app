# Moodboard Testing Guide

## Quick Start Testing

### 1. Start the Backend
```bash
# Make sure you have the virtual environment activated
source venv/bin/activate

# Start the server
./run.sh
# OR for production mode:
# ./start_optimized.sh
```

### 2. Access the Application
Open your browser and navigate to:
- Local: `http://localhost:5000`
- Or your Netlify URL if deployed

### 3. Login
- Enter any email address (e.g., `test@example.com`)
- Click "Sign In"
- You should be redirected to the moodboard page

## Testing the Moodboard Feature

### Test Case 1: Upload via Drag & Drop
1. Open a file explorer window with some image files
2. Drag an image from the file explorer onto the upload area
3. ✅ **Expected**: Image should upload and appear in the grid below
4. ✅ **Expected**: Image count should update

### Test Case 2: Upload via File Browser
1. Click the "Drop images here" area
2. Select one or more image files from the dialog
3. ✅ **Expected**: Images upload with progress indicator
4. ✅ **Expected**: All selected images appear in the grid

### Test Case 3: Multiple Format Support
Test with different file types:
- ✅ PNG file
- ✅ JPG/JPEG file
- ✅ GIF file
- ✅ WebP file
- ❌ PDF or other non-image files (should show error)

### Test Case 4: File Size Validation
1. Try to upload an image larger than 10MB
2. ✅ **Expected**: Error alert saying file is too large

### Test Case 5: Delete Individual Image
1. Upload several images
2. Hover over an image
3. Click the × button that appears in the top-right corner
4. Confirm the deletion
5. ✅ **Expected**: Image is removed from the grid
6. ✅ **Expected**: Image count updates

### Test Case 6: Clear All Images
1. Upload multiple images
2. Click "Clear All" button at the top of the grid
3. Confirm the action
4. ✅ **Expected**: All images are removed
5. ✅ **Expected**: Grid section hides

### Test Case 7: Persistence
1. Upload some images
2. Click "Continue to Model Selection"
3. On the model selection page, click browser back button
4. ✅ **Expected**: Your uploaded images are still there

### Test Case 8: Navigation Flow
1. Upload images (or skip)
2. Click "Continue to Model Selection"
3. ✅ **Expected**: Redirected to model selection page
4. ✅ **Expected**: Normal flow continues (select model → chat)

### Test Case 9: Logout and Return
1. Upload images
2. Click "Use different email"
3. Confirm logout
4. Login with the SAME email
5. ✅ **Expected**: Your previous moodboard images are loaded

### Test Case 10: Multiple Users
1. Login with email A, upload images
2. Logout
3. Login with email B, upload different images
4. ✅ **Expected**: Each user sees only their own images

## Responsive Design Testing

Test on different screen sizes:
- 📱 Mobile (< 640px): 2 columns
- 📱 Tablet (640-1024px): 3-4 columns
- 💻 Desktop (> 1024px): 5 columns

## Backend API Testing

### Using curl:

```bash
# 1. Login and get user ID
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
# Note the user_id from response

# 2. Upload an image
curl -X POST http://localhost:5000/api/moodboard/upload \
  -F "user_id=1" \
  -F "file=@/path/to/image.png"

# 3. Get user's moodboard
curl http://localhost:5000/api/moodboard/1

# 4. Delete an image (use image_id from previous response)
curl -X DELETE http://localhost:5000/api/moodboard/image/1

# 5. Clear all images
curl -X DELETE http://localhost:5000/api/moodboard/clear/1
```

## Database Verification

```bash
# Check the database
sqlite3 data/study.db

# List all tables (should include moodboard_images)
.tables

# View moodboard images
SELECT * FROM moodboard_images;

# Count images per user
SELECT user_id, COUNT(*) as image_count 
FROM moodboard_images 
GROUP BY user_id;

# Exit
.quit
```

## File System Verification

```bash
# Check uploaded images
ls -la data/moodboard/

# Check a specific user's images
ls -la data/moodboard/user_1/

# Check file sizes
du -h data/moodboard/user_*/
```

## Common Issues & Solutions

### Issue: Images not uploading
- Check backend logs: `tail -f logs/error.log`
- Verify the data/moodboard directory exists
- Check file permissions

### Issue: CORS errors
- Ensure backend is running
- Check CORS_ORIGINS in backend/config.py
- Verify API_BASE_URL in frontend env.js

### Issue: Images not displaying
- Check browser console for errors
- Verify image_id in the database matches the request
- Check image file exists on disk

### Issue: Database errors
- Delete data/study.db and restart (WARNING: loses all data)
- Check backend logs for migration issues

## Success Criteria

✅ All test cases pass
✅ No console errors in browser
✅ No errors in backend logs
✅ Images persist across sessions
✅ Navigation flow works correctly
✅ Responsive design works on all screen sizes

## Next Steps After Testing

1. If everything works: Deploy to production
2. If issues found: Check logs and fix bugs
3. Conduct user testing with actual participants
4. Gather feedback on the moodboard UX
5. Consider adding optional enhancements from MOODBOARD_FEATURE.md
