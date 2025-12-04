// jarvis-ui/app/services/api.ts

// Use Next.js API routes (same-origin, more reliable than direct backend calls)
// Next.js routes proxy to the backend at localhost:8000
const API_BASE_URL = "/api";

// Backend URL for weather (can be proxied later if needed)
const BACKEND_URL = "http://localhost:8000/api";

// Fetch weather data via REST (for initial load or manual refresh)
export const fetchWeather = async (city: string = "Bengaluru") => { // Add city parameter
  try {
    // Weather still uses direct backend call (can be proxied if needed)
    const response = await fetch(`${BACKEND_URL}/weather?city=${encodeURIComponent(city)}`);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
        console.error("Weather fetch failed:", errorData);
        return { status: "error", message: errorData?.message || `Failed to fetch weather for ${city}` };
    }
    return response.json();
  } catch (error: any) {
    console.error("Weather fetch network error:", error);
    // Check if it's a connection refused error
    if (error.message.includes("fetch")) {
      return { status: "error", message: "Cannot connect to backend. Please ensure backend server is running on port 8000." };
    }
    return { status: "error", message: error.message || "Network error fetching weather" };
  }
};

// --- Settings API ---

// Fetch all settings
export const getSettings = async () => {
  try {
    // Use Next.js API route for reliability
    const response = await fetch(`${API_BASE_URL}/settings`);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
      console.error("Get settings failed:", errorData);
      throw new Error(errorData?.error || "Failed to fetch settings");
    }
    return response.json();
  } catch (error: any) {
    console.error("Get settings network error:", error);
    if (error.message.includes("fetch") || error.message.includes("Failed to fetch")) {
      throw new Error("Cannot connect to backend. Please ensure backend server is running on port 8000.");
    }
    throw new Error(error.message || "Network error fetching settings");
  }
};

// Update a specific setting
export const updateSetting = async (key: string, value: string) => {
  const response = await fetch(`${API_BASE_URL}/settings/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
    console.error(`Update setting '${key}' failed:`, errorData);
    throw new Error(errorData?.error || `Failed to update setting: ${key}`);
  }
  return response.json();
};

// --- Contacts API ---

// Add a new contact
export const addContact = async (telegram_id: string, names: string[], phone?: string, email?: string) => {
  const response = await fetch(`${API_BASE_URL}/contacts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    // Send all potential contact fields
    body: JSON.stringify({ telegram_id, names, phone, email }),
  });
  if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
      console.error('Add contact failed:', errorData);
      throw new Error(errorData?.error || errorData?.message || 'Failed to add contact');
  }
  return response.json();
};

// Delete a contact
export const deleteContact = async (name: string) => {
  const response = await fetch(`${API_BASE_URL}/contacts/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
      console.error('Delete contact failed:', errorData);
      throw new Error(errorData?.error || errorData?.message || 'Failed to delete contact');
  }
  return response.json();
};

// Update a contact
export const updateContact = async (name: string, data: { names?: string[]; phone?: string; email?: string; telegram_id?: string }) => {
  const response = await fetch(`${API_BASE_URL}/contacts/${encodeURIComponent(name)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
      console.error('Update contact failed:', errorData);
      throw new Error(errorData?.error || errorData?.message || 'Failed to update contact');
  }
  return response.json();
};

// --- Automation API (via REST, could also be done via WebSocket) ---

// Get current brightness
export const getBrightness = async (): Promise<{ brightness?: number; error?: string }> => {
    try {
        const response = await fetch(`${API_BASE_URL}/brightness`);
        if (!response.ok) {
             const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
             return { error: errorData?.error || "Failed to get brightness" };
        }
        return await response.json();
    } catch (error: any) {
        return { error: error.message || "Network error getting brightness" };
    }
};

// Set brightness
export const setBrightness = async (brightness: number): Promise<{ success?: boolean; error?: string; message?: string }> => {
    try {
        const response = await fetch(`${API_BASE_URL}/brightness`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brightness })
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
             return { error: errorData?.error || "Failed to set brightness" };
        }
        return await response.json();
    } catch (error: any) {
         return { error: error.message || "Network error setting brightness" };
    }
};

// Change Windows theme
export const changeTheme = async (mode: 'dark' | 'light'): Promise<{ success?: boolean; error?: string; message?: string }> => {
    try {
        const response = await fetch(`${API_BASE_URL}/theme`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
         if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
             return { error: errorData?.error || "Failed to change theme" };
        }
        return await response.json();
    } catch (error: any) {
         return { error: error.message || "Network error changing theme" };
    }
};


// --- Removed direct WebSocket interactions from here ---
// toggleMic and stopJarvis are now handled via useWebSocket hook in components


// --- Removed unused/placeholder API calls ---
// fetchChatHistory and sendMessage are handled via WebSocket