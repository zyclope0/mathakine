import { describe, expect, it } from "vitest";
import { ApiClientError } from "@/lib/api/client";
import {
  isAuthMeQueryUnauthenticatedError,
  resolveLoginErrorDescription,
} from "@/lib/auth/authLoginFlow";

const labels = {
  loginForbidden: "forbidden",
  loginInvalidCredentials: "badcreds",
  loginInvalidRequest: "badreq",
  loginServerError: "server",
  loginError: "generic",
};

describe("authLoginFlow", () => {
  it("detects 401 ApiClientError for auth me query", () => {
    expect(isAuthMeQueryUnauthenticatedError(new ApiClientError("x", 401))).toBe(true);
    expect(isAuthMeQueryUnauthenticatedError(new ApiClientError("x", 403))).toBe(false);
    expect(isAuthMeQueryUnauthenticatedError(new Error("x"))).toBe(false);
  });

  it("maps login error statuses to descriptions", () => {
    expect(resolveLoginErrorDescription(new ApiClientError("m403", 403), labels)).toBe("m403");
    expect(resolveLoginErrorDescription(new ApiClientError("", 403), labels)).toBe("forbidden");
    expect(resolveLoginErrorDescription(new ApiClientError("x", 401), labels)).toBe("badcreds");
    expect(resolveLoginErrorDescription(new ApiClientError("m400", 400), labels)).toBe("m400");
    expect(resolveLoginErrorDescription(new ApiClientError("", 500), labels)).toBe("server");
    expect(resolveLoginErrorDescription(new ApiClientError("m418", 418), labels)).toBe("m418");
  });
});
