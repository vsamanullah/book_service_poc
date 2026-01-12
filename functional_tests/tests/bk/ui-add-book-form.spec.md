# UI Add Book Form Test Suite

## Overview
This test suite validates the **"Add Book" form functionality** on the BookService application. It ensures the book creation form works correctly, covering UI elements, user interactions, and form submission behavior.

## Test File
`ui-add-book-form.spec.ts`

## Application Under Test
- **URL**: http://localhost:50524/
- **Feature**: Add Book form on the homepage

## Test Categories

### 1. Form Display & Structure
Tests that verify the form renders correctly with all required elements.

#### Tests:
- **should display the Add Book section**
  - Verifies the "Add Book" heading (level 2) is visible on the page

- **should display all form fields**
  - Checks Author dropdown (combobox) is visible
  - Checks Title textbox is visible
  - Checks Year spinbutton is visible
  - Checks Genre textbox is visible
  - Checks Price spinbutton is visible
  - Checks Submit button is visible

- **should have Genre field with placeholder**
  - Validates the Genre field has "Fiction" as placeholder text

- **should have proper form labels**
  - Ensures all labels are present: Author, Title, Year, Genre, Price

### 2. Dropdown Functionality
Tests that verify the author selection dropdown works correctly.

#### Tests:
- **should have default author selected**
  - Confirms that a default author is pre-selected when page loads

- **should display all author options**
  - Verifies dropdown contains: Jane Austen, Charles Dickens, Miguel de Cervantes

- **should allow selecting different authors**
  - Tests changing the selected author to Charles Dickens
  - Verifies the selection is updated correctly

### 3. Form Input Validation
Tests that verify form fields accept appropriate input types.

#### Tests:
- **should validate year field accepts numeric input**
  - Tests filling Year field with "2025"
  - Verifies input type is "number"

- **should validate price field accepts decimal input**
  - Tests filling Price field with "29.99"
  - Verifies input type is "number"
  - Confirms decimal values are accepted

- **should fill out complete form**
  - Tests filling all fields:
    - Author: Jane Austen
    - Title: Test Book Title
    - Year: 2025
    - Genre: Mystery
    - Price: 29.99
  - Verifies all values are correctly set

### 4. Form Submission
Tests that verify form submission behavior and data persistence.

#### Tests:
- **should submit form and add book to list**
  - Creates unique book title with timestamp
  - Fills complete form with test data
  - Submits the form
  - Verifies book count increases or new book appears in list

- **should clear form after successful submission**
  - Fills and submits form
  - Documents post-submission form state

- **should handle form with minimal required fields**
  - Tests submitting with only Author and Title
  - Verifies page remains functional

- **should submit form using Enter key in text field**
  - Fills all form fields
  - Presses Enter in the Price field
  - Verifies form submits successfully

- **should handle multiple rapid submissions**
  - Submits form twice in quick succession
  - Verifies page remains stable and functional

### 5. User Experience & State Management
Tests that verify form behavior during user interaction.

#### Tests:
- **should maintain form state during interaction**
  - Partially fills form
  - Navigates to API page and back
  - Documents whether form state is preserved

- **should display form in correct visual hierarchy**
  - Verifies "Books" section appears before "Add Book" section
  - Confirms both book list and form are visible on same page

## Test Setup
- **beforeEach hook**: Navigates to the application homepage before each test
- **Test isolation**: Each test runs independently with fresh page state

## Selectors Used
The tests use accessibility-focused selectors following Playwright best practices:
- `getByRole('heading')` - For headings
- `getByRole('combobox')` - For dropdown/select elements
- `getByRole('textbox')` - For text input fields
- `getByRole('spinbutton')` - For numeric input fields
- `getByRole('button')` - For buttons

## Expected Behavior
1. Form should display with all required fields
2. Author dropdown should have pre-populated options
3. Numeric fields should only accept numbers
4. Form submission should add book to the list
5. Form should handle various submission methods (click, keyboard)

## Notes
- Uses unique timestamps in test data to avoid conflicts
- Includes wait periods for form submission processing
- Tests document actual behavior rather than prescribing expected outcomes
- Comprehensive coverage of happy path and edge cases
