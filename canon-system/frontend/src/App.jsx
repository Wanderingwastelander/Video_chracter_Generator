import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Characters from './pages/Characters'
import CharacterDetail from './pages/CharacterDetail'
import CreateCharacter from './pages/CreateCharacter'
import ApprovalQueue from './pages/ApprovalQueue'
import Environments from './pages/Environments'
import Settings from './pages/Settings'

function App() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/characters', label: 'Characters' },
    { path: '/approval', label: 'Approval Queue' },
    { path: '/environments', label: 'Environments' },
    { path: '/settings', label: 'Settings' },
  ]
  
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <nav className="w-64 bg-gray-800 p-4 flex flex-col">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-blue-400">Canon System</h1>
          <p className="text-sm text-gray-500">v1.1.0</p>
        </div>
        
        <ul className="space-y-2 flex-1">
          {navItems.map(item => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`block px-4 py-2 rounded transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
        
        <div className="text-xs text-gray-600 mt-4">
          Character & Environment<br />
          Consistency System
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/characters" element={<Characters />} />
          <Route path="/characters/new" element={<CreateCharacter />} />
          <Route path="/characters/:id" element={<CharacterDetail />} />
          <Route path="/approval" element={<ApprovalQueue />} />
          <Route path="/environments" element={<Environments />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
