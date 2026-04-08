import { createContext, useContext, useState } from "react";
import { api } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  async function login(username, password) {
    const data = await api.post("/auth/login", { username, password });
    const userData = { id: data.id, username: data.username, role: data.role, is_manager: data.is_manager };
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
    return userData;
  }

  async function register(username, password, role = "user") {
    const data = await api.post("/auth/register", { username, password, role });
    return data;
  }

  async function logout() {
    try {
      await api.post("/auth/logout");
    } catch {
      // session may already be gone
    }
    localStorage.removeItem("user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
