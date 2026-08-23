import { useState, useEffect } from 'react'
import { applicationsAPI } from '../services/api'

const Applications = () => {
    const [apps, setApps] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        applicationsAPI.list().then(res => {
            setApps(res.data)
            setLoading(false)
        })
    }, [])

    if (loading) return <div>Loading...</div>

    return (
        <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Applications</h2>
            <div className="grid gap-4">
                {apps.map(app => (
                    <div key={app.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-lg font-semibold text-gray-800">{app.subject}</h4>
                                <p className="text-gray-600">To: {app.recipient}</p>
                                <p className="text-gray-500 text-sm mt-1">Sent at: {app.sent_at ? new Date(app.sent_at).toLocaleString() : 'N/A'}</p>
                            </div>
                            <span className="px-3 py-1 rounded-full text-sm font-bold bg-green-100 text-green-800">
                                {app.status}
                            </span>
                        </div>
                    </div>
                ))}
                {apps.length === 0 && <p className="text-gray-500">No applications sent yet.</p>}
            </div>
        </div>
    )
}

export default Applications
