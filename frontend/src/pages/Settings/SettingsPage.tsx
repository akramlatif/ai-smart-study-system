import React from 'react'
import { Card } from '../../components/ui/Card'
import { useUIStore } from '../../store/uiStore'
import { Moon, Sun, Monitor, Bell, Shield, Key } from 'lucide-react'

export function SettingsPage() {
  const { theme, toggleTheme } = useUIStore()

  return (
    <div className="p-6 max-w-4xl mx-auto dark:bg-slate-950 transition-colors h-full overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">Settings</h1>
        <p className="text-gray-500 dark:text-slate-400 mt-2">Manage your account and preferences.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Navigation Sidebar */}
        <div className="col-span-1 flex flex-col gap-1">
          <button className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400 font-medium transition-colors text-left">
            <Monitor className="w-4 h-4" />
            Appearance
          </button>
          <button className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-600 dark:text-slate-400 hover:bg-gray-50 dark:hover:bg-slate-900 font-medium transition-colors text-left">
            <Bell className="w-4 h-4" />
            Notifications
          </button>
          <button className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-600 dark:text-slate-400 hover:bg-gray-50 dark:hover:bg-slate-900 font-medium transition-colors text-left">
            <Shield className="w-4 h-4" />
            Privacy
          </button>
          <button className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-600 dark:text-slate-400 hover:bg-gray-50 dark:hover:bg-slate-900 font-medium transition-colors text-left">
            <Key className="w-4 h-4" />
            Account
          </button>
        </div>

        {/* Content Area */}
        <div className="col-span-1 md:col-span-2 flex flex-col gap-6">
          
          <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Appearance</h2>
            <div className="flex items-center justify-between py-4 border-b border-gray-100 dark:border-slate-800">
              <div>
                <p className="font-medium text-gray-900 dark:text-slate-200">Dark Mode</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">Toggle between light and dark themes.</p>
              </div>
              <button
                onClick={toggleTheme}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900 ${
                  theme === 'dark' ? 'bg-primary-600' : 'bg-gray-200 dark:bg-slate-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            
            <div className="flex gap-4 mt-6">
              <button 
                onClick={() => theme === 'dark' && toggleTheme()}
                className={`flex-1 p-4 border rounded-xl flex flex-col items-center gap-3 transition-all ${
                theme === 'light' 
                  ? 'border-primary-500 bg-primary-50 text-primary-700' 
                  : 'border-gray-200 dark:border-slate-700 text-gray-500 dark:text-slate-400 hover:border-gray-300 dark:hover:border-slate-600'
              }`}>
                <Sun className="w-6 h-6" />
                <span className="font-medium">Light</span>
              </button>
              <button 
                onClick={() => theme === 'light' && toggleTheme()}
                className={`flex-1 p-4 border rounded-xl flex flex-col items-center gap-3 transition-all ${
                theme === 'dark' 
                  ? 'border-primary-500 bg-primary-900/20 text-primary-400' 
                  : 'border-gray-200 dark:border-slate-700 text-gray-500 dark:text-slate-400 hover:border-gray-300 dark:hover:border-slate-600'
              }`}>
                <Moon className="w-6 h-6" />
                <span className="font-medium">Dark</span>
              </button>
            </div>
          </Card>

          <Card className="p-6 dark:bg-slate-900 dark:border-slate-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-4">Study Preferences</h2>
            <div className="flex items-center justify-between py-4 border-b border-gray-100 dark:border-slate-800">
              <div>
                <p className="font-medium text-gray-900 dark:text-slate-200">Strict Quiz Mode</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">Require exact matches for fill-in-the-blank answers.</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 dark:bg-slate-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-1" />
              </button>
            </div>
            <div className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium text-gray-900 dark:text-slate-200">Daily Study Reminders</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">Receive email notifications for scheduled study time.</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-6" />
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
