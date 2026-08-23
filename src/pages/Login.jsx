import { useAuth } from '../context/AuthContext'
import { ArrowRight, BriefcaseBusiness, CheckCircle2, Sparkles } from 'lucide-react'

const Login = () => {
    const { login } = useAuth()
    
    return (
        <div className="relative grid min-h-screen place-items-center overflow-hidden bg-slate-950 px-5 py-10">
            <div className="absolute -left-24 top-0 h-96 w-96 rounded-full bg-indigo-600/30 blur-3xl" /><div className="absolute -right-24 bottom-0 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />
            <div className="relative grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/10 bg-white shadow-2xl md:grid-cols-[1.15fr_.85fr]">
              <div className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 p-8 text-white sm:p-12"><div className="mb-12 flex items-center gap-2 text-lg font-bold"><BriefcaseBusiness /> JobPilot</div><div className="mb-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm"><Sparkles size={15}/> AI-assisted search</div><h1 className="text-4xl font-semibold leading-tight">A clearer path to your next role.</h1><p className="mt-5 max-w-md leading-7 text-indigo-100">Discover location-specific roles, understand your fit, and create stronger applications in one focused workspace.</p><div className="mt-10 space-y-3 text-sm text-indigo-100"><p className="flex items-center gap-2"><CheckCircle2 size={17}/> Precise location-based search</p><p className="flex items-center gap-2"><CheckCircle2 size={17}/> Resume match insights</p></div></div>
              <div className="flex flex-col justify-center p-8 sm:p-12">
                <h2 className="text-2xl font-semibold tracking-tight text-slate-900">Welcome back</h2>
                <p className="mt-2 text-slate-500">Sign in securely to continue your search.</p>
                <button 
                    onClick={login}
                    className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3.5 font-semibold text-white transition hover:bg-indigo-700"
                >
                    Continue with Google <ArrowRight size={18}/>
                </button>
                <p className="mt-5 text-center text-xs leading-5 text-slate-400">By continuing, you agree to use your Google account for secure sign-in.</p>
              </div>
            </div>
        </div>
    )
}

export default Login
