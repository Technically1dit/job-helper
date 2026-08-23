import { Outlet, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogOut, User, Briefcase, LayoutDashboard, Mail, FileText, Menu, X } from 'lucide-react'
import { useState } from 'react'

const Layout = () => {
    const { logout } = useAuth()
    const [open, setOpen] = useState(false)
    const navItems = [
        ['/', 'Dashboard', LayoutDashboard], ['/jobs', 'Jobs', Briefcase], ['/applications', 'Applications', FileText], ['/profile', 'Profile', User], ['/gmail', 'Gmail', Mail]
    ]
    const navClass = ({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'}`

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900">
            <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white p-4 transition-transform lg:translate-x-0`}>
                <div className="mb-8 flex items-center justify-between px-2"><NavLink to="/" className="flex items-center gap-2 text-lg font-bold tracking-tight text-slate-900"><span className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-sm text-white">J</span>JobPilot</NavLink><button onClick={() => setOpen(false)} className="rounded-lg p-2 text-slate-500 lg:hidden"><X size={19}/></button></div>
                
                <nav className="flex-1 space-y-1">
                    {navItems.map(([to, label, Icon]) => <NavLink end={to === '/'} key={to} to={to} onClick={() => setOpen(false)} className={navClass}><Icon size={18}/>{label}</NavLink>)}
                </nav>
                
                <button onClick={logout} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-rose-600 transition hover:bg-rose-50">
                    <LogOut size={18} /> Logout
                </button>
            </aside>
            {open && <button aria-label="Close navigation" onClick={() => setOpen(false)} className="fixed inset-0 z-30 bg-slate-950/30 lg:hidden" />}

            <div className="min-h-screen lg:pl-72">
                <header className="sticky top-0 z-20 flex h-16 items-center border-b border-slate-200 bg-white/85 px-5 backdrop-blur lg:px-10">
                    <button onClick={() => setOpen(true)} className="mr-3 rounded-lg p-2 text-slate-600 lg:hidden"><Menu size={21}/></button>
                    <p className="text-sm font-medium text-slate-500">Your career workspace</p>
                </header>
                <main className="p-5 sm:p-8 lg:p-10">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

export default Layout
