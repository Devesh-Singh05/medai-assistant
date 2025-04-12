'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Upload, Clock } from 'lucide-react';
import { cn } from "@/lib/utils";

export function NavLinks() {
  const pathname = usePathname();

  const links = [
    {
      name: 'Upload',
      href: '/dashboard',
      icon: Upload,
    },
    {
      name: 'Recent',
      href: '/dashboard/recent-uploads',
      icon: Clock,
    },
  ];

  return (
    <nav className="flex justify-center space-x-4 bg-white shadow-sm p-4 mb-6">
      {links.map((link) => {
        const Icon = link.icon;
        const isActive = pathname === link.href;

        return (
          <Link
            key={link.name}
            href={link.href}
            className={cn(
              "flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors",
              isActive 
                ? "bg-gray-100 text-gray-900" 
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            )}
          >
            <Icon className="h-4 w-4 mr-2" />
            {link.name}
          </Link>
        );
      })}
    </nav>
  );
}
