# -*- coding: utf-8 -*-
"""
Contacts Manager - Manage contacts with multiple names, phone, telegram,
 email
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from .logger import Logger

load_dotenv()


class ContactsManager:
    """Manage contacts database"""
    
    def __init__(self):
        self.database_dir = Path(__file__).parent.parent / "Database"
        self.contacts_file = self.database_dir / "contacts.json"
        self._initialize_contacts_file()
        Logger.log("ContactsManager initialized", "CONTACTS")
    
    def _initialize_contacts_file(self):
        """Initialize contacts.json if it doesn't exist"""
        self.database_dir.mkdir(exist_ok=True)
        
        if not self.contacts_file.exists():
            with open(self.contacts_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            Logger.log("Created contacts.json file", "CONTACTS")
    
    def load_contacts(self) -> List[Dict]:
        """Load all contacts"""
        try:
            with open(self.contacts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            Logger.log(f"Error loading contacts: {e}", "ERROR")
            return []
    
    def save_contacts(self, contacts: List[Dict]):
        """Save contacts to file"""
        try:
            with open(self.contacts_file, "w", encoding="utf-8") as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            Logger.log("Contacts saved successfully", "CONTACTS")
        except Exception as e:
            Logger.log(f"Error saving contacts: {e}", "ERROR")
    
    def add_contact(self, names: List[str], phone: str = None, 
                    telegram_id: str = None, email: str = None) -> Dict[str, Any]:
        """
        Add a new contact
        
        Args:
            names: List of names/aliases for the contact
            phone: Phone number
            telegram_id: Telegram ID
            email: Email address
            
        Returns:
            Result dictionary
        """
        if not names or len(names) == 0:
            return {"status": "error", "message": "At least one name is required"}
        
        contacts = self.load_contacts()
        
        # Check if contact already exists
        for contact in contacts:
            if any(name.lower() in [n.lower() for n in contact["names"]] for name in names):
                return {"status": "error", "message": f"Contact with name '{names[0]}' already exists"}
        
        new_contact = {
            "names": names,
            "phone": phone,
            "telegram_id": telegram_id,
            "email": email
        }
        
        contacts.append(new_contact)
        self.save_contacts(contacts)
        
        Logger.log(f"Added contact: {names[0]}", "CONTACTS")
        return {
            "status": "success",
            "message": f"Contact '{names[0]}' added successfully",
            "contact": new_contact
        }
    
    def find_contact(self, name: str) -> Optional[Dict]:
        """Find contact by any of their names"""
        contacts = self.load_contacts()
        
        for contact in contacts:
            if any(name.lower() == n.lower() for n in contact["names"]):
                return contact
        
        return None
    
    def update_contact(self, name: str, names: List[str] = None, 
                       phone: str = None, telegram_id: str = None, 
                       email: str = None) -> Dict[str, Any]:
        """
        Update an existing contact
        
        Args:
            name: Current name to find contact
            names: New list of names (optional)
            phone: New phone number (optional)
            telegram_id: New telegram ID (optional)
            email: New email (optional)
            
        Returns:
            Result dictionary
        """
        contacts = self.load_contacts()
        
        for i, contact in enumerate(contacts):
            if any(name.lower() == n.lower() for n in contact["names"]):
                if names:
                    contact["names"] = names
                if phone is not None:
                    contact["phone"] = phone
                if telegram_id is not None:
                    contact["telegram_id"] = telegram_id
                if email is not None:
                    contact["email"] = email
                
                contacts[i] = contact
                self.save_contacts(contacts)
                
                Logger.log(f"Updated contact: {name}", "CONTACTS")
                return {
                    "status": "success",
                    "message": f"Contact '{name}' updated successfully",
                    "contact": contact
                }
        
        return {"status": "error", "message": f"Contact '{name}' not found"}
    
    def delete_contact(self, name: str) -> Dict[str, Any]:
        """Delete a contact"""
        contacts = self.load_contacts()
        
        for i, contact in enumerate(contacts):
            if any(name.lower() == n.lower() for n in contact["names"]):
                deleted_contact = contacts.pop(i)
                self.save_contacts(contacts)
                
                Logger.log(f"Deleted contact: {name}", "CONTACTS")
                return {
                    "status": "success",
                    "message": f"Contact '{name}' deleted successfully",
                    "contact": deleted_contact
                }
        
        return {"status": "error", "message": f"Contact '{name}' not found"}
    
    def list_all_contacts(self) -> Dict[str, Any]:
        """List all contacts"""
        contacts = self.load_contacts()
        
        return {
            "status": "success",
            "count": len(contacts),
            "contacts": contacts
        }
    
    def get_contact_info(self, name: str, info_type: str) -> Optional[str]:
        """
        Get specific information from a contact
        
        Args:
            name: Contact name
            info_type: 'phone', 'telegram_id', or 'email'
            
        Returns:
            Requested information or None
        """
        contact = self.find_contact(name)
        
        if contact:
            return contact.get(info_type)
        
        return None


# Global instance
contacts_manager = ContactsManager()