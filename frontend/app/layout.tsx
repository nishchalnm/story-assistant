import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Story Assistant',
  description: 'A writing partner that remembers your story',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}