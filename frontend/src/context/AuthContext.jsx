import { createContext, useContext, useState } from "react";
import { useCallback, useEffect } from "react";
import { api } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  const clearAuth = useCallback(() => {
    localStorage.removeItem("user");
    setUser(null);
  }, []);

  useEffect(() => {
    function onExpired() {
      clearAuth();
    }
    window.addEventListener("auth:expired", onExpired);
    return () => window.removeEventListener("auth:expired", onExpired);
  }, [clearAuth]);

  async function login(username, password) {
    const data = await api.auth.login({ username, password });
    const userData = { id: data.id, username: data.username, role: data.role, is_manager: data.is_manager };
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
    await api.auth.portalUser();
    return userData;
  }

  async function register(username, password, role = "user") {
    const data = await api.auth.register({ username, password, role });
    return data;
  }

  async function logout() {
    try {
      await api.auth.logout();
    } catch {
      // session may already be gone
    }
    clearAuth();
  }

  async function verifyUserPortal() {
    await api.auth.portalUser();
    return true;
  }

  async function verifyManagerPortal() {
    await api.auth.portalManager();
    return true;
  }

  return (
    <AuthContext.Provider
      value={{ user, login, register, logout, clearAuth, verifyUserPortal, verifyManagerPortal }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
