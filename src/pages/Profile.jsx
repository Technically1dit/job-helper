import { useState, useEffect } from 'react'
import { profileAPI } from '../services/api'
import { Upload } from 'lucide-react'

const Profile = () => {
    const [profile, setProfile] = useState(null)
    const [loading, setLoading] = useState(true)
    const [uploading, setUploading] = useState(false)

    useEffect(() => {
        profileAPI.get().then(res => {
            setProfile(res.data)
            setLoading(false)
        })
    }, [])

    const handleUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return
        
        setUploading(true)
        try {
            const res = await profileAPI.uploadResume(file)
            setProfile(res.data)
            alert('Resume parsed and profile updated!')
        } catch(e) {
            alert('Upload failed: ' + (e.response?.data?.detail || e.message))
        } finally {
            setUploading(false)
        }
    }

    if (loading) return <div>Loading...</div>

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Resume</h2>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center">
                    <input type="file" accept="application/pdf" className="hidden" id="resume" onChange={handleUpload} disabled={uploading} />
                    <label htmlFor="resume" className="cursor-pointer flex flex-col items-center">
                        <Upload size={32} className="text-blue-500 mb-4" />
                        <span className="text-blue-600 font-semibold">{uploading ? 'Processing...' : 'Upload PDF Resume'}</span>
                        <span className="text-gray-500 text-sm mt-2">{profile.resume_filename || 'No resume uploaded yet'}</span>
                    </label>
                </div>
            </div>
            
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Extracted Profile</h2>
                <div className="space-y-4">
                    <div>
                        <h3 className="font-semibold text-gray-700">Skills</h3>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {profile.skills?.map((s,i) => <span key={i} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">{s}</span>)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Profile
