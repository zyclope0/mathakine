import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getLocalString,
  getSessionString,
  readSessionJson,
  removeLocalKey,
  setLocalString,
  writeSessionJson,
} from "./browser-storage";

describe("browser-storage", () => {
  afterEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("getLocalString returns null when getItem throws", () => {
    vi.spyOn(window.localStorage, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(getLocalString("k")).toBeNull();
  });

  it("fails closed when localStorage access itself throws", () => {
    const originalWindow = window;
    const fakeWindow = Object.create(originalWindow) as Window;
    Object.defineProperty(fakeWindow, "localStorage", {
      configurable: true,
      get() {
        throw new Error("SecurityError");
      },
    });
    vi.stubGlobal("window", fakeWindow);

    expect(getLocalString("k")).toBeNull();
  });

  it("setLocalString swallows setItem errors", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("quota");
    });
    expect(() => setLocalString("k", "v")).not.toThrow();
  });

  it("removeLocalKey swallows removeItem errors", () => {
    vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    expect(() => removeLocalKey("k")).not.toThrow();
  });

  it("readSessionJson returns null for invalid JSON", () => {
    sessionStorage.setItem("x", "not-json");
    expect(readSessionJson("x")).toBeNull();
  });

  it("fails closed when sessionStorage access itself throws", () => {
    const originalWindow = window;
    const fakeWindow = Object.create(originalWindow) as Window;
    Object.defineProperty(fakeWindow, "sessionStorage", {
      configurable: true,
      get() {
        throw new Error("SecurityError");
      },
    });
    vi.stubGlobal("window", fakeWindow);

    expect(getSessionString("x")).toBeNull();
  });

  it("readSessionJson round-trips writeSessionJson", () => {
    writeSessionJson("obj", { a: 1, nested: { b: "c" } });
    expect(readSessionJson("obj")).toEqual({ a: 1, nested: { b: "c" } });
  });
});
