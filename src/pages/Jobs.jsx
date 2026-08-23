import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { jobsAPI } from '../services/api'

const Jobs = () => {
    const [jobs, setJobs] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        jobsAPI.list().then(res => {
            setJobs(res.data)
            setLoading(false)
        })
    }, [])

    if (loading) return <div>Loading...</div>

    return (
        <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Search Results</h2>
            <div className="grid gap-4">
                {jobs.map(job => (
                    <Link key={job.id} to={/jobs/} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-lg font-semibold text-blue-600">{job.title}</h4>
                                <p className="text-gray-600 font-medium">{job.company}</p>
                                <p className="text-gray-500 text-sm mt-1">{job.location}</p>
                                {job.saved_at && <span className="inline-block mt-2 text-xs font-bold bg-indigo-100 text-indigo-800 px-2 py-1 rounded">Saved</span>}
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
        </div>
    )
}

export default Jobs
