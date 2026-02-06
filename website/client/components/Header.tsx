'use client';

import Link from 'next/link';
import { Search } from 'lucide-react';
import { useState } from 'react';

export default function Header() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-primary shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-accent rounded-lg flex items-center justify-center transform group-hover:scale-110 transition-transform">
              <span className="text-primary text-xl font-bold">📹</span>
            </div>
            <span className="text-white text-xl font-bold hidden sm:block">Video Library</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-2 sm:space-x-6">
            <Link
              href="/"
              className="px-4 py-2 text-white hover:bg-hover hover:text-hover-text rounded-lg transition-colors font-medium"
            >
              Recent Updates
            </Link>
            <Link
              href="/actresses"
              className="px-4 py-2 text-white hover:bg-hover hover:text-hover-text rounded-lg transition-colors font-medium"
            >
              Actresses
            </Link>
            <button
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              className="p-2 text-white hover:bg-hover hover:text-hover-text rounded-lg transition-colors"
              aria-label="Search"
            >
              <Search size={20} />
            </button>
          </nav>
        </div>

        {/* Search Bar */}
        {isSearchOpen && (
          <div className="mt-4 animate-in slide-in-from-top duration-200">
            <input
              type="text"
              placeholder="Search videos..."
              className="w-full px-4 py-3 bg-secondary text-light placeholder-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
              autoFocus
            />
          </div>
        )}
      </div>
    </header>
  );
}
