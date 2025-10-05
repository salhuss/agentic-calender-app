import { test, expect } from '@playwright/test';

test.describe('Calendar CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the calendar app
    await page.goto('/');

    // Wait for the app to load
    await expect(page.locator('text=AI Calendar')).toBeVisible();
  });

  test('should create, edit, and delete an event', async ({ page }) => {
    // Step 1: Create a new event
    await page.click('text=New Event');

    // Fill out the event form
    await page.fill('input[name="title"]', 'Test Event');
    await page.fill('textarea[name="description"]', 'This is a test event');
    await page.fill('input[name="startDate"]', '2023-12-15');
    await page.fill('input[name="startTime"]', '14:00');
    await page.fill('input[name="endTime"]', '15:00');
    await page.fill('input[name="location"]', 'Test Location');

    // Submit the form
    await page.click('button:has-text("Create Event")');

    // Wait for the modal to close and event to appear
    await expect(page.locator('text=Test Event')).toBeVisible();

    // Step 2: Edit the event
    await page.click('text=Test Event');

    // Update the title
    await page.fill('input[name="title"]', 'Updated Test Event');
    await page.fill('input[name="location"]', 'Updated Location');

    // Save changes
    await page.click('button:has-text("Update Event")');

    // Verify the event was updated
    await expect(page.locator('text=Updated Test Event')).toBeVisible();

    // Step 3: Delete the event
    await page.click('text=Updated Test Event');

    // Delete the event
    await page.click('button:has-text("Delete")');

    // Confirm deletion in the dialog
    page.on('dialog', dialog => dialog.accept());

    // Verify the event is no longer visible
    await expect(page.locator('text=Updated Test Event')).not.toBeVisible();
  });

  test('should create an all-day event', async ({ page }) => {
    // Create a new event
    await page.click('text=New Event');

    // Fill out the form for an all-day event
    await page.fill('input[name="title"]', 'All Day Conference');
    await page.check('input[name="allDay"]');
    await page.fill('input[name="startDate"]', '2023-12-20');
    await page.fill('input[name="endDate"]', '2023-12-22');

    // Submit the form
    await page.click('button:has-text("Create Event")');

    // Verify the all-day event appears
    await expect(page.locator('text=All Day Conference')).toBeVisible();
  });

  test('should switch between calendar views', async ({ page }) => {
    // Test month view (default)
    await expect(page.locator('button:has-text("month")')).toHaveClass(/bg-white/);

    // Switch to week view
    await page.click('button:has-text("week")');
    await expect(page.locator('button:has-text("week")')).toHaveClass(/bg-white/);

    // Switch to day view
    await page.click('button:has-text("day")');
    await expect(page.locator('button:has-text("day")')).toHaveClass(/bg-white/);

    // Switch back to month view
    await page.click('button:has-text("month")');
    await expect(page.locator('button:has-text("month")')).toHaveClass(/bg-white/);
  });

  test('should navigate between dates', async ({ page }) => {
    // Get the current month/year text
    const currentTitle = await page.locator('h1').textContent();

    // Navigate to next month
    await page.click('[aria-label="Next"]');

    // Verify the title changed
    const nextTitle = await page.locator('h1').textContent();
    expect(nextTitle).not.toBe(currentTitle);

    // Navigate to previous month
    await page.click('[aria-label="Previous"]');

    // Should be back to original title
    const backTitle = await page.locator('h1').textContent();
    expect(backTitle).toBe(currentTitle);

    // Click "Today" button
    await page.click('button:has-text("Today")');

    // Should show current month
    const todayTitle = await page.locator('h1').textContent();
    expect(todayTitle).toContain('2023'); // Assuming tests run in 2023
  });

  test('should use AI assistant to create event', async ({ page }) => {
    // Create a new event
    await page.click('text=New Event');

    // Use the AI assistant
    await page.fill('input[name="aiPrompt"]', 'Meeting with John tomorrow at 3pm at Cafe Rio');
    await page.click('button:has-text("Generate")');

    // Wait for AI to populate fields
    await page.waitForTimeout(1000);

    // Check that fields were populated
    const title = await page.inputValue('input[name="title"]');
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    // Submit the event
    await page.click('button:has-text("Create Event")');

    // Verify event was created
    await expect(page.locator(`text=${title}`)).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page, isMobile }) => {
    if (isMobile) {
      // On mobile, sidebar should be hidden initially
      await expect(page.locator('text=AI Calendar')).not.toBeVisible();

      // Calendar should be visible and functional
      await expect(page.locator('.calendar-grid')).toBeVisible();

      // New Event button should be accessible
      await expect(page.locator('button:has-text("New Event")')).toBeVisible();

      // Day view should be default on mobile
      await expect(page.locator('button:has-text("day")')).toHaveClass(/bg-white/);
    }
  });

  test('should validate form inputs', async ({ page }) => {
    // Try to create event without title
    await page.click('text=New Event');
    await page.click('button:has-text("Create Event")');

    // Should show validation error
    await expect(page.locator('text=Title is required')).toBeVisible();

    // Fill title but set invalid time (end before start)
    await page.fill('input[name="title"]', 'Test Event');
    await page.fill('input[name="startTime"]', '15:00');
    await page.fill('input[name="endTime"]', '14:00');

    // Try to submit
    await page.click('button:has-text("Create Event")');

    // Should show time validation error or prevent submission
    // (Exact behavior depends on implementation)
  });
});