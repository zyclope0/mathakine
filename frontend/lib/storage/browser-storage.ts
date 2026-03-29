function canUseLocalStorage(): boolean {
  try {
    return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
  } catch {
    return false;
  }
}

function canUseSessionStorage(): boolean {
  try {
    return typeof window !== "undefined" && typeof window.sessionStorage !== "undefined";
  } catch {
    return false;
  }
}

/** True when `sessionStorage` can be touched (browser + API present). */
export function isSessionStorageAvailable(): boolean {
  return canUseSessionStorage();
}

export function getLocalString(key: string): string | null {
  if (!canUseLocalStorage()) return null;
  try {
    return localStorage.getItem(key) ?? null;
  } catch {
    return null;
  }
}

export function setLocalString(key: string, value: string): void {
  if (!canUseLocalStorage()) return;
  try {
    localStorage.setItem(key, value);
  } catch {
    /* quota / private mode */
  }
}

export function removeLocalKey(key: string): void {
  if (!canUseLocalStorage()) return;
  try {
    localStorage.removeItem(key);
  } catch {
    /* ignore */
  }
}

export function getSessionString(key: string): string | null {
  if (!canUseSessionStorage()) return null;
  try {
    return sessionStorage.getItem(key) ?? null;
  } catch {
    return null;
  }
}

export function setSessionString(key: string, value: string): void {
  if (!canUseSessionStorage()) return;
  try {
    sessionStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

export function removeSessionKey(key: string): void {
  if (!canUseSessionStorage()) return;
  try {
    sessionStorage.removeItem(key);
  } catch {
    /* ignore */
  }
}

/** Returns `null` if missing, invalid JSON, or storage throws. */
export function readSessionJson(key: string): unknown | null {
  const raw = getSessionString(key);
  if (raw === null) return null;
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return null;
  }
}

export function writeSessionJson(key: string, value: unknown): void {
  if (!canUseSessionStorage()) return;
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* ignore */
  }
}
