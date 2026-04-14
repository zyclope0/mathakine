import { afterEach, describe, expect, it, vi } from "vitest";

import { getBackendUrl } from "./backendUrl";

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("getBackendUrl", () => {
  it("en développement, autorise le fallback localhost si aucune variable", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(getBackendUrl()).toBe("http://localhost:10000");
  });

  it("priorise NEXT_PUBLIC_API_BASE_URL sur NEXT_PUBLIC_API_URL", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://primary.example");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "https://legacy.example");
    expect(getBackendUrl()).toBe("https://primary.example");
  });

  it("utilise NEXT_PUBLIC_API_URL si BASE est vide", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "https://legacy-only.example");
    expect(getBackendUrl()).toBe("https://legacy-only.example");
  });

  it("ignore les valeurs uniquement espaces (traitées comme absentes)", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "   ");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "https://trim.example");
    expect(getBackendUrl()).toBe("https://trim.example");
  });

  it("en production, interdit localhost dans l’URL", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:10000");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(() => getBackendUrl()).toThrow(/localhost/i);
  });

  it("en production, erreur explicite si aucune URL valide", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(() => getBackendUrl()).toThrow(/NEXT_PUBLIC_API_BASE_URL/);
  });

  it("en production, accepte une URL HTTPS non locale", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.prod.example");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(getBackendUrl()).toBe("https://api.prod.example");
  });

  it("en production, interdit 127.0.0.1 (loopback non-literal localhost)", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://127.0.0.1:10000");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(() => getBackendUrl()).toThrow(/adresse locale/i);
  });

  it("en production, rejette une valeur non parsable comme URL", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "backend");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(() => getBackendUrl()).toThrow(/URL absolue valide/i);
  });

  it("en production, rejette une URL relative sans protocole", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "/api");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    expect(() => getBackendUrl()).toThrow(/URL absolue valide/i);
  });
});
