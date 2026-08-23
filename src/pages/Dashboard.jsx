import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { jobsAPI } from '../services/api'
import { Briefcase, Search } from 'lucide-react'

const Dashboard = () => {
    const [jobs, setJobs] = useState([])
    const [query, setQuery] = useState('')
    const [location, setLocation] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        jobsAPI.list().then(res => setJobs(res.data.slice(0, 5)))
    }, [])

    const handleSearch = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            await jobsAPI.search(query, location)
            navigate('/jobs')
        } catch(e) {
            alert('Search failed.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Find Your Next Role</h2>
                <form onSubmit={handleSearch} className="flex gap-4">
                    <input 
                        type="text" placeholder="Job title, keywords, or company"
                        className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={query} onChange={e => setQuery(e.target.value)} required
                    />
                    <input 
                        type="text" placeholder="Location (e.g. Remote, San Francisco)"
                        className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={location} onChange={e => setLocation(e.target.value)} required
                    />
                    <button 
                        type="submit" disabled={loading}
                        className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-70 flex items-center gap-2"
                    >
                        {loading ? 'Searching...' : <><Search size={20} /> Search</>}
                    </button>
                </form>
            </div>
            
            <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Jobs</h3>
            <div className="grid gap-4">
                {jobs.map(job => (
                    <Link key={job.id} to={/jobs/} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition block">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-lg font-semibold text-blue-600">{job.title}</h4>
                                <p className="text-gray-600 font-medium">{job.company}</p>
                                <p className="text-gray-500 text-sm mt-1">{job.location}</p>
                            </div>
                            {job.match_score && (
                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${job.match_score >= 80 ? 'bg-green-100 text-green-800' : job.match_score >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                    {job.match_score}% Match
                                </span>
                            )}
                        </div>
                    </Link>
                ))}
                {jobs.length === 0 && <p className="text-gray-500">No jobs found yet. Do a search to get started!</p>}
            </div>
        </div>
    )
}

export default Dashboard
