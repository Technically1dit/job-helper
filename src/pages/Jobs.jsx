import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { jobsAPI } from '../services/api'
import { ArrowLeft, BriefcaseBusiness, MapPin, SearchX } from 'lucide-react'

const Jobs = () => {
    const [jobs, setJobs] = useState([])
    const [loading, setLoading] = useState(true)
    const routerLocation = useLocation()

    useEffect(() => {
        const recentSearch = routerLocation.state?.search || JSON.parse(sessionStorage.getItem('latestJobSearch') || 'null')
        if (recentSearch) {
            setJobs(recentSearch.jobs || [])
            setLoading(false)
            return
        }
        jobsAPI.list().then(res => setJobs(res.data)).catch(() => setJobs([])).finally(() => setLoading(false))
    }, [routerLocation.state])

    if (loading) return <div>Loading...</div>

    return (
        <div className="max-w-6xl mx-auto">
            <Link to="/" className="mb-5 inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-indigo-700"><ArrowLeft size={16}/> Back to search</Link>
            <div className="mb-7 flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold uppercase tracking-wider text-indigo-600">SEARCH RESULTS</p><h2 className="text-3xl font-semibold tracking-tight text-slate-900">Opportunities for you</h2></div>{routerLocation.state?.search && <div className="rounded-full bg-indigo-50 px-4 py-2 text-sm text-indigo-800">{routerLocation.state.search.query} · {routerLocation.state.search.location}</div>}</div>
            <div className="grid gap-4">
                {jobs.map(job => (
                    <Link key={job.id} to={`/jobs/${job.id}`} className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-100/60">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-xl font-semibold text-slate-900 group-hover:text-indigo-700">{job.title}</h4>
                                <p className="mt-1 font-medium text-slate-600">{job.company}</p>
                                <p className="mt-3 flex items-center gap-1.5 text-sm text-slate-500"><MapPin size={15}/>{job.location}</p>
                                <div className="mt-3 flex flex-wrap gap-2"><span className="inline-block rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">{job.source || 'Job source'}</span>{job.saved_at && <span className="inline-block rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-bold text-indigo-800">Saved</span>}</div>
                            </div>
                            {job.match_score && (
                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${job.match_score >= 80 ? 'bg-green-100 text-green-800' : job.match_score >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                    {job.match_score}% Match
                                </span>
                            )}
                        </div>
                    </Link>
                ))}
            </div>
            {!jobs.length && <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center"><SearchX className="mx-auto mb-3 text-slate-400"/><h3 className="font-semibold text-slate-800">No jobs match this exact location yet</h3><p className="mt-1 text-sm text-slate-500">Try a nearby city, a broader title, or search again later.</p></div>}
        </div>
    )
}

export default Jobs
