import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const location = useLocation();
    
    const navLinks = [
        { name: 'Home', path: '/' },
        { name: 'Inventory', path: '/inventory' },
        { name: 'About', path: '/about' },
        { name: 'Contact', path: '/contact' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <header className="absolute top-0 left-0 right-0 z-50">
            <nav className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex items-center justify-between">
                    <Link to="/" className="text-2xl font-bold text-white tracking-wider">
                        Prevost<span className="text-amber-500">GO</span>
                    </Link>
                    
                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center space-x-8">
                        {navLinks.map(link => (
                            <Link 
                                key={link.path} 
                                to={link.path} 
                                className={`text-sm font-medium transition-colors ${
                                    isActive(link.path) ? 'text-amber-400' : 'text-gray-300 hover:text-white'
                                }`}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>
                    
                    <div className="hidden md:flex">
                        <Link 
                            to="/sell" 
                            className="px-5 py-2 text-sm font-medium text-white bg-white/5 border border-white/20 rounded-lg backdrop-blur-sm hover:bg-white/10 transition-colors"
                        >
                            List Your Coach
                        </Link>
                    </div>

                    {/* Mobile Nav Button */}
                    <div className="md:hidden">
                        <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-white">
                            {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
                        </button>
                    </div>
                </div>

                {/* Mobile Menu */}
                <div className={`transition-all duration-300 ease-in-out md:hidden ${
                    isMenuOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'
                } overflow-hidden`}>
                    <div className="mt-6 bg-black/50 backdrop-blur-lg rounded-lg p-4 space-y-4">
                        {navLinks.map(link => (
                             <Link 
                                key={link.path} 
                                to={link.path} 
                                onClick={() => setIsMenuOpen(false)} 
                                className={`block py-2 text-center rounded-md ${
                                    isActive(link.path) ? 'text-amber-400 bg-white/10' : 'text-gray-200 hover:bg-white/5'
                                }`}
                            >
                                {link.name}
                            </Link>
                        ))}
                         <Link 
                            to="/sell" 
                            onClick={() => setIsMenuOpen(false)}
                            className="block w-full mt-2 px-5 py-3 text-center font-medium text-white bg-amber-600 rounded-lg hover:bg-amber-500 transition-colors"
                         >
                            List Your Coach
                        </Link>
                    </div>
                </div>
            </nav>
        </header>
    );
};

const Footer = () => {
    return (
        <footer className="bg-black border-t border-white/10">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div className="md:col-span-1">
                        <h3 className="text-xl font-bold text-white">
                            Prevost<span className="text-amber-500">GO</span>
                        </h3>
                        <p className="mt-2 text-gray-400 text-sm">
                            The premier marketplace for luxury Prevost motorcoaches.
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-gray-200">Quick Links</h4>
                        <ul className="mt-4 space-y-2 text-sm">
                            <li><Link to="/inventory" className="text-gray-400 hover:text-amber-400">Inventory</Link></li>
                            <li><Link to="/sell" className="text-gray-400 hover:text-amber-400">Sell Your Coach</Link></li>
                            <li><Link to="/financing" className="text-gray-400 hover:text-amber-400">Financing</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-semibold text-gray-200">About</h4>
                        <ul className="mt-4 space-y-2 text-sm">
                            <li><Link to="/about" className="text-gray-400 hover:text-amber-400">About Us</Link></li>
                            <li><Link to="/contact" className="text-gray-400 hover:text-amber-400">Contact</Link></li>
                            <li><Link to="/privacy" className="text-gray-400 hover:text-amber-400">Privacy Policy</Link></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-semibold text-gray-200">Connect</h4>
                        <p className="mt-4 text-gray-400 text-sm">
                            Stay up to date with the latest listings and news.
                        </p>
                        {/* Newsletter form can go here */}
                    </div>
                </div>
                <div className="mt-12 border-t border-white/10 pt-8 text-center text-sm text-gray-500">
                    <p>&copy; {new Date().getFullYear()} PrevostGO. All rights reserved. Not affiliated with Prevost Car Inc.</p>
                </div>
            </div>
        </footer>
    );
};

const Layout = () => {
  return (
    <div className="bg-[#0a0a0a] min-h-screen font-sans text-white relative">
      {/* Animated Gradient Background */}
      <div className="absolute inset-0 z-0 overflow-hidden">
          <div className="absolute top-0 left-0 w-96 h-96 bg-amber-900/30 rounded-full filter blur-3xl opacity-30 animate-blob"></div>
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-900/30 rounded-full filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-amber-800/20 rounded-full filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>
      {/* Noise Texture Overlay */}
      <div className="absolute inset-0 z-0 opacity-[0.02] bg-[url('data:image/svg+xml,%3Csvg%20width%3D%22100%22%20height%3D%22100%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cdefs%3E%3Cfilter%20id%3D%22noise%22%3E%3CfeTurbulence%20type%3D%22fractalNoise%22%20baseFrequency%3D%220.8%22%20numOctaves%3D%224%22%20stitchTiles%3D%22stitch%22/%3E%3C/filter%3E%3C/defs%3E%3Crect%20width%3D%22100%25%22%20height%3D%22100%25%22%20filter%3D%22url(%23noise)%22/%3E%3C/svg%3E')]"></div>
      
      <div className="relative z-10 flex flex-col min-h-screen">
          <Header />
          <div className="flex-grow">
              <Outlet />
          </div>
          <Footer />
      </div>
    </div>
  );
};

export default Layout;
