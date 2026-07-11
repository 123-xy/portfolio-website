# VerifyCo — Android app (Capacitor wrapper)

The VerifyCo frontend is a Next.js web app with server-rendered, data-driven
routes (e.g. `/review/[id]`) and a live REST backend — it is **not** a static
bundle. So the Android app is a thin native **WebView shell** (Capacitor) that
loads the running web app from a URL you configure. This is the standard
Capacitor pattern for API-backed / SSR apps.

```
frontend/
  capacitor.config.ts     # appId, appName, and the server URL (from CAP_SERVER_URL)
  mobile/www/             # offline fallback splash (shown when no server is set)
  android/                # the native Android Studio project  ← open THIS
```

## Prerequisites (on your machine)

- **Android Studio** (Ladybug / 2024.2 or newer) with the Android SDK.
- **JDK 21** (bundled with recent Android Studio).
- **Node 20+** and the frontend deps installed (`npm install` in `frontend/`).
- The VerifyCo backend + frontend running and reachable — the mobile app is a
  window onto them, so they must be up. From the repo root:
  `cd loan-verification-ai && docker compose up --build`.

## The one thing that trips everyone up: networking

The phone/emulator is **not** your laptop, so `localhost` inside the app means
the device itself. Two URLs must be reachable *from the device*:

1. **The web app** the shell loads — `CAP_SERVER_URL` (below).
2. **The backend API** the web app calls — baked into the web build as
   `NEXT_PUBLIC_API_BASE_URL`.

Use a host the device can actually reach for **both**:

| Running on | Use this host for the machine |
|---|---|
| Android **emulator** | `10.0.2.2` (special alias for your machine's localhost) |
| Physical device (same Wi-Fi) | your machine's **LAN IP**, e.g. `192.168.1.20` |

So for the emulator, serve the frontend built against the same host the API is
on:

```bash
# in frontend/ — build & serve the web app with an API URL the device can reach
NEXT_PUBLIC_API_BASE_URL=http://10.0.2.2:8000/api/v1 npm run build
NEXT_PUBLIC_API_BASE_URL=http://10.0.2.2:8000/api/v1 npm run start   # serves :3000
```

(And make sure the backend/compose stack is listening on `0.0.0.0:8000`, which
the Docker stack already does, plus CORS allows the origin — set
`CORS_ORIGINS` to include `http://10.0.2.2:3000`.)

## Build & run in Android Studio

```bash
cd loan-verification-ai/frontend

# 1. Tell the shell where the web app is (emulator example)
export CAP_SERVER_URL=http://10.0.2.2:3000

# 2. Push config + web assets into the android project
npm run cap:sync          # = npx cap sync android

# 3. Open the native project in Android Studio
npm run cap:open          # = npx cap open android
#   (or just open the frontend/android/ folder from Android Studio directly)
```

Then in Android Studio: let Gradle sync finish (first sync downloads the
Android Gradle Plugin), pick an emulator or connected device, and press
**Run ▶**. The app launches and loads the VerifyCo web UI. Log in as the demo
officer (`officer@verifyco.bank` / `OfficerDemo123!`) or register as an
applicant.

To produce an installable artifact: **Build ▸ Build Bundle(s) / APK(s) ▸
Build APK(s)** (or `cd android && ./gradlew assembleDebug`).

## Re-syncing after changes

Any time you change `capacitor.config.ts`, `CAP_SERVER_URL`, or the fallback
in `mobile/www/`, re-run `npm run cap:sync` before rebuilding.

## Notes

- With **no** `CAP_SERVER_URL` set, the app builds and runs but shows the
  offline splash in `mobile/www/index.html` — proof the native shell works
  before you wire up a server.
- For a **production** app you'd point `CAP_SERVER_URL` at your deployed HTTPS
  domain (no cleartext needed) and ship a signed release build; app signing,
  icons/splash, and store metadata are the usual next steps and are out of
  scope for this scaffold.
- `android/` is committed so the project opens immediately. Its build outputs
  (`build/`, `.gradle/`, `local.properties`) are git-ignored by Capacitor's
  generated `android/.gitignore`.
