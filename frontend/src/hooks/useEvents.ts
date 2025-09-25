// React Query hooks for events
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import {
  Event,
  EventCreate,
  EventUpdate,
  EventFilters,
  EventDraft,
} from '@/types/api';

// Query keys
export const eventKeys = {
  all: ['events'] as const,
  lists: () => [...eventKeys.all, 'list'] as const,
  list: (filters: EventFilters) => [...eventKeys.lists(), filters] as const,
  details: () => [...eventKeys.all, 'detail'] as const,
  detail: (id: number) => [...eventKeys.details(), id] as const,
};

// Hooks
export const useEvents = (filters: EventFilters = {}) => {
  return useQuery({
    queryKey: eventKeys.list(filters),
    queryFn: () => apiClient.getEvents(filters),
  });
};

export const useEvent = (id: number) => {
  return useQuery({
    queryKey: eventKeys.detail(id),
    queryFn: () => apiClient.getEvent(id),
    enabled: !!id,
  });
};

export const useCreateEvent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (event: EventCreate) => apiClient.createEvent(event),
    onSuccess: () => {
      // Invalidate and refetch events list
      queryClient.invalidateQueries({ queryKey: eventKeys.lists() });
    },
  });
};

export const useUpdateEvent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, event }: { id: number; event: EventUpdate }) =>
      apiClient.updateEvent(id, event),
    onSuccess: (data, variables) => {
      // Update the specific event in cache
      queryClient.setQueryData(eventKeys.detail(variables.id), data);
      // Invalidate lists to refresh
      queryClient.invalidateQueries({ queryKey: eventKeys.lists() });
    },
  });
};

export const useDeleteEvent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.deleteEvent(id),
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: eventKeys.detail(id) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: eventKeys.lists() });
    },
  });
};

export const useCreateEventDraft = () => {
  return useMutation({
    mutationFn: (prompt: string) => apiClient.createEventDraft(prompt),
  });
};