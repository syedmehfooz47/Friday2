# Google Calendar Integration for Friday AI Assistant

## Overview

Friday AI Assistant now includes full Google Calendar integration, allowing you to manage your calendar events through voice commands and the web UI. The integration uses the same OAuth2 authentication system as Gmail for a seamless experience.

## Features

✅ **View Events** - List upcoming calendar events and meetings  
✅ **Create Events** - Schedule new meetings and appointments  
✅ **Update Events** - Modify existing event details, time, and location  
✅ **Delete Events** - Remove cancelled meetings  
✅ **Search Events** - Find events by keyword  
✅ **Event Details** - Get comprehensive information about specific events  

## Setup Instructions

### 1. Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project (the same one used for Gmail)
3. Navigate to **APIs & Services** > **Library**
4. Search for "Google Calendar API"
5. Click **Enable**

### 2. Update OAuth Scopes

The calendar integration requires additional OAuth scopes. You need to add these scopes to your OAuth consent screen:

**Required Scopes:**

```
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/gmail.modify
```

#### How to Add Scopes:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** > **OAuth consent screen**
3. Click **Edit App**
4. Scroll to **Scopes** section and click **Add or Remove Scopes**
5. In the filter box, search for "calendar"
6. Check the following scopes:
   - `https://www.googleapis.com/auth/calendar` (See, edit, share, and permanently delete all calendars)
   - `https://www.googleapis.com/auth/calendar.events` (View and edit events on all calendars)
7. Click **Update** at the bottom
8. Click **Save and Continue**
9. Complete the remaining steps

**Important:** After adding new scopes, you need to delete the existing `Database/gmail_token.json` file and re-authenticate. The system will ask you to authorize the new permissions.

### 3. Re-authenticate

```bash
# Delete the existing token
rm Database/gmail_token.json

# Or on Windows
del Database\gmail_token.json

# Run Friday - it will prompt for re-authentication
python main.py
```

When the OAuth consent screen appears, make sure to:
- Review the permissions carefully
- Accept all requested permissions including Calendar access
- The token will be saved for future use

## Usage Examples

### Voice Commands

Once Friday is running, you can use these voice commands:

**View Calendar:**
- "Show my calendar events"
- "What meetings do I have today?"
- "List my upcoming appointments"
- "Check my schedule for tomorrow"

**Create Events:**
- "Schedule a meeting tomorrow at 2 PM"
- "Create a calendar event for next Monday at 10 AM"
- "Add a team meeting on Friday at 3 PM for 1 hour"
- "Schedule a dentist appointment next week"

**Search Events:**
- "Find my meeting with John"
- "Search for project review meetings"
- "Show me events about product launch"

**Update Events:**
- "Reschedule my 2 PM meeting to 3 PM"
- "Change the location of tomorrow's meeting"
- "Update the team meeting details"

**Delete Events:**
- "Cancel my meeting at 2 PM"
- "Delete the dentist appointment"
- "Remove tomorrow's team sync"

### Programmatic Usage

You can also use the calendar handler directly in your code:

```python
from Backend.calendar_handler import CalendarHandler
from datetime import datetime, timedelta

# Initialize
calendar = CalendarHandler()

# List upcoming events
result = calendar.list_events(max_results=10)
print(result['events'])

# Create an event
start_time = datetime.utcnow() + timedelta(days=1)
end_time = start_time + timedelta(hours=1)

result = calendar.create_event(
    summary="Team Meeting",
    start_time=start_time.isoformat(),
    end_time=end_time.isoformat(),
    description="Weekly team sync",
    location="Conference Room A",
    attendees=["colleague@example.com"]
)

# Update an event
result = calendar.update_event(
    event_id="event_id_here",
    summary="Updated Meeting Title",
    location="New Location"
)

# Delete an event
result = calendar.delete_event(event_id="event_id_here")

# Search events
result = calendar.search_events(query="team meeting")
```

## Available Tools

Friday's brain now includes these calendar tools:

| Tool Name | Description |
|-----------|-------------|
| `calendar_list_events` | List upcoming calendar events |
| `calendar_create_event` | Create a new calendar event/meeting |
| `calendar_update_event` | Update an existing event |
| `calendar_delete_event` | Delete a calendar event |
| `calendar_search_events` | Search events by keyword |
| `calendar_get_event` | Get detailed info about a specific event |

## Testing

Run the test script to verify your calendar integration:

```bash
python test_calendar.py
```

The test will:
1. Initialize the calendar service
2. List your upcoming events
3. Create a test event
4. Retrieve event details
5. Update the event
6. Search for events
7. Delete the test event

## Troubleshooting

### "Calendar service not initialized" error

**Solution:** 
- Ensure `credentials.json` exists in the project root
- Verify Google Calendar API is enabled
- Delete `Database/gmail_token.json` and re-authenticate

### "Insufficient permissions" error

**Solution:**
- Add the required calendar scopes to your OAuth consent screen (see Setup Instructions)
- Delete `Database/gmail_token.json`
- Re-run Friday to re-authenticate with new permissions

### Authentication browser doesn't open

**Solution:**
- Check if port 0 (auto-select) is available
- Look for the authorization URL in the console
- Copy and paste it into your browser manually

### "Invalid time format" error

**Solution:**
- Ensure times are in ISO format: `YYYY-MM-DDTHH:MM:SS`
- Example: `2026-01-15T14:30:00` for Jan 15, 2026 at 2:30 PM
- Or use Python: `datetime.utcnow().isoformat()`

## Privacy & Security

- Calendar data is accessed using OAuth2 - your password is never stored
- Access tokens are encrypted and stored locally in `Database/gmail_token.json`
- Friday only accesses your calendar when you explicitly request it
- You can revoke access anytime from [Google Account Settings](https://myaccount.google.com/permissions)

## Integration Architecture

The calendar integration follows the same pattern as other Friday tools:

1. **calendar_handler.py** - Core calendar operations using Google Calendar API
2. **brain.py** - Tool definitions and routing
3. **main.py** - WebSocket endpoints for UI integration
4. **Shared OAuth** - Uses the same token as Gmail for unified authentication

## What's Next?

Future enhancements planned:
- 🔔 Calendar event reminders
- 📧 Automatic email invites when creating events
- 📊 Calendar analytics and time management insights
- 🔄 Sync with multiple calendars
- 🤝 Smart scheduling suggestions based on availability
- 📱 Integration with phone calendar sync

## Support

If you encounter any issues:
1. Check the logs in `Database/TerminalLogs/`
2. Review the Google Calendar API documentation
3. Ensure your OAuth credentials are properly configured
4. Verify all required scopes are added

---

**Note:** The calendar integration is now fully functional and ready to use! Just make sure to add the required OAuth scopes and re-authenticate.
