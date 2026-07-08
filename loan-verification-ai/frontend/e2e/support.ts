/**
 * Backend API helpers for E2E test *setup* — registering users, creating and
 * submitting applications, seeding upload artifacts. Deliberately done via
 * direct fetch calls rather than driving the browser: setup isn't what these
 * tests are verifying, and going through the UI for every fixture would make
 * the suite slow and brittle (see the "make it fast" lesson in
 * docs/phase-11-officer-dashboard.md — the same principle applies here).
 */

export const BACKEND_API_BASE_URL =
  process.env.BACKEND_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export const SEEDED_OFFICER_EMAIL = "officer@verifyco.bank";
export const SEEDED_OFFICER_PASSWORD = "OfficerDemo123!";

interface TokenPair {
  access_token: string;
  refresh_token: string;
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BACKEND_API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`${init?.method ?? "GET"} ${path} -> ${response.status}: ${await response.text()}`);
  }
  return (await response.json()) as T;
}

export async function registerApplicant(email: string): Promise<TokenPair> {
  return api<TokenPair>("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      email,
      password: "Str0ngPass!234",
      full_name: "E2E Applicant",
      role: "applicant",
    }),
  });
}

export async function loginOfficer(): Promise<TokenPair> {
  return api<TokenPair>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email: SEEDED_OFFICER_EMAIL, password: SEEDED_OFFICER_PASSWORD }),
  });
}

interface ArtifactSpec {
  kind: "applicant_photo" | "coapplicant_photo" | "verification_video";
  contentType: string;
  filename: string;
  bytes: ArrayBuffer;
}

function filledBuffer(size: number, value: number): ArrayBuffer {
  const buffer = new ArrayBuffer(size);
  new Uint8Array(buffer).fill(value);
  return buffer;
}

const ARTIFACT_SPECS: ArtifactSpec[] = [
  {
    kind: "applicant_photo",
    contentType: "image/jpeg",
    filename: "applicant.jpg",
    bytes: filledBuffer(2048, 1),
  },
  {
    kind: "coapplicant_photo",
    contentType: "image/jpeg",
    filename: "coapplicant.jpg",
    bytes: filledBuffer(2048, 2),
  },
  {
    kind: "verification_video",
    contentType: "video/mp4",
    filename: "video.mp4",
    bytes: filledBuffer(8192, 3),
  },
];

/** Creates, uploads all three required artifacts for, and submits an
 * application — the full setup an officer-review or reports test needs,
 * without ever touching the browser. */
export async function createSubmittedApplication(accessToken: string): Promise<string> {
  const auth = { Authorization: `Bearer ${accessToken}` };

  const app = await api<{ id: string }>("/applications", {
    method: "POST",
    headers: auth,
    body: JSON.stringify({
      loan_amount: 1800000,
      loan_purpose: "E2E verification",
      co_applicant: { full_name: "E2E Co-Applicant", relationship: "sibling", phone: "+919876500000" },
    }),
  });

  for (const spec of ARTIFACT_SPECS) {
    const init = await api<{ artifact_id: string; upload_url: string }>(
      `/applications/${app.id}/uploads/init`,
      {
        method: "POST",
        headers: auth,
        body: JSON.stringify({
          kind: spec.kind,
          content_type: spec.contentType,
          filename: spec.filename,
        }),
      },
    );
    const put = await fetch(init.upload_url, {
      method: "PUT",
      headers: { "Content-Type": spec.contentType },
      body: spec.bytes,
    });
    if (!put.ok) throw new Error(`PUT upload for ${spec.kind} -> ${put.status}`);

    await api(`/applications/${app.id}/uploads/confirm`, {
      method: "POST",
      headers: auth,
      body: JSON.stringify({ artifact_id: init.artifact_id }),
    });
  }

  await api(`/applications/${app.id}/submit`, { method: "POST", headers: auth });
  return app.id;
}

/** Polls the application until the (real, live) AI pipeline has moved it to
 * `pending_review` — requires an actual Celery worker consuming the queue,
 * exactly like this project's manual Phase 9-12 verification passes. */
export async function waitForPendingReview(
  accessToken: string,
  applicationId: string,
  timeoutMs = 60_000,
): Promise<void> {
  const auth = { Authorization: `Bearer ${accessToken}` };
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const app = await api<{ status: string }>(`/applications/${applicationId}`, { headers: auth });
    if (app.status === "pending_review") return;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error(`Application ${applicationId} did not reach pending_review within ${timeoutMs}ms`);
}
