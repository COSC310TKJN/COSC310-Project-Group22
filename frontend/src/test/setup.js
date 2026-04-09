import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";

function createStorageMock() {
  let store = {};
  return {
    getItem: (key) => (key in store ? store[key] : null),
    setItem: (key, value) => {
      store[key] = String(value);
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
}

if (
  typeof window !== "undefined" &&
  (!window.localStorage || typeof window.localStorage.setItem !== "function")
) {
  Object.defineProperty(window, "localStorage", {
    value: createStorageMock(),
    writable: true,
  });
}

if (typeof globalThis !== "undefined" && typeof globalThis.localStorage?.setItem !== "function") {
  globalThis.localStorage = window.localStorage;
}

if (
  typeof window !== "undefined" &&
  (!window.sessionStorage || typeof window.sessionStorage.setItem !== "function")
) {
  Object.defineProperty(window, "sessionStorage", {
    value: createStorageMock(),
    writable: true,
  });
}

if (typeof globalThis !== "undefined" && typeof globalThis.sessionStorage?.setItem !== "function") {
  globalThis.sessionStorage = window.sessionStorage;
}

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  window.localStorage?.clear?.();
  window.sessionStorage?.clear?.();
});
afterAll(() => server.close());
