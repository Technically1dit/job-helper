import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobsAPI, gmailAPI } from '../services/api'
import { Send, Edit2, Loader } from 'lucide-react'

const ApplicationGenerator = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const [job, setJob] = useState(null)
    const [draft, setDraft] = useState({ subject: '', body: '' })
    const [recipient, setRecipient] = useState('')
    const [generating, setGenerating] = useState(false)
    const [sending, setSending] = useState(false)

    useEffect(() => {
        jobsAPI.get(id).then(res => {
            setJob(res.data)
            setRecipient(res.data.contact_email || '')
        })
    }, [id])

    const generateEmail = async () => {
        setGenerating(true)
        try {
            const res = await jobsAPI.generateEmail(id)
            setDraft(res.data)
        } catch(e) {
            alert('Failed to generate email')
        } finally {
            setGenerating(false)
        }
    }

    const sendEmail = async () => {
        if (!recipient) { alert('Recipient email is required'); return }
        setSending(true)
        try {
            await gmailAPI.send({
                job_id: job.id,
                to: recipient,
                subject: draft.subject,
                body: draft.body
            })
            alert('Application sent successfully!')
            navigate('/applications')
        } catch(e) {
            alert('Failed to send email. Is your Gmail connected?')
        } finally {
            setSending(false)
        }
    }

    if (!job) return <div>Loading...</div>

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Write Application</h2>
                <p className="text-gray-600 mb-6">For: {job.title} at {job.company}</p>

                <div className="mb-6">
                    <button 
                        onClick={generateEmail} disabled={generating}
                        className="bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-70 flex items-center gap-2"
                    >
                        {generating ? <><Loader className="animate-spin" size={18}/> Generating...</> : <><Edit2 size={18}/> Generate AI Draft</>}
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Recipient Email</label>
                        <input 
                            type="email" value={recipient} onChange={e => setRecipient(e.target.value)}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            placeholder="hr@company.com"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Subject</label>
                        <input 
                            type="text" value={draft.subject} onChange={e => setDraft({...draft, subject: e.target.value})}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Message Body</label>
                        <textarea 
                            value={draft.body} onChange={e => setDraft({...draft, body: e.target.value})}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 h-64"
                        />
                    </div>
                </div>

                <div className="mt-8 flex justify-end">
                    <button 
                        onClick={sendEmail} disabled={sending || !draft.body}
                        className="bg-green-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                    >
                        {sending ? 'Sending...' : <><Send size={20} /> Send via Gmail</>}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ApplicationGenerator
