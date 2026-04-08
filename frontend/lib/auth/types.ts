/**
 * Frontend auth contracts (FFI-L20C) — shared payloads/responses for useAuth and API glue.
 */
import type { User } from "@/types/api";

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

/** Login/token endpoint JSON body (access mirrored to frontend cookie when needed). */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  csrf_token?: string;
  user: User;
}

export interface ForgotPasswordData {
  email: string;
}

/** Resolved strings for login error toast description (from next-intl in the hook). */
export interface LoginErrorToastLabels {
  loginForbidden: string;
  loginInvalidCredentials: string;
  loginInvalidRequest: string;
  loginServerError: string;
  loginError: string;
}
