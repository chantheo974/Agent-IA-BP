import { forwardRef, useEffect, useRef, useState, type CSSProperties, type ComponentProps } from 'react';
import Link from '../cockpit/link';
import { usePathname, useRouter, useSearchParams } from '../cockpit/router';
import { Button } from '@/components/ui/button';
import { CompanionBadge } from '@/components/cockpit/companion-mark';
import { PageHeading, StateBadge, Surface } from '@/components/cockpit/page-elements';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarHeader, SidebarInset, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarTrigger, useSidebar } from '@/components/ui/sidebar';
import { ArrowRight, Building2, FileSpreadsheet, FileText, Gauge, History, LayoutDashboard, LineChart, Palette, Route, Settings2, Target, X } from '@/components/ui/site-icon';
import { statusLabel } from '../api';
import type { CompanyProfile } from '../workshopTypes';
import type { Catalog, ConnectedProps } from './types';
import { useCaseData } from './data';
import { Legacy, ReadError, SheetPanel, sheetHref } from './SheetPanel';
import { Decisions, Home, Personalization, ScenarioDetail, Scenarios, SheetCatalog, ThemePage, palettes, type PresentationPreferences } from './pages';

const navigation = [
  { label: 'Aujourd’hui', href: '/', icon: LayoutDashboard },
  { label: 'Parcours', href: '/parcours', icon: Route },
  { label: 'Simulations', href: '/simulations', icon: LineChart },
  { label: 'Décisions', href: '/decisions', icon: Target },
  { label: 'Suivi mensuel', href: '/suivi-mensuel', icon: Gauge },
  { label: 'Livrables', href: '/livrables', icon: FileText },
];
export const themeRoutes = [
  { slug: 'ventes', id: 'sales', label: 'Ventes et contrats', description: 'Offres, volumes, prix, contrats et conditions de vente.' },
  { slug: 'couts', id: 'costs', label: 'Coûts et marge', description: 'Achats, charges, stocks et coûts de production.' },
  { slug: 'equipe', id: 'team', label: 'Équipe', description: 'Postes, recrutements et coûts de personnel.' },
  { slug: 'investissements', id: 'investments', label: 'Investissements et financement', description: 'Investissements, dette, aides et fonds propres.' },
  { slug: 'tresorerie', id: 'cash', label: 'Trésorerie et fiscalité', description: 'Délais, flux de trésorerie, TVA et hypothèses fiscales.' },
  { slug: 'synthese', id: 'synthesis', label: 'Synthèse et valeur', description: 'États financiers, contrôles, sensibilités et valorisation.' },
];
function activeDestination(path: string, href: string) {
  if (href === '/') return path === '/';
  if (href === '/parcours') return path === '/parcours' || path.startsWith('/travail');
  return path.startsWith(href);
}
const Destination = forwardRef<HTMLAnchorElement, ComponentProps<typeof Link>>(function Destination({ onClick, ...props }, ref) {
  const { setOpenMobile } = useSidebar();
  return <Link {...props} ref={ref} onClick={event => { onClick?.(event); if (!event.defaultPrevented) setOpenMobile(false); }}/>;
});
function presentationFor(caseId: string): PresentationPreferences {
  try {
    const saved = JSON.parse(localStorage.getItem('tca.cockpit.presentation.v1.' + caseId) || '{}');
    return { palette: palettes.some(p => p.id === saved.palette) ? saved.palette : 'indigo', firstName: typeof saved.firstName === 'string' ? saved.firstName.slice(0, 80) : '', logo: typeof saved.logo === 'string' && /^data:image\/(png|jpeg|webp);base64,/.test(saved.logo) ? saved.logo : '' };
  } catch { return { palette: 'indigo', firstName: '', logo: '' }; }
}

export default function ConnectedCockpit(app: ConnectedProps) {
  const pathname = usePathname(), params = useSearchParams(), router = useRouter();
  const [chatOpen, setChatOpen] = useState(false), [preferences, setPreferences] = useState(() => presentationFor(app.caseId));
  const [preferenceError, setPreferenceError] = useState('');
  const contentRef = useRef<HTMLDivElement>(null);
  const profile = useCaseData<{ profile: CompanyProfile }>(app.caseId, '/profile', app.refresh);
  // Retain identities while refreshing this same dossier so an editor is not
  // unmounted by an SSE notification. Financial projections never use this option.
  const catalog = useCaseData<Catalog>(app.caseId, '/cockpit/catalog', app.refresh, true);
  const version = `${app.active?.revision}:${app.refresh}:${app.draft.id}:${app.draft.status}:${JSON.stringify(app.draft.operations || [])}`;
  const companyName = profile.data?.profile.name || app.active?.client_name || app.active?.name || 'Mon cockpit';
  const palette = palettes.find(item => item.id === preferences.palette) || palettes[0];
  const theme = themeRoutes.find(item => pathname === '/travail/' + item.slug);
  const pageLabel = theme?.label || (pathname.startsWith('/parcours/installation') ? 'Personnalisation' : pathname.startsWith('/expert') ? 'Mode expert' : pathname === '/documents' ? 'Documents' : navigation.find(item => activeDestination(pathname, item.href))?.label) || 'Mon cockpit';
  const paletteStyle = { '--brand': palette.deep, '--brand-accent': palette.accent, '--brand-deep': palette.deep, '--brand-soft': palette.soft, '--primary': palette.deep, '--ring': palette.deep, '--secondary': palette.soft, '--secondary-foreground': palette.deep, '--accent': palette.soft, '--accent-foreground': palette.deep, '--sidebar-primary': palette.deep, '--sidebar-ring': palette.deep, '--sidebar-accent': palette.soft, '--sidebar-accent-foreground': palette.deep } as CSSProperties;
  useEffect(() => {
    setPreferences(presentationFor(app.caseId)); setChatOpen(false);
  }, [app.caseId]);
  useEffect(() => { if (app.dialogsOpen) setChatOpen(false); }, [app.dialogsOpen]);
  useEffect(() => {
    const openAgentSheet = (event: Event) => {
      const name = (event as CustomEvent<{ name: string }>).detail?.name;
      const target = catalog.data?.sheets.find(sheet => sheet.name === name);
      if (target) router.push(sheetHref(target.id));
    };
    window.addEventListener('cockpit:open-agent-sheet', openAgentSheet);
    return () => window.removeEventListener('cockpit:open-agent-sheet', openAgentSheet);
  }, [catalog.data, router]);
  useEffect(() => { document.title = `${pageLabel} · ${companyName}`; }, [pageLabel, companyName]);
  // Only navigation moves focus. A late profile response or an SSE refresh must
  // not take the cursor away from a cell, an input, or an open dialog.
  useEffect(() => { contentRef.current?.focus({ preventScroll: true }); }, [pathname]);
  useEffect(() => {
    const previous = Object.keys(paletteStyle).map(key => [key, document.documentElement.style.getPropertyValue(key)]);
    Object.entries(paletteStyle).forEach(([key, value]) => document.documentElement.style.setProperty(key, String(value)));
    return () => previous.forEach(([key, value]) => value ? document.documentElement.style.setProperty(key, value) : document.documentElement.style.removeProperty(key));
  }, [palette.id]);
  const updatePreferences = (next: PresentationPreferences) => {
    try { localStorage.setItem('tca.cockpit.presentation.v1.' + app.caseId, JSON.stringify(next)); setPreferences(next); setPreferenceError(''); }
    catch { setPreferenceError('La préférence ne peut pas être enregistrée dans ce navigateur. Réduisez la taille du logo ou libérez du stockage.'); }
  };
  const discuss = (sheet = app.sheetName, prompt?: string) => { app.onContext(sheet, prompt); setChatOpen(true); };
  const newCase = () => {
    if (window.dispatchEvent(new CustomEvent('cockpit:before-navigation', { cancelable: true }))) app.onNew();
  };
  const openSheet = (name: string, cell?: string) => {
    const target = catalog.data?.sheets.find(sheet => sheet.name === name);
    if (target) router.push(sheetHref(target.id, 'grille') + (cell ? '&cell=' + encodeURIComponent(cell) : ''));
    else { app.onSheet(name, cell); router.push('/expert?grille=1'); }
  };
  const workshop = (page: Parameters<ConnectedProps['workshop']>[0]) => <Legacy>{app.workshop(page, openSheet)}</Legacy>;
  const chosenSheet = pathname.startsWith('/expert/feuilles/') ? catalog.data?.sheets.find(sheet => encodeURIComponent(sheet.id) === pathname.slice('/expert/feuilles/'.length)) : undefined;
  const brand = <span className="flex min-w-0 items-center gap-3"><span className="grid size-11 shrink-0 place-items-center rounded-[17px] bg-white/75 shadow-sm">{preferences.logo ? <img src={preferences.logo} className="max-h-9 max-w-9 rounded-xl object-contain" alt="Logo de l’entreprise"/> : <Building2 className="size-6 text-[var(--brand)]"/>}</span><span className="min-w-0"><strong className="block truncate text-[17px] tracking-tight text-[#17203a]">{companyName}</strong><span className="text-xs text-slate-500">Mon cockpit financier</span></span></span>;
  let content;
  if (!app.active) content = <Surface className="mt-8"><PageHeading eyebrow="Votre espace local" title={app.initializing || app.caseId ? 'Ouverture du dossier…' : 'Construisons votre prévisionnel'} description={app.initializing || app.caseId ? 'Nous retrouvons vos données et vos versions.' : 'Créez un dossier pour décrire votre entreprise, rassembler vos documents et tester vos décisions.'}/>{!app.initializing && !app.caseId && <Button className="mt-7 min-h-12 rounded-full px-6" onClick={newCase}>Créer mon premier dossier<ArrowRight /></Button>}</Surface>;
  else if (pathname === '/') content = <Home app={app} firstName={preferences.firstName} companyName={companyName} catalog={catalog.data} discuss={discuss}/>;
  else if (pathname === '/parcours/installation') content = <><PageHeading eyebrow="Votre cockpit" title="Un espace à votre image" description="Le profil de l’entreprise appartient au dossier. La palette, le logo et votre prénom sont des préférences de présentation de ce navigateur."/><Personalization preferences={preferences} change={updatePreferences} error={preferenceError}/><ReadError message={profile.error} retry={profile.retry}/>{workshop('company')}</>;
  else if (pathname === '/parcours') content = <><PageHeading eyebrow="Parcours" title="Construisons votre prévisionnel" description="Avancez thème par thème. Les données, sources et contrôles restent liés à votre dossier."/><div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{themeRoutes.map(item => <Surface key={item.id} variant="glass"><h2 className="text-xl font-semibold">{item.label}</h2><p className="mt-3 leading-7 text-slate-500">{item.description}</p><Button className="mt-5 min-h-11 rounded-full px-5" onClick={() => router.push('/travail/' + item.slug)}>Travailler sur ce thème<ArrowRight /></Button></Surface>)}</div><div className="mt-6 flex flex-wrap gap-3"><Button variant="outline" className="min-h-11 rounded-full px-5" onClick={() => router.push('/parcours/installation')}>Profil de l’entreprise</Button><Button variant="outline" className="min-h-11 rounded-full px-5" onClick={() => router.push('/documents')}>Documents et sources</Button></div><details className="mt-6"><summary className="cursor-pointer rounded-2xl bg-white/70 p-4 text-lg font-semibold">Toutes les qualifications et hypothèses du dossier</summary>{workshop('forecast')}</details></>;
  else if (pathname === '/documents') content = <><PageHeading eyebrow="Documents" title="Vos informations, avec leurs sources" description="Importez les pièces, vérifiez les extractions et confirmez les données utiles à votre prévisionnel."/>{workshop('documents')}</>;
  else if (theme) content = catalog.data ? <ThemePage app={app} catalog={catalog.data} theme={theme} version={version} discuss={discuss}/> : null;
  else if (pathname === '/expert') content = <><PageHeading eyebrow="Mode expert" title="Toutes les feuilles de votre modèle" description="Chaque feuille ouvre sa vue métier, sa grille et ses dépendances. Les identifiants suivent les évolutions du modèle."/>{catalog.data && <SheetCatalog catalog={catalog.data}/ >}{params.get('grille') === '1' && <Surface className="mt-6"><Legacy className="connected-grid">{app.grid(() => discuss(''))}</Legacy></Surface>}</>;
  else if (pathname.startsWith('/expert/feuilles/')) content = chosenSheet && catalog.data ? <SheetPanel key={app.caseId + chosenSheet.id} app={app} sheet={chosenSheet} catalog={catalog.data} discuss={discuss} version={version}/> : catalog.loading ? <p role="status">Recherche de la feuille…</p> : <Surface><h1 className="text-xl font-semibold">Cette feuille n’est pas disponible dans ce dossier</h1><p className="mt-3 text-slate-500">Elle a pu être supprimée, ou le lien appartient à un autre modèle.</p><Button className="mt-4 min-h-11 rounded-full" onClick={() => router.push('/expert')}>Consulter les feuilles du dossier</Button></Surface>;
  else if (pathname === '/simulations') content = <Scenarios app={app} workshop={workshop('scenarios')}/>;
  else if (pathname.startsWith('/simulations/')) content = <ScenarioDetail key={app.caseId + pathname} app={app} scenarioId={decodeURIComponent(pathname.slice('/simulations/'.length))}/>;
  else if (pathname === '/decisions') content = <Decisions app={app}/>;
  else if (pathname === '/suivi-mensuel') content = <><PageHeading eyebrow="Suivi mensuel" title="Vos chiffres réels, vos prochaines décisions" description="Conservez votre budget, intégrez le réalisé et contrôlez le raccord avec les mois à venir."/>{workshop('actuals')}</>;
  else if (pathname === '/livrables') content = <><PageHeading eyebrow="Livrables" title="Partagez un dossier à jour" description="Les quatre formats sont produits depuis le même instantané du dossier calculé, avec ses hypothèses et ses sources."/>{workshop('reports')}</>;
  else content = <Surface><h1 className="text-xl font-semibold">Cette page n’existe pas</h1><Button className="mt-4 min-h-11 rounded-full" onClick={() => router.push('/')}>Revenir à mon cockpit</Button></Surface>;
  return <div className="connected-cockpit" style={paletteStyle}><SidebarProvider style={{ '--sidebar-width': '15rem', ...paletteStyle } as CSSProperties} className="min-h-screen">
    <a href="#cockpit-content" className="skip-link">Aller au contenu</a>
    <Sidebar collapsible="offcanvas" className="border-r-0 bg-transparent p-4 pr-1"><div className="nav-island flex size-full flex-col rounded-[28px]">
      <SidebarHeader className="px-5 pb-3 pt-5"><Destination href="/" aria-label="Revenir à l’accueil" className="rounded-[18px]">{brand}</Destination></SidebarHeader>
      <SidebarContent><SidebarGroup className="px-3 pt-5"><SidebarGroupContent><SidebarMenu className="gap-1">{navigation.map(({ label, href, icon: NavIcon }) => <SidebarMenuItem key={href}><SidebarMenuButton size="lg" isActive={activeDestination(pathname, href)} render={<Destination href={href} aria-current={activeDestination(pathname, href) ? 'page' : undefined}/>} className="min-h-12 rounded-[18px] px-3.5 text-[15px] transition data-active:bg-white/88 data-active:text-[var(--brand-deep)] data-active:shadow-[0_10px_24px_rgba(54,63,104,.1)]"><NavIcon/><span>{label}</span></SidebarMenuButton></SidebarMenuItem>)}</SidebarMenu></SidebarGroupContent></SidebarGroup>
      <SidebarGroup className="mt-3 px-3"><SidebarGroupContent><SidebarMenu className="gap-1">{[{ label: 'Mode expert', href: '/expert', icon: FileSpreadsheet }, { label: 'Documents', href: '/documents', icon: FileText }, { label: 'Personnaliser', href: '/parcours/installation', icon: Palette }].map(({ label, href, icon: NavIcon }) => <SidebarMenuItem key={href}><SidebarMenuButton size="lg" isActive={pathname.startsWith(href)} render={<Destination href={href}/>} className="min-h-12 rounded-[18px] px-3.5 text-[15px] data-active:bg-white/88"><NavIcon/><span>{label}</span></SidebarMenuButton></SidebarMenuItem>)}</SidebarMenu></SidebarGroupContent></SidebarGroup></SidebarContent>
      <SidebarFooter className="gap-3 px-4 pb-4"><label className="text-xs font-medium text-slate-500">Dossier actif<select aria-label="Dossier actif" className="mt-2 min-h-11 w-full rounded-2xl border border-white bg-white/65 px-3 text-sm text-slate-700" value={app.caseId} onChange={e => { const event = new CustomEvent('cockpit:before-navigation', { cancelable: true }); if (window.dispatchEvent(event)) app.onCase(e.target.value); }}><option value="" disabled>Choisir un dossier</option>{app.cases.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><Button variant="ghost" className="min-h-11 rounded-full" onClick={newCase}>Nouveau dossier</Button><button className="reference-mini-card flex min-h-14 items-center gap-3 rounded-[18px] px-3 text-left" onClick={app.onVersions} disabled={!app.active}><History className="size-5 text-[var(--brand)]"/><span><strong className="block text-sm">Version du dossier</strong><small className="text-slate-500">{app.active ? 'Révision ' + (app.active.revision ?? 0) : 'Aucun dossier'}</small></span></button><span className="px-2 text-xs text-slate-500" role="status">{!app.caseId ? 'Service local' : app.connection === 'connected' ? 'Synchronisé avec votre serveur' : 'Connexion au serveur…'}</span></SidebarFooter>
    </div></Sidebar>
    <SidebarInset className="min-w-0 bg-transparent pb-24 md:pb-0"><header className="sticky top-0 z-20 bg-transparent px-3 py-3 sm:px-6 lg:px-8 xl:px-12"><div className="top-island flex min-h-[62px] items-center justify-between gap-3 rounded-[22px] px-3 sm:px-5"><div className="top-leading-cluster flex min-w-0 items-center gap-2.5"><SidebarTrigger aria-label="Ouvrir la navigation" className="liquid-control top-glass-control size-11 shrink-0 rounded-full md:hidden"/><Link href="/" className="mobile-brand-capsule top-glass-control min-w-0 rounded-full px-2 py-1.5 md:hidden">{brand}</Link><div className="top-glass-control hidden rounded-[22px] px-4 py-2.5 md:block"><p className="text-[13px] font-semibold uppercase tracking-[0.13em] text-[var(--brand)]">{pageLabel}</p><p className="mt-1 text-sm text-slate-500">Votre espace de décision</p></div></div><div className="top-trailing-cluster flex shrink-0 items-center gap-2"><span className="top-glass-control hidden rounded-full px-3 py-2 text-xs font-semibold text-slate-500 sm:inline-flex">Dossier réel · local</span><Button variant="ghost" className="liquid-control top-glass-control size-11 rounded-full" aria-label="Réglages API" onClick={app.onSettings}><Settings2/></Button></div></div></header>
      <div className="mx-auto w-full max-w-[1380px] px-4 pb-10 pt-4 sm:px-7 lg:px-10 lg:pb-14 lg:pt-7 xl:px-14"><div id="cockpit-content" ref={contentRef} tabIndex={-1} className="route-stage space-y-6 outline-none" aria-label={pageLabel}>
        {(app.error || app.notice) && <div role={app.error ? 'alert' : 'status'} className={'flex items-center gap-3 rounded-2xl p-4 ' + (app.error ? 'bg-red-50 text-red-900' : 'bg-emerald-50 text-emerald-900')}><p className="flex-1">{app.error || app.notice}</p>{app.error && <Button variant="outline" onClick={() => void app.onRefresh()}>Actualiser</Button>}<Button variant="ghost" aria-label="Fermer le message" onClick={app.onDismiss}><X/></Button></div>}
        {app.active && <><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex flex-wrap gap-2"><StateBadge tone="neutral">{app.active.name}</StateBadge><StateBadge>Révision {app.active.revision ?? 0}</StateBadge><StateBadge tone={app.active.calculation_status === 'RECALCULE' ? 'success' : 'warning'}>{statusLabel(app.active.calculation_status)}</StateBadge></div><Button variant="outline" className="min-h-11 rounded-full px-4" onClick={app.onDownload}>Télécharger l’Excel</Button></div><Legacy>{app.toolbar}</Legacy></>}
        {app.active && (pathname.startsWith('/expert') || !!theme || pathname === '/parcours') && <ReadError message={catalog.error} retry={catalog.retry}/>}
        {content}
        {app.active && <Legacy className="connected-draft-bar">{app.draftBar}</Legacy>}
      </div></div>
    </SidebarInset>
    <button aria-label="Ouvrir votre compagnon" onClick={() => discuss()} className="companion-trigger copilot-orbit liquid-control fixed bottom-4 right-4 z-40 flex size-14 items-center justify-center rounded-full p-0 sm:right-7 md:bottom-7"><CompanionBadge size="small" shape="round" motion={chatOpen ? 'engaged' : 'awake'}/></button>
  </SidebarProvider>
  <Dialog open={chatOpen} onOpenChange={setChatOpen}><DialogContent className="connected-cockpit connected-chat-dialog max-h-[92vh] overflow-hidden rounded-[30px] p-0 sm:max-w-[560px]"><DialogHeader className="px-5 pt-5"><DialogTitle className="flex items-center gap-3 text-lg"><CompanionBadge size="small"/>Votre compagnon</DialogTitle><DialogDescription>Discussion sur le dossier actif et la sélection affichée. Les propositions restent au brouillon.</DialogDescription></DialogHeader><Legacy className="connected-chat">{app.chat}</Legacy></DialogContent></Dialog>
  <Legacy>{app.dialogs}</Legacy>
  </div>;
}
