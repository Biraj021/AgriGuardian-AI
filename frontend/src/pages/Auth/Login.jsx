import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Login() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignUp) {
        await register(name, email, password);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md bg-surface p-8 rounded-2xl border border-gray-100 shadow-sm transition-all duration-300">
        
        {/* Branding */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center text-3xl mb-3">
            🌱
          </div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">
            {isSignUp ? 'Create your account' : 'Welcome back'}
          </h2>
          <p className="text-sm text-gray-500 mt-1.5">
            {isSignUp ? 'Start monitoring your farm today' : 'One Intelligent Decision Platform for Every Farmer'}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-700 text-sm p-3.5 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignUp && (
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary-500 transition-colors placeholder:text-gray-400"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="farmer@example.com"
              className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary-500 transition-colors placeholder:text-gray-400"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary-500 transition-colors placeholder:text-gray-400"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 px-4 bg-primary-500 hover:bg-primary-600 active:scale-[0.98] disabled:opacity-50 text-white font-medium text-sm rounded-lg transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              isSignUp ? 'Sign Up' : 'Sign In'
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-50 text-center">
          <button
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError('');
            }}
            className="text-sm font-medium text-primary-500 hover:text-primary-600 transition-colors focus:outline-none"
          >
            {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
          </button>
        </div>

        {!isSignUp && (
          <div className="mt-4 bg-emerald-50 border border-emerald-100 rounded-lg p-3 text-xs text-emerald-800">
            <p className="font-semibold mb-1">🌾 Demo Account</p>
            <p>Email: <code className="font-mono bg-emerald-100 px-1 rounded">demo@agriguardian.com</code></p>
            <p>Password: <code className="font-mono bg-emerald-100 px-1 rounded">Demo@12345</code></p>
            <button
              type="button"
              onClick={() => { setEmail('demo@agriguardian.com'); setPassword('Demo@12345'); }}
              className="mt-2 text-emerald-700 font-semibold underline hover:no-underline"
            >
              Fill demo credentials
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
