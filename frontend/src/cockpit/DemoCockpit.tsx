import { lazy, Suspense } from 'react';
import RootLayout from './app/layout';
import { RouterProvider, usePathname } from './router';
import Link from './link';

const Home = lazy(() => import('./app/page'));
const Journey = lazy(() => import('./app/parcours/page'));
const Setup = lazy(() => import('./app/parcours/installation/page'));
const Sales = lazy(() => import('./app/travail/ventes/page'));
const Simulations = lazy(() => import('./app/simulations/page'));
const Atlas = lazy(() => import('./app/simulations/atlas/page'));
const Decisions = lazy(() => import('./app/decisions/page'));
const Actuals = lazy(() => import('./app/suivi-mensuel/page'));
const Reports = lazy(() => import('./app/livrables/page'));
const Expert = lazy(() => import('./app/expert/page'));
const Sheet = lazy(() => import('./app/expert/feuilles/page'));
const Theme = lazy(() => import('./app/travail/theme-page'));
const Scenario = lazy(() => import('./app/simulations/scenario-page'));

function Routes() {
  const path = usePathname().replace(/\/$/, '') || '/';
  const pages = { '/': Home, '/parcours': Journey, '/parcours/installation': Setup,
    '/travail/ventes': Sales, '/simulations': Simulations, '/simulations/atlas': Atlas,
    '/decisions': Decisions, '/suivi-mensuel': Actuals, '/livrables': Reports, '/expert': Expert };
  const Page = pages[path as keyof typeof pages] || (/^\/expert\/feuilles\/[^/]+$/.test(path) ? Sheet
    : /^\/travail\/(couts|equipe|investissements|tresorerie|synthese)$/.test(path) ? Theme
    : /^\/simulations\/[^/]+$/.test(path) ? Scenario : undefined);
  return <RootLayout><div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950" role="note">
    <span>Démonstration : données fictives conservées dans ce navigateur.</span>
    <a href="/" className="font-semibold underline">Ouvrir mes dossiers réels</a>
  </div><Suspense fallback={<p role="status">Ouverture de la vue…</p>}>
    {Page ? <Page /> : <section><h1>Cette vue n’existe pas</h1><Link href="/parcours">Revenir au parcours</Link></section>}
  </Suspense></RootLayout>;
}

export default function DemoCockpit() {
  return <RouterProvider basePath="/demo"><Routes /></RouterProvider>;
}
