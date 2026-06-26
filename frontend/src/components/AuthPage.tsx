import { useEffect, useState } from "react";
import { requestOTP, verifyOTP, googleCallback, facebookCallback, appleCallback, googleLoginUrl } from "../auth_api";
import type { AuthToken, User } from "../types";
import "./AuthPage.css";

interface Props {
  onAuthSuccess: (token: string, user: User) => void;
}

type OTPMode = "email" | "phone";
type AuthStep = "social" | "otp-request" | "otp-verify";

export function AuthPage({ onAuthSuccess }: Props) {
  const [step, setStep] = useState<AuthStep>("social");
  const [otpMode, setOtpMode] = useState<OTPMode>("email");
  const [input, setInput] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [testOTP, setTestOTP] = useState<string>("");

  const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isValidPhone = (phone: string) => /^[+]?[\d\s\-()]+$/.test(phone) && phone.length >= 10;

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const state = params.get("state") ?? undefined;

    if (!code) {
      return;
    }

    const oauthCode = code;

    async function finishGoogleLogin() {
      setLoading(true);
      setError("");
      try {
        const response = await googleCallback(oauthCode, state);
        onAuthSuccess(response.access_token, response.user);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Google login failed");
      } finally {
        setLoading(false);
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
      }
    }

    void finishGoogleLogin();
  }, [onAuthSuccess]);

  async function handleSocialAuth(provider: "google" | "facebook" | "apple") {
    setLoading(true);
    setError("");
    try {
      let response: AuthToken;

      if (provider === "google") {
        const oauthUrl = await googleLoginUrl();
        window.location.assign(oauthUrl);
        return;
      } else if (provider === "facebook") {
        // Placeholder until full provider integration is added.
        const code = `${provider}_auth_code_${Date.now()}`;
        response = await facebookCallback(code);
      } else {
        // Placeholder until full provider integration is added.
        const code = `${provider}_auth_code_${Date.now()}`;
        response = await appleCallback(code);
      }

      onAuthSuccess(response.access_token, response.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "OAuth failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleOTPRequest(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const isEmail = otpMode === "email";
    if ((isEmail && !isValidEmail(input)) || (!isEmail && !isValidPhone(input))) {
      setError(isEmail ? "Please enter a valid email" : "Please enter a valid phone");
      setLoading(false);
      return;
    }

    try {
      const result = await requestOTP(isEmail ? input : undefined, !isEmail ? input : undefined);
      setTestOTP(result.code_for_testing || "");
      setStep("otp-verify");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  }

  async function handleOTPVerify(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (otp.length !== 6 || !/^\d+$/.test(otp)) {
      setError("Please enter a 6-digit code");
      setLoading(false);
      return;
    }

    try {
      const isEmail = otpMode === "email";
      const response = await verifyOTP(otp, isEmail ? input : undefined, !isEmail ? input : undefined);
      onAuthSuccess(response.access_token, response.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid OTP");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <header className="auth-header">
            <h1>Welcome to Collaborative Todo</h1>
            <p>Sign up to get started</p>
          </header>

          {step === "social" && (
            <div className="auth-section">
              <h2 className="section-title">Quick Sign Up</h2>
              <div className="social-buttons">
                <button
                  className="social-btn google-btn"
                  onClick={() => handleSocialAuth("google")}
                  disabled={loading}
                  aria-label="Continue with Google"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Continue with Google
                </button>

                <button
                  className="social-btn facebook-btn"
                  onClick={() => handleSocialAuth("facebook")}
                  disabled={loading}
                  aria-label="Continue with Facebook"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="#1877F2">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  Continue with Facebook
                </button>

                <button
                  className="social-btn apple-btn"
                  onClick={() => handleSocialAuth("apple")}
                  disabled={loading}
                  aria-label="Sign in with Apple"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.01 2.29.66 3.06.66.87 0 2.33-.87 3.95-.76 1.63.12 2.84.65 3.19 1.63-.06.04-2.18 1.16-2.13 3.44.05 2.85 2.46 3.78 2.48 3.84-.04.04-.68 1.56-2.26 2.92"/>
                    <path d="M12.03 7.25c-.15-1.48.27-2.74 1.13-3.65.68-.76 1.84-1.34 2.65-1.25.1 1.52-.36 2.74-1.13 3.65-.81.88-2.02 1.44-2.65 1.25"/>
                  </svg>
                  Sign in with Apple
                </button>
              </div>

              <div className="divider">
                <span>or</span>
              </div>

              <button
                className="btn btn-secondary btn-full"
                onClick={() => setStep("otp-request")}
              >
                Sign up with Email or Phone
              </button>
            </div>
          )}

          {step === "otp-request" && (
            <form onSubmit={handleOTPRequest} className="auth-section">
              <button
                type="button"
                className="back-btn"
                onClick={() => {
                  setStep("social");
                  setError("");
                  setInput("");
                }}
              >
                ← Back
              </button>

              <h2 className="section-title">Sign up with OTP</h2>

              <div className="otp-mode-tabs">
                <button
                  type="button"
                  className={`tab ${otpMode === "email" ? "active" : ""}`}
                  onClick={() => {
                    setOtpMode("email");
                    setInput("");
                    setError("");
                  }}
                >
                  Email
                </button>
                <button
                  type="button"
                  className={`tab ${otpMode === "phone" ? "active" : ""}`}
                  onClick={() => {
                    setOtpMode("phone");
                    setInput("");
                    setError("");
                  }}
                >
                  Phone
                </button>
              </div>

              <div className="form-group">
                <label htmlFor="otp-input" className="form-label">
                  {otpMode === "email" ? "Email Address" : "Phone Number"}
                </label>
                <input
                  id="otp-input"
                  type={otpMode === "email" ? "email" : "tel"}
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value);
                    setError("");
                  }}
                  placeholder={otpMode === "email" ? "you@example.com" : "+1 (555) 123-4567"}
                  disabled={loading}
                />
              </div>

              {error && <div className="alert alert-error">{error}</div>}

              <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? "Sending OTP..." : "Send OTP"}
              </button>
            </form>
          )}

          {step === "otp-verify" && (
            <form onSubmit={handleOTPVerify} className="auth-section">
              <button
                type="button"
                className="back-btn"
                onClick={() => {
                  setStep("otp-request");
                  setError("");
                  setOtp("");
                  setTestOTP("");
                }}
              >
                ← Back
              </button>

              <h2 className="section-title">Enter OTP</h2>
              <p className="hint-text">
                We sent a 6-digit code to {otpMode === "email" ? "your email" : "your phone"}. It expires in 120 seconds.
              </p>

              <div className="form-group">
                <label htmlFor="otp-code" className="form-label">
                  6-Digit Code
                </label>
                <input
                  id="otp-code"
                  type="text"
                  inputMode="numeric"
                  value={otp}
                  onChange={(e) => {
                    const val = e.target.value.replace(/\D/g, "").slice(0, 6);
                    setOtp(val);
                    setError("");
                  }}
                  placeholder="000000"
                  maxLength={6}
                  disabled={loading}
                  className="otp-input"
                />
              </div>

              {testOTP && (
                <div className="alert alert-info">
                  <strong>Test OTP (dev):</strong> {testOTP}
                </div>
              )}

              {error && <div className="alert alert-error">{error}</div>}

              <button type="submit" className="btn btn-primary btn-full" disabled={loading || otp.length !== 6}>
                {loading ? "Verifying..." : "Verify & Sign Up"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
