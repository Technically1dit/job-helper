import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { jobsAPI } from '../services/api'
import { ArrowRight, BriefcaseBusiness, MapPin, Search, Sparkles } from 'lucide-react'

const Dashboard = () => {
    const [jobs, setJobs] = useState([])
    const [query, setQuery] = useState('')
    const [location, setLocation] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        jobsAPI.list().then(res => setJobs(res.data.slice(0, 5))).catch(() => setJobs([]))
    }, [])

    const handleSearch = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const result = await jobsAPI.search(query.trim(), location.trim())
            sessionStorage.setItem('latestJobSearch', JSON.stringify({
                query: query.trim(), location: location.trim(), jobs: result.data
            }))
            navigate('/jobs', { state: { search: { query: query.trim(), location: location.trim(), jobs: result.data } } })
        } catch(e) {
            alert('Search failed.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-6xl mx-auto space-y-10">
            <section className="relative overflow-hidden rounded-[2rem] bg-slate-950 px-6 py-10 text-white shadow-2xl shadow-indigo-950/20 sm:px-10 sm:py-14">
                <div className="absolute -right-16 -top-20 h-72 w-72 rounded-full bg-violet-500/30 blur-3xl" />
                <div className="absolute -bottom-24 left-1/3 h-64 w-64 rounded-full bg-cyan-400/15 blur-3xl" />
                <div className="relative max-w-3xl">
                    <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-sm font-medium text-indigo-100"><Sparkles size={15} /> A more focused job search</div>
                    <h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">Find work that fits your next chapter.</h2>
                    <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">Search a precise role and location, then use AI to assess fit and make every application count.</p>
                </div>
                <form onSubmit={handleSearch} className="relative mt-8 grid gap-3 rounded-2xl border border-white/10 bg-white/10 p-3 backdrop-blur sm:grid-cols-[1.25fr_1fr_auto]">
                    <label className="flex items-center gap-3 rounded-xl bg-white px-4 py-3 text-slate-700"><Search size={18} className="text-indigo-600" /><input
                        type="text" aria-label="Job title or keywords" placeholder="Job title or keywords"
                        className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
                        value={query} onChange={e => setQuery(e.target.value)} required
                    /></label>
                    <label className="flex items-center gap-3 rounded-xl bg-white px-4 py-3 text-slate-700"><MapPin size={18} className="text-indigo-600" /><input
                        type="text" aria-label="Location" placeholder="City or Remote (e.g. Ahmedabad)"
                        className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
                        value={location} onChange={e => setLocation(e.target.value)} required
                    /></label>
                    <button 
                        type="submit" disabled={loading}
                        className="justify-center rounded-xl bg-indigo-500 px-6 py-3 font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-70 flex items-center gap-2"
                    >
                        {loading ? 'Searching...' : <><Search size={20} /> Search</>}
                    </button>
                </form>
            </section>
            
            <section>
            <div className="mb-5 flex items-end justify-between"><div><p className="text-sm font-medium text-indigo-600">YOUR WORKSPACE</p><h3 className="text-2xl font-semibold tracking-tight text-slate-900">Recent opportunities</h3></div><Link to="/jobs" className="hidden items-center gap-1 text-sm font-semibold text-indigo-600 hover:text-indigo-800 sm:flex">View all <ArrowRight size={16}/></Link></div>
            <div className="grid gap-3">
                {jobs.map(job => (
                    <Link key={job.id} to={`/jobs/${job.id}`} className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-100/50 block">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-lg font-semibold text-slate-900 group-hover:text-indigo-700">{job.title}</h4>
                                <p className="mt-1 font-medium text-slate-600">{job.company}</p>
                                <p className="mt-2 flex items-center gap-1.5 text-sm text-slate-500"><MapPin size={14}/>{job.location}</p>
                            </div>
                            {job.match_score && (
                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${job.match_score >= 80 ? 'bg-green-100 text-green-800' : job.match_score >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                    {job.match_score}% Match
                                </span>
                            )}
                        </div>
                    </Link>
                ))}
                {jobs.length === 0 && <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500"><BriefcaseBusiness className="mx-auto mb-3 text-slate-400" />No saved opportunities yet — start with a search above.</div>}
            </div>
            </section>
        </div>
    )
}

export default Dashboard
