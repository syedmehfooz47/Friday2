# -*- coding: utf-8 -*-
"""
Test script for Google Calendar integration
Run this to verify calendar functionality
"""

from Backend.calendar_handler import CalendarHandler
from datetime import datetime, timedelta
import json

def test_calendar_integration():
    """Test all calendar operations"""
    
    print("=" * 60)
    print("Google Calendar Integration Test")
    print("=" * 60)
    
    # Initialize calendar handler
    print("\n1. Initializing Calendar Handler...")
    calendar = CalendarHandler()
    
    if not calendar.service:
        print("❌ Failed to initialize calendar service")
        print("Please ensure:")
        print("  - credentials.json is in the project root")
        print("  - You've enabled Google Calendar API")
        print("  - Required scopes are added")
        return
    
    print("✅ Calendar service initialized successfully")
    
    # Test 1: List upcoming events
    print("\n2. Testing: List Upcoming Events")
    result = calendar.list_events(max_results=5)
    if result['status'] == 'success':
        print(f"✅ Found {result['count']} events")
        for event in result['events']:
            print(f"   - {event['summary']} ({event['start']})")
    else:
        print(f"❌ Error: {result['message']}")
    
    # Test 2: Create a test event
    print("\n3. Testing: Create Calendar Event")
    start_time = (datetime.utcnow() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    result = calendar.create_event(
        summary="Test Event - Friday AI Assistant",
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        description="This is a test event created by Friday AI Assistant",
        location="Online"
    )
    
    if result['status'] == 'success':
        print(f"✅ Event created: {result['event_id']}")
        event_id = result['event_id']
        
        # Test 3: Get event details
        print("\n4. Testing: Get Event Details")
        result = calendar.get_event(event_id=event_id)
        if result['status'] == 'success':
            print(f"✅ Retrieved event: {result['event']['summary']}")
            print(f"   Location: {result['event']['location']}")
            print(f"   Start: {result['event']['start']}")
        else:
            print(f"❌ Error: {result['message']}")
        
        # Test 4: Update event
        print("\n5. Testing: Update Event")
        new_start = start_time + timedelta(hours=1)
        new_end = new_start + timedelta(hours=1)
        
        result = calendar.update_event(
            event_id=event_id,
            summary="Updated Test Event - Friday AI",
            start_time=new_start.isoformat(),
            end_time=new_end.isoformat(),
            location="Conference Room A"
        )
        
        if result['status'] == 'success':
            print(f"✅ Event updated successfully")
        else:
            print(f"❌ Error: {result['message']}")
        
        # Test 5: Search events
        print("\n6. Testing: Search Events")
        result = calendar.search_events(query="Friday", max_results=5)
        if result['status'] == 'success':
            print(f"✅ Found {result['count']} events matching 'Friday'")
        else:
            print(f"❌ Error: {result['message']}")
        
        # Test 6: Delete event
        print("\n7. Testing: Delete Event")
        result = calendar.delete_event(event_id=event_id)
        if result['status'] == 'success':
            print(f"✅ Event deleted successfully")
        else:
            print(f"❌ Error: {result['message']}")
    else:
        print(f"❌ Failed to create event: {result['message']}")
    
    print("\n" + "=" * 60)
    print("Calendar Integration Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_calendar_integration()
