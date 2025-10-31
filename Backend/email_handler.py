# -*- coding: utf-8 -*-
"""
Advanced Email Handler - Professional email management
Supports sending, reading, deleting, and replying to emails
Uses Gmail API with OAuth2 authentication
"""

import base64
import json
import mimetypes
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from Backend.logger import Logger

load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Token file location
TOKEN_FILE = Path(__file__).parent.parent / "Database" / "gmail_token.json"
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"


class EmailHandler:
    """Advanced email management handler using Gmail API"""
    
    def __init__(self):
        self.service = None
        self.user_email = None
        self._initialize_gmail_service()
        Logger.log("EmailHandler initialized", "EMAIL")
    
    def _initialize_gmail_service(self) -> bool:
        """
        Initialize Gmail API service with OAuth2 authentication
        
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
                    Logger.log("Loaded existing Gmail credentials", "EMAIL")
                except Exception as e:
                    Logger.log(f"Failed to load existing credentials: {e}", "ERROR")
                    creds = None
            
            # If no valid credentials, perform OAuth2 flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        Logger.log("Refreshed Gmail credentials", "EMAIL")
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
                        Logger.log("OAuth2 authentication successful", "EMAIL")
                    except Exception as e:
                        Logger.log(f"OAuth2 authentication failed: {e}", "ERROR")
                        return False
                
                # Save credentials for next time
                try:
                    with open(str(TOKEN_FILE), 'w') as token:
                        token.write(creds.to_json())
                    Logger.log("Gmail credentials saved", "EMAIL")
                except Exception as e:
                    Logger.log(f"Failed to save credentials: {e}", "ERROR")
            
            # Build Gmail service
            try:
                self.service = build('gmail', 'v1', credentials=creds)
                # pylint: disable=no-member
                profile = self.service.users().getProfile(userId='me').execute()
                self.user_email = profile.get('emailAddress', 'unknown')
                Logger.log(f"Gmail service initialized for: {self.user_email}", "EMAIL")
                return True
            except Exception as e:
                Logger.log(f"Failed to build Gmail service: {e}", "ERROR")
                return False
        
        except Exception as e:
            Logger.log(f"Error initializing Gmail service: {e}", "ERROR")
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: Optional[str] = None, bcc: Optional[str] = None,
                   attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            to: Recipient email address(es), comma-separated
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients, optional
            bcc: BCC recipients, optional
            attachments: List of file paths to attach
            
        Returns:
            Dictionary with status and message
        """
        if not self.service:
            return {"status": "error", "message": "Gmail service not initialized"}
        
        if not to or not subject or body is None:
            return {"status": "error", "message": "Missing required fields: to, subject, body"}
        
        try:
            Logger.log(f"Preparing to send email to: {to}", "EMAIL")
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to.strip()
            message['subject'] = subject.strip()
            
            if cc:
                message['cc'] = cc.strip()
            if bcc:
                message['bcc'] = bcc.strip()
            
            # Add body (detect if HTML)
            if '<html>' in body.lower() or '<body>' in body.lower():
                part = MIMEText(body, 'html')
            else:
                part = MIMEText(body, 'plain')
            message.attach(part)

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if not os.path.exists(file_path):
                        Logger.log(f"Attachment file not found: {file_path}", "WARNING")
                        continue
                    
                    content_type, encoding = mimetypes.guess_type(file_path)
                    if content_type is None or encoding is not None:
                        content_type = 'application/octet-stream'
                    main_type, sub_type = content_type.split('/', 1)
                    
                    try:
                        with open(file_path, 'rb') as fp:
                            part = MIMEBase(main_type, sub_type)
                            part.set_payload(fp.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                        message.attach(part)
                        Logger.log(f"Successfully attached file: {file_path}", "EMAIL")
                    except Exception as e:
                        Logger.log(f"Error attaching file {file_path}: {e}", "ERROR")

            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            send_message = {
                'raw': raw_message
            }
            
            # pylint: disable=no-member
            result = self.service.users().messages().send(
                userId='me', 
                body=send_message
            ).execute()
            
            Logger.log(f"Email sent successfully to {to} with ID: {result.get('id')}", "EMAIL")
            Logger.log_chat("TOOL", f"✅ Email sent to {to}")
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {to}",
                "email_id": result.get('id'),
                "recipients": to,
                "subject": subject
            }
        
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def read_emails(self, folder: str = "INBOX", limit: int = 10, 
                    unread_only: bool = False, sender: Optional[str] = None,
                    subject_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Read emails from specified folder
        
        Args:
            folder: Folder to read from (INBOX, SENT, DRAFTS, TRASH)
            limit: Maximum emails to retrieve
            unread_only: Only unread emails
            sender: Filter by sender email
            subject_filter: Filter by subject keyword
            
        Returns:
            Dictionary with email list
        """
        if not self.service:
            return {"status": "error", "message": "Gmail service not initialized"}
        
        try:
            Logger.log(f"Reading {limit} emails from {folder}", "EMAIL")
            
            # Build query
            query_parts = []
            
            # Map folder names to Gmail labels
            label_map = {
                "INBOX": "INBOX",
                "SENT": "SENT",
                "DRAFTS": "DRAFTS",
                "TRASH": "TRASH",
                "SPAM": "SPAM"
            }
            
            label = label_map.get(folder.upper(), folder)
            query_parts.append(f"in:{label}")
            
            if unread_only:
                query_parts.append("is:unread")
            
            if sender:
                query_parts.append(f"from:{sender}")
            
            if subject_filter:
                query_parts.append(f"subject:{subject_filter}")
            
            query = " ".join(query_parts)
            Logger.log(f"Query: {query}", "EMAIL")
            
            # Search messages
            # pylint: disable=no-member
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            Logger.log(f"Found {len(messages)} emails", "EMAIL")
            
            email_list = []
            
            for msg in messages:
                try:
                    # Get full message
                    # pylint: disable=no-member
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    headers = message['payload']['headers']
                    
                    # Extract email details
                    email_data = {
                        "id": msg['id'],
                        "from": self._get_header(headers, 'From'),
                        "to": self._get_header(headers, 'To'),
                        "subject": self._get_header(headers, 'Subject'),
                        "date": self._get_header(headers, 'Date'),
                        "snippet": message.get('snippet', ''),
                        "unread": 'UNREAD' in message.get('labelIds', [])
                    }
                    
                    email_list.append(email_data)
                
                except Exception as e:
                    Logger.log(f"Error processing message {msg['id']}: {e}", "ERROR")
                    continue
            
            Logger.log(f"Successfully retrieved {len(email_list)} emails", "EMAIL")
            
            return {
                "status": "success",
                "folder": folder,
                "count": len(email_list),
                "emails": email_list
            }
        
        except Exception as e:
            error_msg = f"Failed to read emails: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def delete_email(self, email_id: Optional[str] = None, 
                     folder: Optional[str] = None, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete email(s)
        
        Args:
            email_id: Specific email ID to delete
            folder: Folder to delete all emails from
            confirm: Confirmation flag
            
        Returns:
            Dictionary with status
        """
        if not self.service:
            return {"status": "error", "message": "Gmail service not initialized"}
        
        if not confirm:
            return {"status": "error", "message": "Deletion requires confirmation. Set confirm=True"}
        
        try:
            if email_id:
                Logger.log(f"Deleting email ID: {email_id}", "EMAIL")
                # pylint: disable=no-member
                self.service.users().messages().delete(
                    userId='me',
                    id=email_id
                ).execute()
                
                Logger.log(f"Email {email_id} deleted successfully", "EMAIL")
                Logger.log_chat("TOOL", f"✅ Email deleted")
                
                return {
                    "status": "success",
                    "message": f"Email {email_id} deleted successfully",
                    "deleted_id": email_id
                }
            
            elif folder:
                Logger.log(f"Deleting all emails from {folder}", "EMAIL")
                
                # Get all emails in folder
                # pylint: disable=no-member
                results = self.service.users().messages().list(
                    userId='me',
                    q=f"in:{folder}",
                    maxResults=100
                ).execute()
                
                messages = results.get('messages', [])
                deleted_count = 0
                
                for msg in messages:
                    try:
                        # pylint: disable=no-member
                        self.service.users().messages().delete(
                            userId='me',
                            id=msg['id']
                        ).execute()
                        deleted_count += 1
                    except Exception as e:
                        Logger.log(f"Error deleting message {msg['id']}: {e}", "ERROR")
                
                Logger.log(f"Deleted {deleted_count} emails from {folder}", "EMAIL")
                Logger.log_chat("TOOL", f"✅ Deleted {deleted_count} emails from {folder}")
                
                return {
                    "status": "success",
                    "message": f"Deleted {deleted_count} emails from {folder}",
                    "deleted_count": deleted_count,
                    "folder": folder
                }
            
            else:
                return {"status": "error", "message": "Specify either email_id or folder"}
        
        except Exception as e:
            error_msg = f"Failed to delete email: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    def reply_email(self, email_id: str, body: str, 
                    reply_all: bool = False) -> Dict[str, Any]:
        """
        Reply to an email
        
        Args:
            email_id: ID of email to reply to
            body: Reply message body
            reply_all: Reply to all recipients
            
        Returns:
            Dictionary with status
        """
        if not self.service:
            return {"status": "error", "message": "Gmail service not initialized"}
        
        if not email_id or not body:
            return {"status": "error", "message": "Missing required fields: email_id, body"}
        
        try:
            Logger.log(f"Preparing reply to email ID: {email_id}", "EMAIL")
            
            # Get original message
            # pylint: disable=no-member
            original_message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            headers = original_message['payload']['headers']
            original_subject = self._get_header(headers, 'Subject')
            original_from = self._get_header(headers, 'From')
            original_to = self._get_header(headers, 'To')
            message_id = self._get_header(headers, 'Message-ID')
            
            # Create reply subject
            if not original_subject.startswith('Re:'):
                reply_subject = f"Re: {original_subject}"
            else:
                reply_subject = original_subject
            
            # Create reply message
            reply_message = MIMEMultipart('alternative')
            reply_message['to'] = original_from
            reply_message['subject'] = reply_subject
            reply_message['In-Reply-To'] = message_id
            reply_message['References'] = message_id
            
            # Add body
            part = MIMEText(body, 'plain')
            reply_message.attach(part)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode()
            
            send_message = {'raw': raw_message}
            
            # pylint: disable=no-member
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            Logger.log(f"Reply sent to {original_from} with ID: {result.get('id')}", "EMAIL")
            Logger.log_chat("TOOL", f"✅ Reply sent to {original_from}")
            
            return {
                "status": "success",
                "message": f"Reply sent to {original_from}",
                "reply_id": result.get('id'),
                "reply_to": original_from,
                "subject": reply_subject
            }
        
        except Exception as e:
            error_msg = f"Failed to send reply: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
    
    @staticmethod
    def _get_header(headers: List[Dict], name: str) -> str:
        """
        Extract header value from headers list
        
        Args:
            headers: List of header dictionaries
            name: Header name to find
            
        Returns:
            Header value or empty string
        """
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ""