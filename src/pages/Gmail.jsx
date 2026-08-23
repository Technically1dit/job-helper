import { useState, useEffect } from 'react'
import { gmailAPI } from '../services/api'
import { Mail, CheckCircle, XCircle } from 'lucide-react'

const Gmail = () => {
    const [status, setStatus] = useState({ connected: false, email: '' })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadStatus()
    }, [])

    const loadStatus = () => {
        setLoading(true)
        gmailAPI.status().then(res => {
            setStatus(res.data)
            setLoading(false)
        })
    }

    const connect = async () => {
        const res = await gmailAPI.connect()
        window.location.href = res.data.url
    }

    const disconnect = async () => {
        await gmailAPI.disconnect()
        loadStatus()
    }

    if (loading) return <div>Loading...</div>

    return (
        <div className="max-w-xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <Mail size={48} className="mx-auto text-red-500 mb-6" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Gmail Integration</h2>
            <p className="text-gray-600 mb-8">Connect your Gmail account to send job applications directly from JobHunter AI.</p>
            
            {status.connected ? (
                <div className="space-y-6">
                    <div className="flex items-center justify-center gap-2 text-green-600 font-semibold bg-green-50 p-4 rounded-lg border border-green-200">
                        <CheckCircle size={20} /> Connected as {status.email}
                    </div>
                    <button onClick={disconnect} className="text-red-600 hover:underline">Disconnect Account</button>
                </div>
            ) : (
                <button onClick={connect} className="w-full bg-red-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-red-700 transition">
                    Connect Gmail Account
                </button>
            )}
        </div>
    )
}

export default Gmail
