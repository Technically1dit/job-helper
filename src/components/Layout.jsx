import { Outlet, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogOut, User, Briefcase, LayoutDashboard, Mail, FileText, Bell } from 'lucide-react'

const Layout = () => {
    const { logout } = useAuth()

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <div className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col">
                <div className="text-xl font-bold text-blue-600 mb-8 px-4">JobHunter AI</div>
                
                <nav className="flex-1 space-y-2">
                    <Link to="/" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg">
                        <LayoutDashboard size={20} /> Dashboard
                    </Link>
                    <Link to="/jobs" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg">
                        <Briefcase size={20} /> Search Jobs
                    </Link>
                    <Link to="/applications" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg">
                        <FileText size={20} /> Applications
                    </Link>
                    <Link to="/profile" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg">
                        <User size={20} /> Profile
                    </Link>
                    <Link to="/gmail" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg">
                        <Mail size={20} /> Gmail Settings
                    </Link>
                </nav>
                
                <button onClick={logout} className="flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg w-full">
                    <LogOut size={20} /> Logout
                </button>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
                    <h1 className="text-xl font-semibold text-gray-800">JobHunter AI</h1>
                    <div className="flex items-center gap-4">
                        <button className="p-2 text-gray-400 hover:text-blue-600 rounded-full hover:bg-blue-50">
                            <Bell size={20} />
                        </button>
                    </div>
                </header>
                <main className="flex-1 overflow-y-auto p-8 bg-gray-50">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

export default Layout
