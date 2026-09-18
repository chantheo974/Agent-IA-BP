'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FileSpreadsheet,
  FileText,
  Gauge,
  History,
  LayoutDashboard,
  LineChart,
  Palette,
  Route,
  RotateCcw,
  Target,
  X,
} from '@/components/ui/site-icon';
import { CompanionBadge } from '@/components/cockpit/companion-mark';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from '@/components/ui/sidebar';
import { useDemo } from '@/components/cockpit/demo-provider';
import { ImpactSheet } from '@/components/cockpit/impact-sheet';
import { CopilotSheet } from '@/components/cockpit/copilot-sheet';

const navigation = [
  { label: 'Aujourd’hui', href: '/', icon: LayoutDashboard },
  { label: 'Parcours', href: '/parcours', icon: Route },
  { label: 'Simulations', href: '/simulations', icon: LineChart },
  { label: 'Décisions', href: '/decisions', icon: Target },
  { label: 'Suivi mensuel', href: '/suivi-mensuel', icon: Gauge },
  { label: 'Livrables', href: '/livrables', icon: FileText },
];

const pageLabels: Array<[string, string]> = [
  ['/parcours/installation', 'Personnalisation'],
  ['/travail/ventes', 'Ventes et contrats'],
  ['/travail/couts', 'Coûts et marge'],
  ['/travail/equipe', 'Équipe'],
  ['/travail/investissements', 'Investissements et financement'],
  ['/travail/tresorerie', 'Trésorerie et fiscalité'],
  ['/travail/synthese', 'Synthèse et valeur'],
  ['/simulations/atlas', 'Simulation Atlas'],
  ['/simulations', 'Simulations'],
  ['/decisions', 'Décisions'],
  ['/suivi-mensuel', 'Suivi mensuel'],
  ['/livrables', 'Livrables'],
  ['/expert', 'Mode expert'],
  ['/parcours', 'Parcours'],
  ['/', 'Aujourd’hui'],
];

function isActive(pathname: string, href: string) {
  if (href === '/') return pathname === '/';
  if (href === '/simulations') return pathname.startsWith('/simulations');
  if (href === '/parcours') {
    if (pathname.startsWith('/parcours/installation')) return false;
    return pathname.startsWith('/parcours') || pathname.startsWith('/travail');
  }
  return pathname.startsWith(href);
}

const SidebarDestination = React.forwardRef<
  HTMLAnchorElement,
  React.ComponentProps<typeof Link>
>(function SidebarDestination({ onClick, ...props }, ref) {
  const { setOpenMobile } = useSidebar();

  return (
    <Link
      ref={ref}
      {...props}
      onClick={(event) => {
        onClick?.(event);
        if (!event.defaultPrevented) setOpenMobile(false);
      }}
    />
  );
});

function BrandMark({ compact = false }: { compact?: boolean }) {
  const { state } = useDemo();
  const initial = state.brand.companyName.trim().charAt(0).toUpperCase() || 'L';

  return (
    <div className="flex min-w-0 items-center gap-3">
      <div className="grid size-11 shrink-0 place-items-center overflow-hidden rounded-[15px] bg-[var(--brand-deep)] text-base font-bold text-white shadow-[0_9px_22px_color-mix(in_srgb,var(--brand)_24%,transparent)]">
        {state.brand.logoDataUrl ? (
          // The data URL is created and kept entirely in this browser.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={state.brand.logoDataUrl}
            alt=""
            className="size-full object-contain bg-white p-1"
          />
        ) : (
          initial
        )}
      </div>
      {!compact ? (
        <div className="min-w-0">
          <p className="truncate text-[15px] font-semibold tracking-[-0.01em]">
            {state.brand.companyName}
          </p>
          <p className="truncate text-[13px] text-slate-500">Mon cockpit</p>
        </div>
      ) : (
        <span className="max-w-[132px] truncate pr-1 text-sm font-semibold tracking-[-0.01em] text-slate-800">
          {state.brand.companyName}
        </span>
      )}
    </div>
  );
}

function ResetDialog() {
  const { resetDemo } = useDemo();
  return (
    <Dialog>
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            className="min-h-11 w-full justify-start rounded-xl px-3 text-sm text-slate-500"
          />
        }
      >
        <RotateCcw data-icon="inline-start" /> Réinitialiser la démo
      </DialogTrigger>
      <DialogContent
        showCloseButton={false}
        className="max-w-[440px] rounded-[26px] p-6"
      >
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">
            Revenir à la démonstration initiale ?
          </DialogTitle>
          <DialogDescription className="text-[15px] leading-6">
            Le logo, les préférences, les scénarios et l’historique créés dans
            ce navigateur seront remplacés par les données fictives de départ.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="-mx-6 -mb-6 mt-3 rounded-b-[26px] px-6">
          <DialogClose
            render={<Button variant="outline" className="h-11 rounded-full" />}
          >
            Garder mon état
          </DialogClose>
          <DialogClose
            render={
              <Button className="h-11 rounded-full" onClick={resetDemo} />
            }
          >
            Réinitialiser
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { state, hydrated, toast, dismissToast, setCopilotOpen } = useDemo();
  const contentRef = React.useRef<HTMLDivElement>(null);
  const previousPath = React.useRef(pathname);
  const hasStickyDecisionBar = pathname.startsWith('/simulations/atlas');
  const pageLabel =
    pageLabels.find(([path]) =>
      path === '/' ? pathname === '/' : pathname.startsWith(path),
    )?.[1] ?? 'Mon cockpit';

  React.useEffect(() => {
    document.title = `${pageLabel} · ${state.brand.companyName}`;
    if (previousPath.current !== pathname) {
      window.scrollTo({ top: 0, behavior: 'instant' });
      contentRef.current?.focus({ preventScroll: true });
      previousPath.current = pathname;
    }
  }, [pathname, pageLabel, state.brand.companyName]);

  const brandStyle = {
    '--brand': state.brand.palette.deep,
    '--brand-accent': state.brand.palette.accent,
    '--brand-deep': state.brand.palette.deep,
    '--brand-soft': state.brand.palette.soft,
    '--primary': state.brand.palette.deep,
    '--ring': state.brand.palette.deep,
    '--secondary': state.brand.palette.soft,
    '--secondary-foreground': state.brand.palette.deep,
    '--accent': state.brand.palette.soft,
    '--accent-foreground': state.brand.palette.deep,
    '--sidebar-primary': state.brand.palette.deep,
    '--sidebar-ring': state.brand.palette.deep,
    '--sidebar-accent': state.brand.palette.soft,
    '--sidebar-accent-foreground': state.brand.palette.deep,
  } as React.CSSProperties;

  React.useEffect(() => {
    const root = document.documentElement;
    const tokens: Record<string, string> = {
      '--brand': state.brand.palette.deep,
      '--brand-accent': state.brand.palette.accent,
      '--brand-deep': state.brand.palette.deep,
      '--brand-soft': state.brand.palette.soft,
      '--primary': state.brand.palette.deep,
      '--ring': state.brand.palette.deep,
      '--secondary': state.brand.palette.soft,
      '--secondary-foreground': state.brand.palette.deep,
      '--accent': state.brand.palette.soft,
      '--accent-foreground': state.brand.palette.deep,
      '--sidebar-primary': state.brand.palette.deep,
      '--sidebar-ring': state.brand.palette.deep,
      '--sidebar-accent': state.brand.palette.soft,
      '--sidebar-accent-foreground': state.brand.palette.deep,
    };

    Object.entries(tokens).forEach(([name, value]) =>
      root.style.setProperty(name, value),
    );
  }, [
    state.brand.palette.accent,
    state.brand.palette.deep,
    state.brand.palette.soft,
  ]);

  return (
    <SidebarProvider
      style={
        { '--sidebar-width': '15rem', ...brandStyle } as React.CSSProperties
      }
      className="min-h-screen"
    >
      <a href="#cockpit-content" className="skip-link">
        Aller au contenu
      </a>
      <Sidebar
        collapsible="offcanvas"
        className="border-r-0 bg-transparent p-4 pr-1"
      >
        <div className="nav-island flex size-full flex-col rounded-[28px]">
          <SidebarHeader className="px-5 pb-3 pt-5">
            <SidebarDestination
              href="/"
              aria-label="Revenir à l’accueil"
              className="rounded-[18px]"
            >
              <BrandMark />
            </SidebarDestination>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup className="px-3 pt-5">
              <SidebarGroupContent>
                <SidebarMenu className="gap-1">
                  {navigation.map(({ label, href, icon: Icon }) => (
                    <SidebarMenuItem key={href}>
                      <SidebarMenuButton
                        size="lg"
                        isActive={isActive(pathname, href)}
                        render={
                          <SidebarDestination
                            href={href}
                            aria-current={
                              isActive(pathname, href) ? 'page' : undefined
                            }
                          />
                        }
                        className="min-h-12 rounded-[18px] px-3.5 text-[15px] transition data-active:bg-white/88 data-active:text-[var(--brand-deep)] data-active:shadow-[0_10px_24px_rgba(54,63,104,.1)]"
                      >
                        <Icon />
                        <span>{label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>

            <SidebarGroup className="mt-3 px-3">
              <SidebarGroupContent>
                <SidebarMenu className="gap-1">
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      size="lg"
                      isActive={pathname.startsWith('/expert')}
                      render={
                        <SidebarDestination
                          href="/expert"
                          aria-current={
                            pathname.startsWith('/expert') ? 'page' : undefined
                          }
                        />
                      }
                      className="min-h-12 rounded-[18px] px-3.5 text-[15px] data-active:bg-white/88 data-active:text-[var(--brand-deep)] data-active:shadow-[0_10px_24px_rgba(54,63,104,.1)]"
                    >
                      <FileSpreadsheet />
                      <span>Mode expert</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      size="lg"
                      isActive={pathname.startsWith('/parcours/installation')}
                      render={
                        <SidebarDestination
                          href="/parcours/installation?mode=review"
                          aria-current={
                            pathname.startsWith('/parcours/installation')
                              ? 'page'
                              : undefined
                          }
                        />
                      }
                      className="min-h-12 rounded-2xl px-3.5 text-[15px]"
                    >
                      <Palette />
                      <span>Personnaliser</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter className="gap-1 px-3 pb-4">
            <SidebarDestination
              href="/decisions"
              className="reference-mini-card mx-1 flex min-h-14 items-center gap-3 rounded-[18px] px-3"
            >
              <span className="grid size-9 shrink-0 place-items-center rounded-[13px] bg-white/72 text-[var(--brand-deep)] shadow-sm">
                <History className="size-4" />
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-semibold text-slate-700">
                  Version officielle
                </span>
                <span className="block truncate text-[12px] text-slate-500">
                  {state.referenceVersions[0]?.label}
                </span>
              </span>
            </SidebarDestination>
            <ResetDialog />
          </SidebarFooter>
        </div>
      </Sidebar>

      <SidebarInset className="min-w-0 bg-transparent pb-20 md:pb-0">
        <header className="sticky top-0 z-20 bg-transparent px-3 py-3 sm:px-6 lg:px-8 xl:px-12">
          <div className="top-island flex min-h-[62px] items-center justify-between rounded-[22px] px-3 sm:px-5">
            <div className="top-leading-cluster flex min-w-0 items-center gap-2.5">
              <SidebarTrigger
                aria-label="Ouvrir la navigation"
                className="liquid-control top-glass-control size-11 shrink-0 rounded-full md:hidden"
              />
              <Link
                href="/"
                aria-label="Revenir à l’accueil"
                className="mobile-brand-capsule top-glass-control min-w-0 rounded-full px-2 py-1.5 md:hidden"
              >
                <BrandMark compact />
              </Link>
              <div className="top-glass-control hidden rounded-[22px] px-4 py-2.5 md:block">
                <p className="text-[13px] font-semibold uppercase tracking-[0.13em] text-[var(--brand)]">
                  {pageLabel}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Votre espace de décision
                </p>
              </div>
            </div>
            <div className="top-trailing-cluster flex shrink-0 items-center gap-2">
              <span className="top-glass-control pointer-events-none hidden rounded-full px-3 py-2 text-[12px] font-semibold text-slate-500 sm:inline-flex">
                <span>Données de démonstration</span>
              </span>
            </div>
          </div>
        </header>

        <div className="mx-auto w-full max-w-[1380px] px-4 pb-10 pt-4 sm:px-7 lg:px-10 lg:pb-14 lg:pt-7 xl:px-14">
          <div
            key={pathname}
            id="cockpit-content"
            ref={contentRef}
            tabIndex={-1}
            className="route-stage outline-none"
            aria-label={pageLabel}
          >
            {hydrated ? children : (
              <div aria-busy="true" className="rounded-[30px] border border-white/80 bg-white/55 p-6">
                <output className="block text-slate-600">Nous retrouvons votre espace…</output>
                <div aria-hidden="true" className="mt-6 h-64 rounded-[24px] bg-white/55" />
              </div>
            )}
          </div>
        </div>
      </SidebarInset>

      {pathname !== '/' ? (
        <button
          aria-label="Ouvrir votre compagnon"
          onClick={() => setCopilotOpen(true)}
          className={`companion-trigger copilot-orbit liquid-control fixed right-4 z-40 flex size-14 items-center justify-center rounded-full p-0 sm:right-7 ${
            hasStickyDecisionBar
              ? 'bottom-4 md:bottom-[118px]'
              : 'bottom-4 md:bottom-7'
          }`}
        >
          <CompanionBadge size="small" shape="round" motion="awake" />
          <span className="sr-only">Demander à votre compagnon</span>
        </button>
      ) : null}

      {toast ? (
        <output
          aria-live="polite"
          className="cockpit-toast fixed left-1/2 top-24 z-[80] flex w-[min(92vw,520px)] -translate-x-1/2 items-center gap-3 rounded-[22px] border border-white bg-white/95 py-3 pl-5 pr-2 text-sm font-medium text-slate-800 shadow-xl backdrop-blur-2xl"
        >
          <span className="min-w-0 flex-1">{toast}</span>
          <button
            type="button"
            onClick={dismissToast}
            aria-label="Fermer le message"
            className="grid size-11 shrink-0 place-items-center rounded-full hover:bg-slate-100"
          >
            <X className="size-4" />
          </button>
        </output>
      ) : null}

      <ImpactSheet />
      <CopilotSheet />
    </SidebarProvider>
  );
}
