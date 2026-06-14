# FawkesPath — Frontend

The web client for **FawkesPath**, an intelligent career mentor. Upload your
résumé, get an AI‑predicted next best skill and a multi‑step career pathway
toward a target role, receive course recommendations and daily nudges, track
your progress as a growing tree of achievements, and chat with **Fawkes**, an
on‑screen avatar assistant.

This is a single‑page React application. It talks to several backend services
(Django REST API + a Flask résumé‑processor / ML prediction service) through a
shared API base URL.

---

## Tech Stack

| Concern            | Choice |
| ------------------ | ------ |
| Framework          | [React 19](https://react.dev/) (bootstrapped with Create React App / `react-scripts` 5) |
| Routing            | [React Router](https://reactrouter.com/) v7 (`BrowserRouter`) |
| Global state       | [Redux Toolkit](https://redux-toolkit.js.org/) + React‑Redux (avatar state) |
| Auth state         | React Context (`AuthContext`) |
| HTTP               | [Axios](https://axios-http.com/) with per‑service clients & interceptors |
| Styling            | [Tailwind CSS](https://tailwindcss.com/) v3 + PostCSS / Autoprefixer |
| Markdown           | `react-markdown` (chat rendering) |
| QR codes           | `qrcode.react` (TOTP setup) |
| Testing            | Jest + React Testing Library (via `react-scripts test`) |

---

## Prerequisites

- **Node.js** 18+ and **npm** (CRA 5 / React 19).
- A running backend reachable at `REACT_APP_API_BASE_URL` (the Django API and
  the Flask `resume-processor` are both served under this base URL).

---

## Getting Started

```bash
# from the frontend/ directory
npm install        # install dependencies
npm start          # start the dev server at http://localhost:3000
```

The app expects the backend to be available at the URL configured in `.env`
(default `http://localhost:8000/api`).

---

## Environment Variables

Configuration is provided through CRA environment variables in a `.env` file at
the project root. `.env` is git‑ignored, so create your own from the example
below. **All variables must be prefixed with `REACT_APP_`** to be exposed to the
browser.

```dotenv
# Base URL for all backend services (Django API + Flask resume-processor).
# The trailing path matters: clients append /auth, /resumes, /resume-processor, etc.
REACT_APP_API_BASE_URL=http://localhost:8000/api

# Product / brand name shown in the header, manifest, etc.
REACT_APP_NAME=FawkesPath

# Display name of the on-screen avatar assistant.
REACT_APP_AVATAR_NAME=Fawkes
```

To point at a deployed backend, swap the base URL (an example production URL is
commented in `.env`). Restart `npm start` after changing any `REACT_APP_*` value.

---

## Available Scripts

| Command          | Description |
| ---------------- | ----------- |
| `npm start`      | Run the dev server with hot reload at `http://localhost:3000`. |
| `npm test`       | Run the test suite in interactive watch mode. |
| `npm run build`  | Produce an optimized production build in `build/`. |
| `npm run eject`  | Eject CRA configuration (one‑way; avoid unless necessary). |

To run tests once (non‑interactive, e.g. in CI):

```bash
CI=true npm test
```

---

## Project Structure

```
frontend/
├── public/                 # Static assets served as-is
│   ├── index.html          # HTML shell (#root mount point)
│   ├── manifest.json       # PWA metadata
│   ├── avatar/             # Avatar state images (idle, thinking, celebrating, …)
│   ├── leaf_left/right.png # Decorative assets
│   └── logo.png, favicon.ico
├── src/
│   ├── index.js            # App entry: wires Redux <Provider>, <BrowserRouter>, <AuthProvider>
│   ├── App.jsx             # Route table + auth/route guards + global chrome (Header, Avatar)
│   ├── index.css           # Tailwind directives + global styles
│   │
│   ├── config/             # Axios clients, one per backend service
│   │   ├── api-backend.js          # Django REST API: auth, resumes, chat, nudges
│   │   ├── api-progress.js         # Progress/achievements API
│   │   └── api-resume-processor.js # Flask resume-processor: parsing + ML skill prediction
│   │
│   ├── context/
│   │   └── AuthContext.jsx  # Auth provider: login, TOTP, register, current user
│   │
│   ├── store/              # Redux Toolkit
│   │   ├── index.js         # Store configuration
│   │   └── avatarSlice.js   # Avatar mood/visibility state machine
│   │
│   ├── pages/             # Full-page, route-level screens
│   │   ├── Login.jsx, Signup.jsx
│   │   ├── ForgotPassword.jsx, ResetPassword.jsx
│   │   ├── TOTPSetup.jsx, TOTPVerify.jsx   # Two-factor auth
│   │   └── Profile.jsx
│   │
│   ├── views/
│   │   └── MainApp.jsx      # Tabbed shell (Dashboard / History / Progress)
│   │
│   ├── components/         # Reusable UI + feature components
│   │   ├── Dashboard.jsx           # Main authenticated landing view
│   │   ├── ResumeUpload.jsx        # Upload + target-role selection
│   │   ├── ResumeHistory.jsx       # Past résumés, activate/switch
│   │   ├── NextBestStep.jsx        # ML-predicted next skill
│   │   ├── CareerPathway.jsx       # Multi-step roadmap to target role
│   │   ├── CourseRecommendations.jsx
│   │   ├── DailyNudge.jsx          # AI-generated daily motivation
│   │   ├── ProgressTree.jsx        # Achievements visualized as a tree
│   │   ├── Achievement*.jsx, AddAchievementModal.jsx, SkillUploadModal.jsx
│   │   ├── Avatar.jsx, ChatWindow.jsx   # On-screen assistant + chat
│   │   ├── Header.jsx, Logo.jsx
│   │   ├── UserProfile.jsx, UserAvatar.jsx
│   │   ├── PasswordInput.jsx, SearchableDropdown.jsx
│   │   └── …
│   │
│   └── utils/
│       └── skills.js        # Display formatting for skill labels
└── tailwind.config.js, postcss.config.js
```

---

## Application Architecture

### Composition & providers

`src/index.js` mounts the app inside three providers, outermost to innermost:

1. **Redux `<Provider>`** — global UI state (the avatar).
2. **`<BrowserRouter>`** — client‑side routing.
3. **`<AuthProvider>`** — authentication/session state.

`App.jsx` then renders the route table plus the persistent chrome — the
`Header` (tabs) and the floating `Avatar` assistant — when the user is fully
authenticated.

### Routing & guards

Routes are defined in `App.jsx`. Two guard components enforce access:

- **`ProtectedRoute`** — requires a logged‑in user **with TOTP confirmed**;
  otherwise redirects to `/login` or `/totp-setup`.
- **`GuestOnly`** — redirects authenticated users away from auth pages.

| Path                          | Screen           | Access |
| ----------------------------- | ---------------- | ------ |
| `/login`                      | Login            | Guests only |
| `/signup`                     | Signup           | Guests only |
| `/forgot-password`            | Forgot password  | Guests only |
| `/reset-password/:uid/:token` | Reset password   | Guests only |
| `/totp-verify`                | TOTP login code  | Only when a login is pending 2FA |
| `/totp-setup`                 | TOTP enrollment  | Logged in, not yet confirmed |
| `/profile`                    | Profile          | Protected |
| `/`                           | Main app (tabs)  | Protected |

The main app (`/`) is a **tabbed view** (`MainApp.jsx`) rather than separate
routes — Dashboard, History, and My Progress are switched via header tabs and
local state.

### Authentication & 2FA

`AuthContext` owns the session. On mount it reads JWT tokens from
`localStorage` and validates them via `/auth/me/`. The login flow supports
**TOTP two‑factor authentication**:

1. `login()` posts credentials. If the backend responds with `totp_required`,
   the app stores a short‑lived `totp_token` and routes to `/totp-verify`.
2. `verifyTotpLogin(code)` exchanges the code for JWT access/refresh tokens.
3. New users without TOTP are routed to `/totp-setup`, which renders a QR code
   (`qrcode.react`) to enroll an authenticator app.

Tokens are persisted in `localStorage` under the `tokens` key.

### API layer

Each backend service has its own Axios client in `src/config/`:

- **`api-backend.js`** — the Django REST API. Exposes `authAPI`, `resumeAPI`
  (résumés, next‑best‑step, career pathway, course recommendations), `chatAPI`,
  and `nudgeAPI`.
- **`api-progress.js`** — `progressService` for achievements (multipart image
  uploads).
- **`api-resume-processor.js`** — the Flask résumé‑processor/ML service for
  résumé parsing, skill catalogs, designations, and next‑skill prediction.

**Interceptors** on the Django and progress clients:

- *Request* — attach `Authorization: Bearer <access>` from `localStorage`.
- *Response* — on a `401`, transparently refresh the token via
  `/auth/token/refresh/` and retry the original request once; if refresh fails,
  clear tokens and redirect to `/login`.

### Global state (Redux)

The Redux store currently holds a single **`avatar`** slice — a small state
machine driving the assistant's mood/animation (`idle`, `listening`,
`thinking`, `analyzing`, `presenting`, `encouraging`, `celebrating`, `error`,
`warning`) plus visibility and contextual messages. Feature components dispatch
state changes (e.g. `setState('thinking')` while a résumé is processed) so the
avatar reacts to what the app is doing.

---

## Key Features

- **Résumé upload & parsing** — upload a résumé and pick a target designation;
  the résumé‑processor extracts skills.
- **Next Best Step** — ML‑predicted single next skill toward the target role.
- **Career Pathway** — a multi‑step roadmap visualization toward the goal role.
- **Course Recommendations** — suggested courses to close skill gaps.
- **Daily Nudge** — AI‑generated daily motivation, regenerable on demand.
- **Progress Tree** — achievements rendered as a growing tree; add achievements
  with proof images.
- **Fawkes avatar & chat** — a persistent assistant with a context‑aware mood
  and a Markdown‑rendered chat window backed by conversation history.
- **Résumé history** — view past résumés and switch the active one.
- **Secure auth** — JWT sessions, TOTP 2FA, password reset.

---

## Styling

Tailwind CSS is configured in `tailwind.config.js` (scanning `src/**/*.{js,jsx,ts,tsx}`)
with a few custom animations (`fade-in`, `fade-in-up`, `slide-in`, `scale-in`,
`pulse-soft`). Global directives live in `src/index.css`. The UI favors a calm,
minimal aesthetic with indigo accents.

---

## Building for Production

```bash
npm run build
```

This emits a minified, hash‑named bundle in `build/`. Serve it as static files
behind any web server (e.g. nginx) and ensure SPA fallback routing (all unknown
paths → `index.html`) so client‑side routes resolve. Set `REACT_APP_API_BASE_URL`
to the deployed backend before building.

---

## Testing

Tests use Jest and React Testing Library via `react-scripts`. Setup lives in
`src/setupTests.js`.

```bash
npm test            # watch mode
CI=true npm test    # single run
```

---

## Notes

- This is the **frontend only**. It requires the FawkesPath backend services
  (Django API + Flask résumé‑processor) to be running and reachable at
  `REACT_APP_API_BASE_URL`.
- Avatar artwork lives in `public/avatar/`, one image per mood state.
