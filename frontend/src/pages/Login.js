import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    const result = await login(email, password);
    setLoading(false);

    if (result.success) {
      toast.success('Login successful!');
      navigate('/dashboard');
    } else {
      toast.error(result.error || 'Login failed');
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 min-h-screen">
      <div className="hidden md:block bg-gray-100 relative overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1610496571096-8367bdbbae2b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNDR8MHwxfHNlYXJjaHwyfHxtaW5pbWFsaXN0JTIwd2hpdGUlMjBhcmNoaXRlY3R1cmUlMjBhYnN0cmFjdHxlbnwwfHx8fDE3NzYxODg5MDJ8MA&ixlib=rb-4.1.0&q=85"
          alt="Architecture"
          className="w-full h-full object-cover"
        />
      </div>
      
      <div className="flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-sm space-y-6">
          <div className="space-y-2">
            <h1 className="text-4xl tracking-tight font-bold" style={{ fontFamily: 'Satoshi, sans-serif' }}>
              Student Hub
            </h1>
            <p className="text-sm text-gray-500" style={{ fontFamily: 'IBM Plex Sans, sans-serif' }}>
              Sign in to manage students
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" data-testid="login-form">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-black focus:border-black"
                data-testid="login-email-input"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-black focus:border-black"
                data-testid="login-password-input"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-black text-white hover:bg-gray-800 rounded-md px-4 py-2 text-sm font-medium transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-black"
              data-testid="login-submit-button"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
