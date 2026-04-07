import { describe, expect, it } from "vitest";

import {
  VALIDATE_TOKEN_CALLER_HEADER,
  buildValidateTokenRequestHeaders,
} from "./validateTokenBackendHeaders";

describe("buildValidateTokenRequestHeaders", () => {
  it("includes JSON content type and caller header for routeSession", () => {
    expect(buildValidateTokenRequestHeaders("routeSession")).toEqual({
      "Content-Type": "application/json",
      [VALIDATE_TOKEN_CALLER_HEADER]: "routeSession",
    });
  });

  it("includes syncCookie caller", () => {
    expect(buildValidateTokenRequestHeaders("syncCookie")).toEqual({
      "Content-Type": "application/json",
      [VALIDATE_TOKEN_CALLER_HEADER]: "syncCookie",
    });
  });
});
