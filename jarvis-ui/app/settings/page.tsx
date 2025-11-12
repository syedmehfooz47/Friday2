// jarvis-ui/app/settings/page.tsx

"use client";

import { useEffect, useState, memo } from "react";
import { Header } from "@/app/(dashboard)/_comps/Header"; // Adjust import path if needed
import { FrostedCard } from "@/app/(dashboard)/_comps/ui/FrostedCard"; // Adjust import path if needed
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area"; // Import ScrollArea
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { getSettings, updateSetting, addContact, deleteContact, updateContact } from "@/app/services/api"; // Updated API functions
import { toast } from "sonner";
import { BrainCircuit, Contact, KeyRound, Trash2, Mail, Phone } from "lucide-react"; // Added icons

// Interface for API Key Slot structure
interface ApiKeySlot {
    slot: string;
    label: string;
    has_key: boolean;
    is_active: boolean;
}

// Interface for API Keys structure
interface ApiKeys {
    groq: ApiKeySlot[];
    google: ApiKeySlot[];
}

// Interface for Model structure
interface Models {
    Groq?: string;
    Gemini?: string;
    Ollama?: string;
    Cohere?: string;
}

// Interface for Contact structure (matching backend)
interface ContactType {
    names: string[];
    phone?: string | null;
    telegram_id?: string | null;
    email?: string | null;
}

// Helper to format model names (handles potential missing keys)
const formatModelName = (name: string | undefined): string => {
    if (!name) return "N/A";
    // Basic formatting, adjust if model names have complex structures
    return name.split(':')[0].split('/').pop() || name;
};

export default function SettingsPage() {
    // State initialization with better typing
    const [settings, setSettings] = useState<{
        api_keys: ApiKeys;
        models: Models;
        contacts: ContactType[]; // Store contacts as an array
        llm_provider: string;
        active_assistant: string;
        active_groq_api: string;
        active_google_api: string;
    }>({
        api_keys: { groq: [], google: [] },
        models: {},
        contacts: [],
        llm_provider: "Groq",
        active_assistant: "Friday",
        active_groq_api: "",
        active_google_api: ""
    });
    const [isLoading, setIsLoading] = useState(true);
    const [newContactName, setNewContactName] = useState("");
    const [newContactTelegramId, setNewContactTelegramId] = useState("");
    const [newContactPhone, setNewContactPhone] = useState("");
    const [newContactEmail, setNewContactEmail] = useState("");
    const [contactNames, setContactNames] = useState<string[]>([]);
    const [isAddContactOpen, setIsAddContactOpen] = useState(false);

    // Fetch settings on component mount
    const loadSettings = async () => {
        setIsLoading(true);
        try {
            const fetchedSettings = await getSettings();
             // Add checks for potentially missing fields
             const apiKeys: ApiKeys = fetchedSettings.api_keys || { groq: [], google: [] };
             const models: Models = fetchedSettings.models || {};
             const contacts: ContactType[] = fetchedSettings.contacts || [];

            setSettings({
                 api_keys: apiKeys,
                 models: models,
                 contacts: contacts,
                 llm_provider: fetchedSettings.llm_provider || "Groq",
                 active_assistant: fetchedSettings.active_assistant || "Friday",
                 active_groq_api: fetchedSettings.active_groq_api || (apiKeys.groq.length > 0 ? apiKeys.groq[0].slot : ""),
                 active_google_api: fetchedSettings.active_google_api || (apiKeys.google.length > 0 ? apiKeys.google[0].slot : "")
            });
            console.log("Settings loaded:", fetchedSettings);
        } catch (error: any) {
            toast.error("Failed to load settings", { description: error.message });
            console.error("Settings load error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { loadSettings(); }, []);

    // Generic handler for updating settings via API
    const handleSettingChange = async (key: string, value: string, successMessage: string) => {
        // Optimistically update local state for faster UI feedback
        setSettings(prev => ({ ...prev, [key.toLowerCase()]: value })); // Match state keys

        try {
            await updateSetting(key, value); // Call API
            toast.success(successMessage);
             // Optionally re-fetch settings if backend modifies other things on update
             // await loadSettings();
        } catch (error: any) {
            toast.error("Update Failed", { description: error.message });
             // Revert optimistic update on failure
            await loadSettings(); // Re-fetch to ensure consistency
        }
    };

    const handleApiKeyChange = async (provider: 'groq' | 'google', value: string) => {
         const key = provider === 'groq' ? 'ACTIVE_GROQ_API' : 'ACTIVE_GOOGLE_API';
         const stateKey = provider === 'groq' ? 'active_groq_api' : 'active_google_api';

         // Optimistic update
        setSettings(prev => ({ ...prev, [stateKey]: value }));

        try {
            await updateSetting(key, value);
            toast.success(`Active ${provider === 'groq' ? 'Groq' : 'Google'} key set to ${value}. Restart backend if needed.`);
        } catch (error: any) {
             toast.error(`Failed to set active ${provider} key`, { description: error.message });
             await loadSettings(); // Revert
        }
    };

    // Handler for adding a new contact
    const handleAddContact = async (e: React.FormEvent) => {
         e.preventDefault(); // Prevent form submission page reload
        const names = contactNames.filter(Boolean); // Use the names array

        if (names.length === 0) {
            toast.error("Invalid Input", { description: "Please provide at least one contact name." });
            return;
        }
        if (!newContactTelegramId.trim() && !newContactPhone.trim() && !newContactEmail.trim()) {
            toast.error("Invalid Input", { description: "Please provide Telegram ID, Phone, or Email." });
            return;
        }

        try {
            // Call API with all fields (empty strings are handled by backend/contacts_manager)
            const response = await addContact(
                newContactTelegramId.trim(),
                names,
                newContactPhone.trim() || undefined, // Send undefined if empty
                newContactEmail.trim() || undefined // Send undefined if empty
            );
            // Update local state with the full list returned by the API
            setSettings(prev => ({ ...prev, contacts: response.contacts }));
            setNewContactName("");
            setNewContactTelegramId("");
            setNewContactPhone("");
            setNewContactEmail("");
            setContactNames([]);
            setIsAddContactOpen(false);
            toast.success(response.message || "Contact Added");
        } catch (error: any) {
            toast.error("Failed to add contact", { description: error.message });
        }
    };

    const handleAddAlias = () => {
        if (newContactName.trim()) {
            setContactNames(prev => [...prev, newContactName.trim()]);
            setNewContactName("");
        }
    };

     // Handler for delete contact
    const handleDeleteContact = async (contactNameToDelete: string) => {
        try {
            const response = await deleteContact(contactNameToDelete);
            setSettings(prev => ({ ...prev, contacts: response.contacts }));
            toast.success(response.message || "Contact Deleted");
        } catch (error: any) {
            toast.error("Failed to delete contact", { description: error.message });
        }
    };


    // Prepare options for LLM provider RadioGroup
    const llmOptions = [
        { id: "Groq", name: "Groq", model: formatModelName(settings.models?.Groq) },
        // { id: "Cohere", name: "Cohere", model: formatModelName(settings.models?.Cohere) }, // Uncomment if Cohere added
        { id: "Gemini", name: "Gemini", model: formatModelName(settings.models?.Gemini) },
        { id: "Ollama", name: "Local (Ollama)", model: formatModelName(settings.models?.Ollama) },
    ].filter(opt => opt.model && opt.model !== "N/A"); // Filter out providers with no model listed

    // Prepare options for Assistant personality RadioGroup
    const assistantOptions = ["Friday", "Jarvis"]; // Use Assistantname values from .env?

    return (
        <div className="min-h-screen text-slate-900 dark:text-slate-100 relative overflow-hidden p-4 sm:p-6 lg:p-8">
             {/* Background Effects */}
            <div aria-hidden="true" className="fixed inset-0 -z-10 overflow-hidden">
                <div className="absolute inset-0 bg-white dark:bg-slate-950"></div>
                <div className="absolute top-0 left-0 h-[40rem] w-[40rem] bg-cyan-200/50 dark:bg-cyan-500/20 rounded-full blur-[16rem] filter opacity-70 dark:opacity-50"></div>
                 <div className="absolute -bottom-20 -right-20 h-[40rem] w-[40rem] bg-purple-200/50 dark:bg-purple-500/20 rounded-full blur-[16rem] filter opacity-70 dark:opacity-50"></div>
            </div>

            <Header />

            <main className="max-w-6xl mx-auto">
                 <h1 className="text-3xl font-bold mb-8 text-slate-800 dark:text-slate-100">Settings</h1>

                 {isLoading ? (
                     <div className="flex justify-center items-center h-64">
                         <p className="text-slate-500 animate-pulse">Loading settings...</p>
                     </div>
                 ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Column 1: Core Settings */}
                        <section className="space-y-8 lg:col-span-1">
                            {/* Personality Core */}
                            <div>
                                <h2 className="text-xl font-semibold mb-4 text-slate-700 dark:text-slate-200">Personality Core</h2>
                                <RadioGroup
                                    value={settings.active_assistant}
                                    onValueChange={(val) => handleSettingChange('Assistantname', val, `Personality switched to ${val}. Restart backend.`)}
                                    className="space-y-3"
                                >
                                    {assistantOptions.map(option => (
                                        <Label key={option} htmlFor={option} className={`flex items-center p-4 rounded-xl border transition-all cursor-pointer ${settings.active_assistant === option ? 'border-cyan-500 bg-cyan-500/10 shadow-inner' : 'border-slate-200 dark:border-white/10 bg-slate-100/5 dark:bg-white/5 hover:border-slate-300 dark:hover:border-white/20'}`}>
                                            <RadioGroupItem value={option} id={option} className="mr-3 flex-shrink-0" />
                                            <p className="font-medium text-slate-800 dark:text-slate-100">{option}</p>
                                        </Label>
                                    ))}
                                </RadioGroup>
                            </div>

                             {/* AI Model Provider */}
                            <div>
                                <h2 className="text-xl font-semibold mb-4 text-slate-700 dark:text-slate-200">AI Model Provider</h2>
                                <RadioGroup
                                    value={settings.llm_provider}
                                    onValueChange={(val) => handleSettingChange('LLM_PROVIDER', val, `Primary provider set to ${val}. Restart backend.`)}
                                    className="space-y-3"
                                >
                                     {llmOptions.length > 0 ? llmOptions.map(option => (
                                        <Label key={option.id} htmlFor={option.id} className={`flex items-center p-4 rounded-xl border transition-all cursor-pointer ${settings.llm_provider === option.id ? 'border-cyan-500 bg-cyan-500/10 shadow-inner' : 'border-slate-200 dark:border-white/10 bg-slate-100/5 dark:bg-white/5 hover:border-slate-300 dark:hover:border-white/20'}`}>
                                            <RadioGroupItem value={option.id} id={option.id} className="mr-3 flex-shrink-0" />
                                            <div className="flex-1">
                                                <p className="font-medium text-slate-800 dark:text-slate-100">{option.name}</p>
                                                <p className="text-xs text-slate-500 dark:text-slate-400">{option.model}</p>
                                            </div>
                                            <BrainCircuit className={`w-5 h-5 flex-shrink-0 ml-2 transition-colors ${settings.llm_provider === option.id ? 'text-cyan-400' : 'text-slate-500'}`} />
                                        </Label>
                                    )) : <p className="text-sm text-slate-500">No models configured in backend.</p>}
                                </RadioGroup>
                            </div>
                        </section>

                        {/* Column 2 & 3: API Keys and Contacts */}
                        <section className="space-y-8 lg:col-span-2">
                             {/* API Key Rotation */}
                            <div>
                                <h2 className="text-xl font-semibold mb-4 text-slate-700 dark:text-slate-200">API Key Rotation</h2>
                                <FrostedCard>
                                    <div className="p-4 md:p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <Label className="flex items-center text-slate-600 dark:text-slate-300 font-medium">
                                                <KeyRound className="w-4 h-4 mr-2 text-purple-400" />Active Groq API Key
                                            </Label>
                                            {settings.api_keys.groq.length > 0 ? (
                                                <Select value={settings.active_groq_api} onValueChange={(val) => handleApiKeyChange('groq', val)}>
                                                    <SelectTrigger className="bg-white/50 dark:bg-black/20"><SelectValue placeholder="Select Groq Key Slot" /></SelectTrigger>
                                                    <SelectContent>
                                                        {settings.api_keys.groq.map((slot) => (
                                                            <SelectItem 
                                                                key={slot.slot} 
                                                                value={slot.slot}
                                                                disabled={!slot.has_key}
                                                            >
                                                                {slot.label} {!slot.has_key && '(No API Key)'}
                                                            </SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            ) : <p className="text-sm text-slate-500 pt-2">No Groq key slots configured</p>}
                                        </div>
                                        <div className="space-y-2">
                                            <Label className="flex items-center text-slate-600 dark:text-slate-300 font-medium">
                                                <KeyRound className="w-4 h-4 mr-2 text-blue-400" />Active Google API Key
                                            </Label>
                                             {settings.api_keys.google.length > 0 ? (
                                                <Select value={settings.active_google_api} onValueChange={(val) => handleApiKeyChange('google', val)}>
                                                    <SelectTrigger className="bg-white/50 dark:bg-black/20"><SelectValue placeholder="Select Google Key Slot" /></SelectTrigger>
                                                    <SelectContent>
                                                        {settings.api_keys.google.map((slot) => (
                                                            <SelectItem 
                                                                key={slot.slot} 
                                                                value={slot.slot}
                                                                disabled={!slot.has_key}
                                                            >
                                                                {slot.label} {!slot.has_key && '(No API Key)'}
                                                            </SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            ) : <p className="text-sm text-slate-500 pt-2">No Google key slots configured</p>}
                                        </div>
                                    </div>
                                </FrostedCard>
                            </div>

                            {/* Telegram Contacts */}
                            <div>
                                <h2 className="text-xl font-semibold mb-4 text-slate-700 dark:text-slate-200">Telegram Contacts</h2>
                                <FrostedCard>
                                    <div className="p-4 md:p-6">
                                        {/* Contact List */}
                                        <div className="mb-4">
                                            <h3 className="text-sm font-medium text-slate-600 dark:text-slate-300 mb-2">Saved Contacts</h3>
                                             <ScrollArea className="h-48 border rounded-lg border-slate-200 dark:border-white/10 p-2 bg-slate-50/5 dark:bg-black/10">
                                                <div className="space-y-2">
                                                    {settings.contacts.length > 0 ? settings.contacts.map((contact, index) => (
                                                        <div key={`contact-${index}-${contact.names[0] || 'unknown'}`} className="flex items-center justify-between text-sm p-3 bg-white/50 dark:bg-black/20 rounded-lg shadow-sm">
                                                            <div className="flex-1 overflow-hidden mr-2">
                                                                <p className="font-medium text-slate-800 dark:text-slate-200 truncate">{contact.names.join(', ')}</p>
                                                                {contact.telegram_id && <p className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center"><Contact className="w-3 h-3 mr-1 text-blue-400" /> {contact.telegram_id}</p>}
                                                                {contact.phone && <p className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center"><Phone className="w-3 h-3 mr-1 text-green-400" /> {contact.phone}</p>}
                                                                {contact.email && <p className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center"><Mail className="w-3 h-3 mr-1 text-purple-400" /> {contact.email}</p>}
                                                            </div>
                                                            <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:bg-red-500/10 hover:text-red-600" onClick={() => handleDeleteContact(contact.names[0])}>
                                                                <Trash2 className="w-4 h-4" />
                                                            </Button>
                                                        </div>
                                                    )) : <p className="text-sm text-slate-400 text-center py-4">No contacts added yet.</p>}
                                                </div>
                                             </ScrollArea>
                                        </div>

                                        {/* Add Contact Button */}
                                        <Dialog open={isAddContactOpen} onOpenChange={setIsAddContactOpen}>
                                            <DialogTrigger asChild>
                                                <Button className="w-full bg-cyan-600 hover:bg-cyan-700">Add Contact</Button>
                                            </DialogTrigger>
                                            <DialogContent className="sm:max-w-[425px]">
                                                <DialogHeader>
                                                    <DialogTitle>Add New Contact</DialogTitle>
                                                </DialogHeader>
                                                <form onSubmit={handleAddContact} className="space-y-3">
                                                    <div>
                                                        <Label>Name</Label>
                                                        <div className="flex space-x-2">
                                                            <Input placeholder="Enter name" value={newContactName} onChange={e => setNewContactName(e.target.value)} />
                                                            <Button type="button" onClick={handleAddAlias} variant="outline">Add Alias</Button>
                                                        </div>
                                                        {contactNames.length > 0 && (
                                                            <div className="mt-2">
                                                                <p className="text-sm text-slate-600 dark:text-slate-400">Aliases: {contactNames.join(', ')}</p>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <Input placeholder="Telegram Chat ID (Optional)" value={newContactTelegramId} onChange={e => setNewContactTelegramId(e.target.value)} />
                                                    <Input placeholder="Phone Number (Optional)" value={newContactPhone} onChange={e => setNewContactPhone(e.target.value)} type="tel"/>
                                                    <Input placeholder="Email Address (Optional)" value={newContactEmail} onChange={e => setNewContactEmail(e.target.value)} type="email"/>
                                                    <Button type="submit" className="w-full bg-cyan-600 hover:bg-cyan-700">Add Contact</Button>
                                                </form>
                                            </DialogContent>
                                        </Dialog>
                                    </div>
                                </FrostedCard>
                            </div>
                        </section>
                    </div>
                 )}
            </main>
        </div>
    );
}