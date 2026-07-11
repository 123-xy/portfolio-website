import type { CapacitorConfig } from "@capacitor/cli";

// The VerifyCo web app is API-backed with server-rendered dynamic routes
// (e.g. /review/[id]), so it is NOT a static bundle Capacitor can ship offline.
// Instead the native Android shell is a WebView that loads the running web app.
//
// Point it at wherever the frontend is served, via CAP_SERVER_URL, before
// running `npx cap sync`:
//   - Android emulator -> host machine:  http://10.0.2.2:3000
//   - Physical device on the same Wi-Fi:  http://<your-LAN-IP>:3000
//   - A deployed environment:             https://app.your-domain.com
//
// With no CAP_SERVER_URL set, the app loads the bundled offline fallback page
// in `mobile/www` (a "configure the server" splash) so the project still
// builds and runs in Android Studio out of the box.
const serverUrl = process.env.CAP_SERVER_URL?.trim();

const config: CapacitorConfig = {
  appId: "com.verifyco.app",
  appName: "VerifyCo",
  webDir: "mobile/www",
  ...(serverUrl
    ? {
        server: {
          url: serverUrl,
          // Plain http (LAN/emulator dev) needs cleartext; https does not.
          cleartext: serverUrl.startsWith("http://"),
        },
      }
    : {}),
};

export default config;
