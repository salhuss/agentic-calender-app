// API Client
import {
  Event,
  EventCreate,
  EventUpdate,
  EventListResponse,
  EventDraft,
  EventFilters,
  APIError,
} from '@/types/api';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error: APIError = await response.json();
        throw new Error(error.detail.message || 'API request failed');
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error');
    }
  }

  // Events API
  async getEvents(filters: EventFilters = {}): Promise<EventListResponse> {
    const searchParams = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });

    const query = searchParams.toString();
    const endpoint = `/events${query ? `?${query}` : ''}`;

    return this.request<EventListResponse>(endpoint);
  }

  async getEvent(id: number): Promise<Event> {
    return this.request<Event>(`/events/${id}`);
  }

  async createEvent(event: EventCreate): Promise<Event> {
    return this.request<Event>('/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  }

  async updateEvent(id: number, event: EventUpdate): Promise<Event> {
    return this.request<Event>(`/events/${id}`, {
      method: 'PUT',
      body: JSON.stringify(event),
    });
  }

  async deleteEvent(id: number): Promise<void> {
    await this.request<void>(`/events/${id}`, {
      method: 'DELETE',
    });
  }

  async createEventDraft(prompt: string): Promise<EventDraft> {
    return this.request<EventDraft>('/events/draft', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }
}

export const apiClient = new APIClient();