import React, { useState, useEffect } from 'react';
import { DateTime } from 'luxon';
import { useForm } from 'react-hook-form';
import { Event, EventCreate, EventUpdate } from '@/types/api';
import { useCreateEvent, useUpdateEvent, useDeleteEvent, useCreateEventDraft } from '@/hooks/useEvents';
import { formatTimeForInput, formatDateForInput, parseInputDateTime, parseInputDate, getCurrentTimezone } from '@/utils/date';

interface EventModalProps {
  event?: Event | null;
  defaultDate?: DateTime | null;
  onClose: () => void;
}

interface EventFormData {
  title: string;
  description?: string;
  startDate: string;
  startTime: string;
  endDate: string;
  endTime: string;
  allDay: boolean;
  location?: string;
  attendees: string;
  aiPrompt?: string;
}

const EventModal: React.FC<EventModalProps> = ({ event, defaultDate, onClose }) => {
  const [showAIHelper, setShowAIHelper] = useState(!event);
  const [aiLoading, setAILoading] = useState(false);

  const createMutation = useCreateEvent();
  const updateMutation = useUpdateEvent();
  const deleteMutation = useDeleteEvent();
  const aiDraftMutation = useCreateEventDraft();

  const isEditing = !!event;
  const currentTz = getCurrentTimezone();

  // Set up form with default values
  const getDefaultValues = (): EventFormData => {
    if (event) {

      return {
        title: event.title,
        description: event.description || '',
        startDate: formatDateForInput(event.start_datetime),
        startTime: event.all_day ? '09:00' : formatTimeForInput(event.start_datetime).split('T')[1],
        endDate: formatDateForInput(event.end_datetime),
        endTime: event.all_day ? '17:00' : formatTimeForInput(event.end_datetime).split('T')[1],
        allDay: event.all_day,
        location: event.location || '',
        attendees: event.attendees.join(', '),
      };
    } else {
      const defaultStart = defaultDate || DateTime.now();
      const defaultEnd = defaultStart.plus({ hours: 1 });

      return {
        title: '',
        description: '',
        startDate: defaultStart.toFormat('yyyy-MM-dd'),
        startTime: '09:00',
        endDate: defaultEnd.toFormat('yyyy-MM-dd'),
        endTime: '10:00',
        allDay: false,
        location: '',
        attendees: '',
        aiPrompt: '',
      };
    }
  };

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<EventFormData>({
    defaultValues: getDefaultValues(),
  });

  const watchAllDay = watch('allDay');
  const watchStartDate = watch('startDate');
  const watchAiPrompt = watch('aiPrompt');

  // Auto-set end date when start date changes
  useEffect(() => {
    if (watchStartDate) {
      const currentEndDate = watch('endDate');
      if (!currentEndDate || currentEndDate < watchStartDate) {
        setValue('endDate', watchStartDate);
      }
    }
  }, [watchStartDate, setValue, watch]);

  const handleAIDraft = async () => {
    if (!watchAiPrompt?.trim()) return;

    setAILoading(true);
    try {
      const draft = await aiDraftMutation.mutateAsync(watchAiPrompt);

      // Fill form with AI suggestions
      setValue('title', draft.title);
      if (draft.description) setValue('description', draft.description);
      if (draft.location) setValue('location', draft.location);
      if (draft.attendees.length > 0) setValue('attendees', draft.attendees.join(', '));

      setValue('allDay', draft.all_day);

      if (draft.start_datetime) {
        const startDt = DateTime.fromISO(draft.start_datetime);
        setValue('startDate', startDt.toFormat('yyyy-MM-dd'));
        if (!draft.all_day) {
          setValue('startTime', startDt.toFormat('HH:mm'));
        }
      }

      if (draft.end_datetime) {
        const endDt = DateTime.fromISO(draft.end_datetime);
        setValue('endDate', endDt.toFormat('yyyy-MM-dd'));
        if (!draft.all_day) {
          setValue('endTime', endDt.toFormat('HH:mm'));
        }
      }

      setShowAIHelper(false);
    } catch (error) {
      console.error('AI draft error:', error);
    } finally {
      setAILoading(false);
    }
  };

  const onSubmit = async (data: EventFormData) => {
    try {
      let startDateTime: string;
      let endDateTime: string;

      if (data.allDay) {
        const { start, end } = parseInputDate(data.startDate, currentTz);
        startDateTime = start;
        endDateTime = parseInputDate(data.endDate, currentTz).end;
      } else {
        startDateTime = parseInputDateTime(`${data.startDate}T${data.startTime}`, currentTz);
        endDateTime = parseInputDateTime(`${data.endDate}T${data.endTime}`, currentTz);
      }

      const attendees = data.attendees
        ? data.attendees.split(',').map(email => email.trim()).filter(Boolean)
        : [];

      const eventData = {
        title: data.title,
        description: data.description || undefined,
        start_datetime: startDateTime,
        end_datetime: endDateTime,
        all_day: data.allDay,
        location: data.location || undefined,
        attendees,
        original_timezone: currentTz,
      };

      if (isEditing) {
        await updateMutation.mutateAsync({
          id: event.id,
          event: eventData as EventUpdate,
        });
      } else {
        await createMutation.mutateAsync(eventData as EventCreate);
      }

      onClose();
    } catch (error) {
      console.error('Submit error:', error);
    }
  };

  const handleDelete = async () => {
    if (!event || !confirm('Are you sure you want to delete this event?')) return;

    try {
      await deleteMutation.mutateAsync(event.id);
      onClose();
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {isEditing ? 'Edit Event' : 'Create Event'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
            disabled={isLoading}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* AI Helper */}
        {showAIHelper && !isEditing && (
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-700">
            <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
              AI Event Assistant
            </h3>
            <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
              Describe your event in natural language and I'll help fill out the details.
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                {...register('aiPrompt')}
                placeholder="e.g., Meeting with John tomorrow 3pm at Cafe Rio"
                className="form-input flex-1 text-sm"
                disabled={aiLoading}
              />
              <button
                type="button"
                onClick={handleAIDraft}
                disabled={aiLoading || !watchAiPrompt?.trim()}
                className="btn-primary text-sm px-3 py-1"
              >
                {aiLoading ? 'Generating...' : 'Generate'}
              </button>
            </div>
            <div className="mt-2 flex justify-between">
              <div></div>
              <button
                type="button"
                onClick={() => setShowAIHelper(false)}
                className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
              >
                Fill manually
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Title */}
          <div>
            <label className="form-label">
              Title *
            </label>
            <input
              type="text"
              {...register('title', { required: 'Title is required' })}
              className="form-input"
              disabled={isLoading}
            />
            {errors.title && (
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.title.message}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="form-label">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="form-input"
              disabled={isLoading}
            />
          </div>

          {/* All Day Toggle */}
          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('allDay')}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
              disabled={isLoading}
            />
            <label className="ml-2 block text-sm text-gray-900 dark:text-gray-100">
              All day
            </label>
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">
                Start Date *
              </label>
              <input
                type="date"
                {...register('startDate', { required: 'Start date is required' })}
                className="form-input"
                disabled={isLoading}
              />
              {errors.startDate && (
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.startDate.message}</p>
              )}
            </div>
            <div>
              <label className="form-label">
                End Date *
              </label>
              <input
                type="date"
                {...register('endDate', { required: 'End date is required' })}
                className="form-input"
                disabled={isLoading}
              />
              {errors.endDate && (
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.endDate.message}</p>
              )}
            </div>
          </div>

          {!watchAllDay && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="form-label">
                  Start Time
                </label>
                <input
                  type="time"
                  {...register('startTime')}
                  className="form-input"
                  disabled={isLoading}
                />
              </div>
              <div>
                <label className="form-label">
                  End Time
                </label>
                <input
                  type="time"
                  {...register('endTime')}
                  className="form-input"
                  disabled={isLoading}
                />
              </div>
            </div>
          )}

          {/* Location */}
          <div>
            <label className="form-label">
              Location
            </label>
            <input
              type="text"
              {...register('location')}
              className="form-input"
              placeholder="e.g., Conference Room A, Zoom, etc."
              disabled={isLoading}
            />
          </div>

          {/* Attendees */}
          <div>
            <label className="form-label">
              Attendees
            </label>
            <input
              type="text"
              {...register('attendees')}
              className="form-input"
              placeholder="Enter email addresses, separated by commas"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Separate multiple email addresses with commas
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4">
            <div>
              {isEditing && (
                <button
                  type="button"
                  onClick={handleDelete}
                  className="btn-danger"
                  disabled={isLoading}
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                </button>
              )}
            </div>
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={isLoading}
              >
                {isLoading
                  ? isEditing
                    ? 'Updating...'
                    : 'Creating...'
                  : isEditing
                  ? 'Update Event'
                  : 'Create Event'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EventModal;