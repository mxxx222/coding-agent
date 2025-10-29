import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string
  plan: 'free' | 'pro' | 'enterprise'
}

interface AppState {
  user: User | null
  isAuthenticated: boolean
  theme: 'light' | 'dark'
  sidebarOpen: boolean

  // Actions
  setUser: (user: User | null) => void
  setTheme: (theme: 'light' | 'dark') => void
  toggleSidebar: () => void
  logout: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, _get) => ({
      user: null,
      isAuthenticated: false,
      theme: 'light',
      sidebarOpen: false,

      setUser: user =>
        set({
          user,
          isAuthenticated: !!user,
        }),

      setTheme: theme => set({ theme }),

      toggleSidebar: () =>
        set(state => ({
          sidebarOpen: !state.sidebarOpen,
        })),

      logout: () =>
        set({
          user: null,
          isAuthenticated: false,
          sidebarOpen: false,
        }),
    }),
    {
      name: 'coding-agent-store',
      partialize: state => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
)

// Selectors for better performance
export const useUser = () => useAppStore(state => state.user)
export const useIsAuthenticated = () => useAppStore(state => state.isAuthenticated)
export const useTheme = () => useAppStore(state => state.theme)
export const useSidebarOpen = () => useAppStore(state => state.sidebarOpen)
