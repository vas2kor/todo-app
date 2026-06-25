import type { AuthToken } from "./types";

const API_BASE = "";

export async function requestOTP(email?: string, phone?: string): Promise<{ code_for_testing?: string }> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/v1/auth/otp/request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, phone }),
    });
  } catch {
    throw new Error("Cannot reach server. Make sure the backend is running on port 8000.");
  }

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail?.detail || "Failed to request OTP");
  }
  return response.json();
}

export async function verifyOTP(code: string, email?: string, phone?: string): Promise<AuthToken> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/v1/auth/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, email, phone }),
    });
  } catch {
    throw new Error("Cannot reach server. Make sure the backend is running on port 8000.");
  }

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail?.detail || "Invalid or expired OTP");
  }
  return response.json();
}

export async function googleCallback(code: string): Promise<AuthToken> {
  const response = await fetch(`${API_BASE}/api/v1/auth/google/callback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    throw new Error("Google login failed");
  }
  return response.json();
}

export async function facebookCallback(code: string): Promise<AuthToken> {
  const response = await fetch(`${API_BASE}/api/v1/auth/facebook/callback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    throw new Error("Facebook login failed");
  }
  return response.json();
}

export async function appleCallback(code: string): Promise<AuthToken> {
  const response = await fetch(`${API_BASE}/api/v1/auth/apple/callback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    throw new Error("Apple login failed");
  }
  return response.json();
}
