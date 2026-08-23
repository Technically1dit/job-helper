import { useAuth } from '../context/AuthContext'

const Login = () => {
    const { login } = useAuth()
    
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md text-center">
                <h1 className="text-3xl font-bold text-blue-600 mb-2">JobHunter AI</h1>
                <p className="text-gray-600 mb-8">Your personal AI-powered job search assistant.</p>
                <button 
                    onClick={login}
                    className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 transition"
                >
                    Continue with Google
                </button>
            </div>
        </div>
    )
}

export default Login
