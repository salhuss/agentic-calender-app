// API Types - Generated from backend OpenAPI schema

export interface Event {
  id: number;
  title: string;
  description?: string;
  start_datetime: string;
  end_datetime: string;
  all_day: boolean;
  location?: string;
  attendees: string[];
  original_timezone: string;
  created_at: string;
  updated_at: string;
}

export interface EventCreate {
  title: string;
  description?: string;
  start_datetime: string;
  end_datetime: string;
  all_day?: boolean;
  location?: string;
  attendees?: string[];
  original_timezone?: string;
}

export interface EventUpdate {
  title?: string;
  description?: string;
  start_datetime?: string;
  end_datetime?: string;
  all_day?: boolean;
  location?: string;
  attendees?: string[];
  original_timezone?: string;
}

export interface EventListResponse {
  events: Event[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface EventDraft {
  title: string;
  description?: string;
  start_datetime?: string;
  end_datetime?: string;
  all_day: boolean;
  location?: string;
  attendees: string[];
  confidence: number;
  extracted_entities: Record<string, any>;
}

export interface APIError {
  detail: {
    code: string;
    message: string;
    fields?: Record<string, any>;
  };
}

export interface EventFilters {
  from?: string;
  to?: string;
  query?: string;
  page?: number;
  size?: number;
}