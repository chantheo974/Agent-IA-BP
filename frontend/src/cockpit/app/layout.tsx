import './globals.css';

import { AppShell } from '@/components/cockpit/app-shell';
import { DemoProvider } from '@/components/cockpit/demo-provider';

export const metadata = {
  title: 'Mon cockpit financier',
  description:
    'Prototype local d’un cockpit financier clair et orienté décision.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
        <DemoProvider>
          <AppShell>{children}</AppShell>
        </DemoProvider>
  );
}
