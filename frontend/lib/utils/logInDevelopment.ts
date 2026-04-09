export function logInDevelopment(logFn: () => void): void {
  if (process.env.NODE_ENV === "development") {
    logFn();
  }
}
