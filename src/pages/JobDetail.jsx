import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobsAPI } from '../services/api'
import { Building2, Search, Zap, ExternalLink, Bookmark, Mail } from 'lucide-react'

const JobDetail = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [job, setJob] = useState(null)
    const [loading, setLoading] = useState(true)
    
    // Status states for actions
    const [analyzing, setAnalyzing] = useState(false)
    const [researching, setResearching] = useState(false)
    const [findingContact, setFindingContact] = useState(false)

    useEffect(() => {
        loadJob()
    }, [id])

    const loadJob = () => {
        jobsAPI.get(id).then(res => {
            setJob(res.data)
            setLoading(false)
        })
    }

    const analyzeJob = async () => {
        setAnalyzing(true)
        await jobsAPI.analyze(id)
        loadJob()
        setAnalyzing(false)
    }

    const researchCompany = async () => {
        setResearching(true)
        await jobsAPI.company(id)
        loadJob()
        setResearching(false)
    }

    const findContact = async () => {
        setFindingContact(true)
        await jobsAPI.contact(id)
        loadJob()
        setFindingContact(false)
    }

    const toggleSave = async () => {
        await jobsAPI.toggleSave(id)
        loadJob()
    }

    if (loading) return <div>Loading...</div>
    if (!job) return <div>Job not found</div>

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                <div className="flex justify-between items-start">
                    <div>
                        <h2 className="text-3xl font-bold text-gray-800">{job.title}</h2>
                        <div className="text-xl text-gray-600 mt-2 font-medium">{job.company} &bull; {job.location}</div>
                        <div className="mt-3 flex flex-wrap gap-2"><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">Source: {job.source || 'Not available'}</span>{job.apply_url && <a href={job.apply_url} target="_blank" rel="noopener noreferrer" className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">Application link available</a>}</div>
                        {job.job_type && <span className="inline-block mt-4 bg-gray-100 text-gray-700 px-3 py-1 rounded-md text-sm">{job.job_type}</span>}
                    </div>
                    <div className="flex gap-2">
                        <button onClick={toggleSave} className={`p-3 rounded-lg border ${job.saved_at ? 'bg-indigo-50 border-indigo-200 text-indigo-600' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}>
                            <Bookmark size={20} fill={job.saved_at ? "currentColor" : "none"} />
                        </button>
                        {job.source_url && (
                            <a href={job.source_url} target="_blank" rel="noopener noreferrer" className="p-3 bg-blue-50 text-blue-600 rounded-lg border border-blue-100 hover:bg-blue-100 flex items-center gap-2">
                                <ExternalLink size={20} /> View Original
                            </a>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
                {/* AI Actions */}
                <div className="col-span-1 space-y-4">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="font-bold text-gray-800 mb-4">AI Actions</h3>
                        
                        <button onClick={analyzeJob} disabled={analyzing} className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition mb-3">
                            <span className="flex items-center gap-2"><Zap size={18} /> Resume Match</span>
                            {analyzing && <span className="text-xs">Processing...</span>}
                        </button>

                        <button onClick={researchCompany} disabled={researching} className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition mb-3">
                            <span className="flex items-center gap-2"><Building2 size={18} /> Research Company</span>
                            {researching && <span className="text-xs">Processing...</span>}
                        </button>

                        <button onClick={findContact} disabled={findingContact} className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition">
                            <span className="flex items-center gap-2"><Search size={18} /> Find Contacts</span>
                            {findingContact && <span className="text-xs">Processing...</span>}
                        </button>
                    </div>
                    
                    {/* Write Application Email button */}
                    <button 
                        onClick={() => navigate(`/jobs/${id}/application`)}
                        className="w-full flex items-center justify-center gap-2 p-4 bg-green-600 text-white rounded-xl shadow-sm font-semibold hover:bg-green-700 transition"
                    >
                        <Mail size={20} /> Write Application
                    </button>
                </div>

                {/* AI Results */}
                <div className="col-span-2 space-y-6">
                    {job.match_score && (
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><Zap size={20} className="text-blue-500"/> AI Match Analysis</h3>
                            <div className="flex items-center gap-4 mb-4">
                                <div className={`text-4xl font-bold ${job.match_score >= 80 ? 'text-green-600' : job.match_score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                                    {job.match_score}%
                                </div>
                                <div>
                                    <p className="text-gray-700 font-medium">Recommendation: <span className="capitalize">{job.analysis?.recommendation?.replace('_', ' ')}</span></p>
                                </div>
                            </div>
                            <p className="text-gray-600">{job.analysis?.short_summary}</p>
                            
                            <div className="mt-4 grid grid-cols-2 gap-4">
                                <div>
                                    <h4 className="text-sm font-semibold text-green-700 mb-2">Matching Skills</h4>
                                    <ul className="text-sm text-gray-600 space-y-1">
                                        {job.analysis?.matching_skills?.map((s,i) => <li key={i}>&bull; {s}</li>)}
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="text-sm font-semibold text-red-700 mb-2">Missing Skills</h4>
                                    <ul className="text-sm text-gray-600 space-y-1">
                                        {job.analysis?.missing_skills?.map((s,i) => <li key={i}>&bull; {s}</li>)}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}

                    {job.company_summary && (
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><Building2 size={20} className="text-blue-500"/> Company Profile</h3>
                            <p className="text-gray-700 mb-4">{job.company_summary}</p>
                            <div className="text-sm text-gray-500">
                                <p>Industry: {job.industry}</p>
                                {job.company_website && <p>Website: <a href={job.company_website} target="_blank" rel="noreferrer" className="text-blue-600">{job.company_website}</a></p>}
                            </div>
                        </div>
                    )}

                    {job.contact_email && (
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><Search size={20} className="text-blue-500"/> Hiring Contact</h3>
                            <div className="bg-blue-50 border border-blue-100 p-4 rounded-lg">
                                <p className="font-bold text-blue-900">{job.contact_name}</p>
                                <p className="text-blue-800">{job.contact_role}</p>
                                <p className="text-blue-600 mt-2">{job.contact_email}</p>
                            </div>
                        </div>
                    )}

                    {!job.contact_email && <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100"><h3 className="font-bold text-gray-800 mb-2">Recruitment contact</h3><p className="text-sm text-gray-500">Recruitment email: Not found. We only show addresses verified in a source.</p></div>}

                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="font-bold text-gray-800 mb-4">Job Description</h3>
                        <div className="text-gray-700 whitespace-pre-wrap">{job.description || 'No description provided.'}</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default JobDetail
