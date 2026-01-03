import React, { createContext, useState, useEffect, useContext } from 'react'
import axios from 'axios'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUserProfile()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/accounts/users/profile/')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/token/', {
        username,
        password,
      })
      const { access, refresh } = response.data
      localStorage.setItem('token', access)
      localStorage.setItem('refresh_token', refresh)
      setToken(access)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
      await fetchUserProfile()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    delete axios.defaults.headers.common['Authorization']
    setToken(null)
    setUser(null)
  }

  const isAdmin = () => user?.role_name === 'admin'
  const isBaseCommander = () => user?.role_name === 'base_commander'
  const isLogisticsOfficer = () => user?.role_name === 'logistics_officer'

  const value = {
    user,
    loading,
    login,
    logout,
    isAdmin,
    isBaseCommander,
    isLogisticsOfficer,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


