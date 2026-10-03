import React, { createContext, useContext, useState, useEffect } from "react";
import { setAuthTokenGetter } from "../api/client";
import { authApi } from "../api/auth";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // Initialize state from localStorage
  const [token, setToken] = useState(() => localStorage.getItem("auth_token"));
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("auth_user");
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(false);

  // Sync token to localStorage and Axios client
  useEffect(() => {
    if (token) {
      localStorage.setItem("auth_token", token);
    } else {
      localStorage.removeItem("auth_token");
    }
    setAuthTokenGetter(() => token);
  }, [token]);

  // Sync user to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem("auth_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("auth_user");
    }
  }, [user]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await authApi.login(email, password);
      setToken(data.access_token);
      setAuthTokenGetter(() => data.access_token);

      const profile = await authApi.getMe();
      const userData = {
        ...profile,
        role: data.role || profile.role,
      };
      setUser(userData);
      return { token: data.access_token, role: userData.role, user: profile };
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
      const userData = {
        ...profile,
        role: "admin",
      };
      setUser(userData);
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
      const userData = {
        ...profile,
        health_code: data.health_code,
        role: "patient",
      };
      setUser(userData);
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
      const userData = {
        ...profile,
        professional_code: data.professional_code,
        verification_status: data.verification_status,
        role: "healthcare_professional",
      };
      setUser(userData);
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
