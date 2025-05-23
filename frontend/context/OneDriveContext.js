import React, { createContext, useContext, useState, useEffect } from 'react';

const OneDriveContext = createContext();

export function OneDriveProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userToken, setUserToken] = useState(null);

  useEffect(() => {
    // ⭐ CARICA TOKEN DA LOCALSTORAGE ALL'AVVIO
    const savedToken = localStorage.getItem('onedrive_user_token');
    const savedUserId = localStorage.getItem('onedrive_user_id');
    
    if (savedToken && savedUserId) {
      setUserToken(savedToken);
      setIsAuthenticated(true);
      console.log('✅ Token caricato da localStorage');
    }
    
    checkAuthStatus();

    // ⭐ GESTIONE CALLBACK DA URL
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get('onedrive_auth');
    const userId = urlParams.get('user_id');
    const token = urlParams.get('token');
    
    if (authStatus === 'success' && userId) {
      console.log('✅ Autenticazione completata via URL');
      
      // ⭐ SALVA TOKEN E USER_ID
      localStorage.setItem('onedrive_user_id', userId);
      if (token) {
        localStorage.setItem('onedrive_user_token', token);
        setUserToken(token);
      }
      
      setIsAuthenticated(true);
      setError(null);
      
      // Pulisci URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authStatus === 'error') {
      const errorMsg = urlParams.get('message') || 'Errore sconosciuto';
      setError(`Errore autenticazione: ${errorMsg.replace(/_/g, ' ')}`);
      setIsAuthenticated(false);
    }

    setIsLoading(false);
  }, []);

  /**
   * ⭐ CHECK STATUS CON HEADERS
   */
  const checkAuthStatus = async () => {
    try {
      const savedUserId = localStorage.getItem('onedrive_user_id');
      if (!savedUserId) {
        setIsAuthenticated(false);
        return;
      }

      console.log('🔍 Test auth status con header...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}/onedrive/auth/status`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${savedUserId}`,
          'X-OneDrive-User-ID': savedUserId,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setIsAuthenticated(data.authenticated || false);
        console.log('✅ Auth status verificato:', data.authenticated);
      } else {
        setIsAuthenticated(false);
        console.log('❌ Auth status check fallito');
      }
      
    } catch (err) {
      console.error('❌ Errore check auth:', err);
      setIsAuthenticated(false);
    }
  };

  /**
   * ⭐ UPLOAD CON HEADERS
   */
  const uploadToOneDrive = async (endpoint) => {
    const savedUserId = localStorage.getItem('onedrive_user_id');
    
    if (!savedUserId || !isAuthenticated) {
      console.log('❌ Non autenticato, avvio autenticazione...');
      startAuthentication();
      return { success: false, needsAuth: true };
    }

    try {
      console.log(`📤 Upload su OneDrive: ${endpoint}`);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${savedUserId}`,
          'X-OneDrive-User-ID': savedUserId,
          'Accept': 'application/json'
        }
      });
      
      console.log(`📡 Upload response: ${response.status}`);
      
      if (response.status === 401) {
        console.log('🔄 Token scaduto, riavvio autenticazione...');
        localStorage.removeItem('onedrive_user_id');
        localStorage.removeItem('onedrive_user_token');
        setIsAuthenticated(false);
        startAuthentication();
        return { success: false, needsAuth: true };
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Errore durante il caricamento su OneDrive');
      }
      
      const result = await response.json();
      console.log('✅ Upload completato:', result);
      return result;
      
    } catch (err) {
      console.error('❌ Errore upload OneDrive:', err);
      throw err;
    }
  };

  /**
   * ⭐ TEST CONNECTION CON HEADERS
   */
  const testConnection = async () => {
    const savedUserId = localStorage.getItem('onedrive_user_id');
    
    try {
      console.log('🧪 Test connessione OneDrive...');
      
      const headers = {
        'Accept': 'application/json'
      };
      
      if (savedUserId) {
        headers['Authorization'] = `Bearer ${savedUserId}`;
        headers['X-OneDrive-User-ID'] = savedUserId;
      }
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BE_API_URL}/onedrive/test/connection`, {
        headers
      });
      
      const result = await response.json();
      console.log('🧪 Test result:', result);
      
      if (result.status === 'success') {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
      
      return result;
      
    } catch (err) {
      console.error('❌ Errore test connessione:', err);
      return { status: 'error', message: err.message };
    }
  };

  const startAuthentication = () => {
    console.log('🔐 Avvio autenticazione OneDrive...');
    window.location.href = `${process.env.NEXT_PUBLIC_BE_API_URL}/onedrive/auth`;
  };

  const logout = async () => {
    localStorage.removeItem('onedrive_user_id');
    localStorage.removeItem('onedrive_user_token');
    setUserToken(null);
    setIsAuthenticated(false);
    setError(null);
    console.log('✅ Logout completato');
  };

  const value = {
    isAuthenticated,
    isLoading,
    error,
    userToken,
    startAuthentication,
    logout,
    checkAuthStatus,
    uploadToOneDrive,
    testConnection
  };

  return (
    <OneDriveContext.Provider value={value}>
      {children}
    </OneDriveContext.Provider>
  );
}

export function useOneDrive() {
  const context = useContext(OneDriveContext);
  if (context === undefined) {
    throw new Error('useOneDrive deve essere usato all\'interno di un OneDriveProvider');
  }
  return context;
}