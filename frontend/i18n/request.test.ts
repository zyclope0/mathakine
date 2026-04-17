import { beforeEach, describe, expect, it, vi } from "vitest";

const cookiesMock = vi.fn();
const headersMock = vi.fn();

vi.mock("next/headers", () => ({
  cookies: cookiesMock,
  headers: headersMock,
}));

vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("notFound");
  }),
}));

vi.mock("next-intl/server", () => ({
  getRequestConfig: (factory: unknown) => factory,
}));

describe("i18n request config", () => {
  beforeEach(() => {
    cookiesMock.mockReset();
    headersMock.mockReset();
  });

  it("uses Accept-Language when no locale param or cookie exists", async () => {
    cookiesMock.mockResolvedValue({
      get: () => undefined,
    });
    headersMock.mockResolvedValue({
      get: (key: string) => (key === "accept-language" ? "en-US,en;q=0.9" : null),
    });

    const requestConfigModule = await import("@/i18n/request");
    const requestConfig = requestConfigModule.default as (args: {
      locale?: string;
    }) => Promise<{ locale: string }>;

    const config = await requestConfig({});

    expect(config.locale).toBe("en");
  });

  it("keeps explicit route locale precedence when provided", async () => {
    cookiesMock.mockResolvedValue({
      get: () => ({ value: "fr" }),
    });
    headersMock.mockResolvedValue({
      get: () => "en-US,en;q=0.9",
    });

    const requestConfigModule = await import("@/i18n/request");
    const requestConfig = requestConfigModule.default as (args: {
      locale?: string;
    }) => Promise<{ locale: string }>;

    const config = await requestConfig({ locale: "en" });

    expect(config.locale).toBe("en");
  });
});
