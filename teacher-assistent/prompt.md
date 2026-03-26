Build a "Teacher Assistant" web application — a single-page tool where students paste an assignment prompt and write an essay to receive AI-powered rubric feedback from Claude.

## Files to create

### `index.html` — Full single-file frontend (HTML + CSS + JS)

**Layout:** Two-column grid (320px left panel, 1fr right panel), responsive to single column below 860px. Sticky header.

**Header:**
- Logo: blue rounded-rect icon with horizontal lines SVG + "Teacher Assistant" text
- Buttons: "Save Session" and "Load Session" (secondary style)

**Left panel (3 cards stacked):**
1. **Assignment card** — School level `<select>` (Elementary K-5, Middle 6-8, High School 9-12, Undergraduate, Graduate) + Assignment Prompt `<textarea>` (min 160px)
2. **AI Settings card** — Password input for Anthropic API key, note saying key is stored in localStorage and sent to Anthropic API, link to console.anthropic.com
3. **Saved Sessions card** (hidden by default, toggled by Load Session button) — scrollable list of saved session items with name, date, word count, and a delete (×) button

**Right panel (2 cards stacked):**
1. **Essay card** — Large `<textarea>` (min 360px, no border), footer bar with word count (highlighted in blue) and two buttons: "Clear" + "Get Feedback" (green)
   - Selecting a school level shows a blue badge in this card's header
2. **Feedback Rubric card** — Shows empty state SVG + message by default; becomes a 2-column grid of rubric items after feedback is received, plus an overall feedback box

**Rubric criteria (6 items):** Grammar, Structure, Content Relevance, Answers the Question, Appropriate Level, Meets Requirements
- Each item: label + icon, score out of 10, color-coded progress bar, 2-3 sentence feedback
- Score colors: green (≥8), amber (5-7), red (<5)

**Save Session modal:** Overlay with session name input, Cancel + Save buttons

**CSS design tokens:**
- Colors: blue `#2563eb`, green `#16a34a`, amber `#d97706`, red `#dc2626`, gray scale from `#f8fafc` to `#0f172a`
- Border radius: 10px, subtle box shadows

**JavaScript behavior:**
- Live word count on essay textarea input
- School level change → show/hide badge in essay card header
- Clear essay button with confirm dialog (skips if empty)
- Save/load/delete sessions via `localStorage` key `teacher_assistant_sessions`; sessions store: name, savedAt ISO string, assignment text, schoolLevel, essay text
- API key persisted to `localStorage` key `ta_api_key`, restored on DOMContentLoaded
- Toast notification (bottom-center, dark pill, auto-dismisses after 2s) for save/load actions
- Modal closes on backdrop click or Escape key; Enter in session name input triggers save

**getFeedback() function:**
- Validates: API key present, assignment present, essay present, school level selected — shows error in rubric area if any missing
- Shows spinner ("Analyzing your essay...") and disables "Get Feedback" button
- POSTs to `/api/chat` with body: `{ apiKey, model: "claude-sonnet-4-6", max_tokens: 1200, system: "...", messages: [{role:"user", content:"..."}] }`
- System prompt: experienced teacher, respond with ONLY valid JSON, no markdown
- User prompt asks Claude to evaluate the essay for the selected school level and return JSON with exactly these keys: `grammar`, `structure`, `contentRelevance`, `answersQuestion`, `appropriateLevel`, `meetsRequirements` (each with `score` 1-10 and `feedback` string), plus `overallFeedback` string
- Parses response JSON (falls back to regex extraction if wrapped in backticks)
- Renders rubric grid with color-coded items and overall feedback box
- Re-enables button in finally block

### `server.js` — Node.js local proxy server

- Plain `http`/`https`/`fs`/`path` — no npm dependencies
- Listens on port 3000
- `POST /api/chat` → strips `apiKey` from body, forwards remaining payload to `https://api.anthropic.com/v1/messages` with headers: `Content-Type: application/json`, `x-api-key`, `anthropic-version: 2023-06-01`; pipes response back to client
- All other routes → static file serving from `__dirname`, defaulting `GET /` to `index.html`; MIME types for `.html`, `.css`, `.js`, `.json`
- Logs: `Teacher Assistant running at http://localhost:3000`

## Usage
Run with `node server.js` then open http://localhost:3000. No npm install needed.