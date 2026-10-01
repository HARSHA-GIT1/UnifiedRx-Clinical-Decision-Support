import React, { createContext, useContext, useState, useEffect } from "react";
import { setAuthTokenGetter } from "../api/client";
import { authApi } from "../api/auth";

/**
 * SECURITY ARCHITECTURE NOTE:
 * JWT access tokens are stored strictly in React in-memory state.
 * By design, tokens are NEVER persisted to localStorage or sessionStorage
 * to completely eliminate persistent cross-site scripting (XSS) token exfiltration risks.
 *
 * An intentional tradeoff of this security boundary is that a hard browser refresh
 * terminates the in-memory React session and requires the user to log in again.
 */

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Register in-memory token getter for Axios client
  useEffect(() => {
    setAuthTokenGetter(() => token);
  }, [token]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await authApi.login(email, password);
      // Immediately set token in memory so subsequent /me call has Authorization header
      setToken(data.access_token);
      setAuthTokenGetter(() => data.access_token);

      // Fetch profile
      const profile = await authApi.getMe();
      setUser({
        ...profile,
        role: data.role || profile.role,
      });
      return { token: data.access_token, role: data.role || profile.role, user: profile };
    } finally {
      setLoading(false);
    }
  };

  const adminLogin = async (email, password) => {
    setLoading(true);
    try {
      const data = await authApi.adminLogin(email, password);
      setToken(data.access_token);
      setAuthTokenGetter(() => data.access_token);

      const profile = await authApi.getMe();
      setUser({
        ...profile,
        role: "admin",
      });
      return { token: data.access_token, role: "admin", user: profile };
    } finally {
      setLoading(false);
    }
  };

  const registerPatient = async (formData) => {
    setLoading(true);
    try {
      const data = await authApi.registerPatient(formData);
      setToken(data.access_token);
      setAuthTokenGetter(() => data.access_token);

      const profile = await authApi.getMe();
      setUser({
        ...profile,
        health_code: data.health_code,
        role: "patient",
      });
      return {
        health_code: data.health_code,
        token: data.access_token,
        role: "patient",
        full_name: data.full_name,
      };
    } finally {
      setLoading(false);
    }
  };

  const registerDoctor = async (formData) => {
    setLoading(true);
    try {
      const data = await authApi.registerDoctor(formData);
      setToken(data.access_token);
      setAuthTokenGetter(() => data.access_token);

      const profile = await authApi.getMe();
      setUser({
        ...profile,
        professional_code: data.professional_code,
        verification_status: data.verification_status,
        role: "healthcare_professional",
      });
      return {
        professional_code: data.professional_code,
        verification_status: data.verification_status,
        token: data.access_token,
        role: "healthcare_professional",
        full_name: data.full_name,
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setAuthTokenGetter(() => null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        isAuthenticated: !!token,
        login,
        adminLogin,
        registerPatient,
        registerDoctor,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
