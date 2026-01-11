# -*- coding: utf-8 -*-
"""
Google Calendar Handler - Calendar management integration
Supports viewing, creating, updating, and deleting calendar events
Uses Gmail API OAuth2 authentication (same token system)
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .logger import Logger

# Google Calendar API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',  # Full access to calendars
    'https://www.googleapis.com/auth/calendar.events'  # Access to events
]

# Token file location (shared with Gmail)
TOKEN_FILE = Path(__file__).parent.parent / "Database" / "gmail_token.json"
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"


class CalendarHandler:
    """Advanced calendar management handler using Google Calendar API"""
    
    def __init__(self):
        self.service = None
        self.user_email = None
        self._initialize_calendar_service()
        Logger.log("CalendarHandler initialized", "CALENDAR")
    
    def _initialize_calendar_service(self) -> bool:
        """
        Initialize Google Calendar API service with OAuth2 authentication
        Uses same credentials as Gmail for unified authentication
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure Database directory exists
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            creds = None
            
            # Load existing token if available
            if TOKEN_FILE.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
                    Logger.log("Loaded existing Google credentials", "CALENDAR")
                except Exception as e:
                    Logger.log(f"Failed to load existing credentials: {e}", "ERROR")
                    creds = None
            
            # If no valid credentials, perform OAuth2 flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        Logger.log("Refreshed Google credentials", "CALENDAR")
                    except Exception as e:
                        Logger.log(f"Failed to refresh credentials: {e}", "ERROR")
                        creds = None
                
                if not creds:
                    if not CREDENTIALS_FILE.exists():
                        Logger.log(f"credentials.json not found at {CREDENTIALS_FILE}", "ERROR")
                        Logger.log("Please download credentials.json from Google Cloud Console", "WARNING")
                        Logger.log("1. Go to https://console.cloud.google.com", "INFO")
                        Logger.log("2. Create OAuth 2.0 Client ID (Desktop Application)", "INFO")
                        Logger.log("3. Download JSON and save as credentials.json in project root", "INFO")
                        return False
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(CREDENTIALS_FILE), SCOPES)
                        creds = flow.run_local_server(port=0)
                        Logger.log("OAuth2 authentication successful", "CALENDAR")
                    except Exception as e:
                        Logger.log(f"OAuth2 authentication failed: {e}", "ERROR")
                        return False
                
                # Save credentials for next time
                try:
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    Logger.log("Google credentials saved", "CALENDAR")
                except Exception as e:
                    Logger.log(f"Failed to save credentials: {e}", "ERROR")
            
            # Build Calendar service
            try:
                self.service = build('calendar', 'v3', credentials=creds)
                
                # Get user email from calendar settings
                try:
                    settings = self.service.settings().get(setting='timezone').execute()
                    Logger.log(f"Calendar service initialized", "CALENDAR")
                except:
                    pass
                
                return True
            except Exception as e:
                Logger.log(f"Failed to build Calendar service: {e}", "ERROR")
                return False
        
        except Exception as e:
            Logger.log(f"Error initializing Calendar service: {e}", "ERROR")
            return False
    
    def list_events(self, max_results: int = 10, time_min: Optional[str] = None,
                    time_max: Optional[str] = None, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        List upcoming calendar events
        
        Args:
            max_results: Maximum number of events to return
            time_min: Start time (ISO format), defaults to now
            time_max: End time (ISO format), optional
            calendar_id: Calendar to query (default: 'primary')
            
        Returns:
            Dictionary with status and events list
        """
        if not self.service:
            return {"status": "error", "message": "Calendar service not initialized"}
        
        try:
            Logger.log(f"Fetching {max_results} events from calendar", "CALENDAR")
            
            # Default to now if no time_min specified
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            # Build parameters
            params = {
                'calendarId': calendar_id,
                'timeMin': time_min,
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if time_max:
                params['timeMax'] = time_max
            
            # Call the Calendar API
            events_result = self.service.events().list(**params).execute()
            events = events_result.get('items', [])
            
            Logger.log(f"Found {len(events)} events", "CALENDAR")
            
            # Format events for easy reading
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': [a.get('email') for a in event.get('attendees', [])],
                    'status': event.get('status', 'confirmed'),
                    'html_link': event.get('htmlLink', '')
                })
            
            Logger.log_chat("TOOL", f"📅 Retrieved {len(formatted_events)} calendar events")
            
            return {
                "status": "success",
                "count": len(formatted_events),
                "events": formatted_events,
                "message": f"Retrieved {len(formatted_events)} events"
            }
        
        except HttpError as e:
            error_msg = f"Calendar API error: {e}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Failed to list events: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def create_event(self, summary: str, start_time: str, end_time: str,
                     description: Optional[str] = None, location: Optional[str] = None,
                     attendees: Optional[List[str]] = None, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Create a new calendar event
        
        Args:
            summary: Event title
            start_time: Start time (ISO format: YYYY-MM-DDTHH:MM:SS)
            end_time: End time (ISO format: YYYY-MM-DDTHH:MM:SS)
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee email addresses (optional)
            calendar_id: Calendar to create event in (default: 'primary')
            
        Returns:
            Dictionary with status and event details
        """
        if not self.service:
            return {"status": "error", "message": "Calendar service not initialized"}
        
        if not summary or not start_time or not end_time:
            return {"status": "error", "message": "Missing required fields: summary, start_time, end_time"}
        
        try:
            Logger.log(f"Creating calendar event: {summary}", "CALENDAR")
            
            # Build event object
            event = {
                'summary': summary,
                'start': {'dateTime': start_time, 'timeZone': 'UTC'},
                'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            Logger.log(f"Event created with ID: {created_event['id']}", "CALENDAR")
            Logger.log_chat("TOOL", f"✅ Calendar event '{summary}' created")
            
            return {
                "status": "success",
                "message": f"Event '{summary}' created successfully",
                "event_id": created_event['id'],
                "event_link": created_event.get('htmlLink', ''),
                "summary": summary,
                "start": start_time,
                "end": end_time
            }
        
        except HttpError as e:
            error_msg = f"Calendar API error: {e}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Failed to create event: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def update_event(self, event_id: str, summary: Optional[str] = None,
                     start_time: Optional[str] = None, end_time: Optional[str] = None,
                     description: Optional[str] = None, location: Optional[str] = None,
                     calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Update an existing calendar event
        
        Args:
            event_id: ID of event to update
            summary: New event title (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            description: New description (optional)
            location: New location (optional)
            calendar_id: Calendar containing the event (default: 'primary')
            
        Returns:
            Dictionary with status and updated event details
        """
        if not self.service:
            return {"status": "error", "message": "Calendar service not initialized"}
        
        if not event_id:
            return {"status": "error", "message": "Missing required field: event_id"}
        
        try:
            Logger.log(f"Updating calendar event: {event_id}", "CALENDAR")
            
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if summary:
                event['summary'] = summary
            
            if start_time:
                event['start'] = {'dateTime': start_time, 'timeZone': 'UTC'}
            
            if end_time:
                event['end'] = {'dateTime': end_time, 'timeZone': 'UTC'}
            
            if description is not None:  # Allow empty string to clear description
                event['description'] = description
            
            if location is not None:  # Allow empty string to clear location
                event['location'] = location
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            Logger.log(f"Event {event_id} updated successfully", "CALENDAR")
            Logger.log_chat("TOOL", f"✅ Calendar event updated")
            
            return {
                "status": "success",
                "message": f"Event updated successfully",
                "event_id": updated_event['id'],
                "event_link": updated_event.get('htmlLink', ''),
                "summary": updated_event.get('summary', '')
            }
        
        except HttpError as e:
            error_msg = f"Calendar API error: {e}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Failed to update event: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Delete a calendar event
        
        Args:
            event_id: ID of event to delete
            calendar_id: Calendar containing the event (default: 'primary')
            
        Returns:
            Dictionary with status
        """
        if not self.service:
            return {"status": "error", "message": "Calendar service not initialized"}
        
        if not event_id:
            return {"status": "error", "message": "Missing required field: event_id"}
        
        try:
            Logger.log(f"Deleting calendar event: {event_id}", "CALENDAR")
            
            # Delete the event
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            Logger.log(f"Event {event_id} deleted successfully", "CALENDAR")
            Logger.log_chat("TOOL", f"✅ Calendar event deleted")
            
            return {
                "status": "success",
                "message": f"Event deleted successfully",
                "event_id": event_id
            }
        
        except HttpError as e:
            error_msg = f"Calendar API error: {e}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Failed to delete event: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def search_events(self, query: str, max_results: int = 10,
                      calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Search for events matching a query
        
        Args:
            query: Search query (matches event title, description, location)
            max_results: Maximum number of events to return
            calendar_id: Calendar to search (default: 'primary')
            
        Returns:
            Dictionary with status and matching events
        """
        if not self.service:
            return {"status": "error", "message": "Calendar service not initialized"}
        
        if not query:
            return {"status": "error", "message": "Missing required field: query"}
        
        try:
            Logger.log(f"Searching calendar events for: {query}", "CALENDAR")
            
            # Search events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            Logger.log(f"Found {len(events)} matching events", "CALENDAR")
            
            # Format events
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'html_link': event.get('htmlLink', '')
                })
            
            Logger.log_chat("TOOL", f"📅 Found {len(formatted_events)} events matching '{query}'")
            
            return {
                "status": "success",
                "count": len(formatted_events),
                "events": formatted_events,
                "query": query,
                "message": f"Found {len(formatted_events)} events matching '{query}'"
            }
        
        except HttpError as e:
            error_msg = f"Calendar API error: {e}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Failed to search events: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Get details of a specific event
        
        Args:
            event_id: ID of event to retrieve
            calendar_id: Calendar containing the event (default: 'primary')
            
        Returns:
            Dictionary with status and event details
        """
        if not self.service:
            return {"status": "error", "message": "Calendar service not initialized"}
        
        if not event_id:
            return {"status": "error", "message": "Missing required field: event_id"}
        
        try:
            Logger.log(f"Fetching calendar event: {event_id}", "CALENDAR")
            
            # Get the event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            event_details = {
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'attendees': [a.get('email') for a in event.get('attendees', [])],
                'status': event.get('status', 'confirmed'),
                'html_link': event.get('htmlLink', ''),
                'created': event.get('created', ''),
                'updated': event.get('updated', '')
            }
            
            Logger.log(f"Event retrieved: {event_details['summary']}", "CALENDAR")
            Logger.log_chat("TOOL", f"📅 Retrieved event details")
            
            return {
                "status": "success",
                "event": event_details,
                "message": "Event details retrieved successfully"
            }
        
        except HttpError as e:
            error_msg = f"Calendar API error: {e}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Failed to get event: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
