import { createContext, useContext, useMemo, useSyncExternalStore, type ReactNode } from 'react';

// The visual prototype only needs client navigation. Keeping the same small
// interface lets its pages run as static assets served by the local Python API.
const BasePath = createContext('');
const HISTORY_KEY = '__tca_cockpit_index';
let historyIndex = 0, committedHref = '', revertingHistory = false;
if (typeof window !== 'undefined') {
  historyIndex = Number.isInteger(window.history.state?.[HISTORY_KEY]) ? window.history.state[HISTORY_KEY] : 0;
  committedHref = window.location.href;
  window.history.replaceState({ ...window.history.state, [HISTORY_KEY]: historyIndex }, '', committedHref);
  window.addEventListener('popstate', () => {
    if (revertingHistory) { revertingHistory = false; return; }
    const destination = window.location.href;
    const targetIndex = window.history.state?.[HISTORY_KEY];
    const before = new CustomEvent('cockpit:before-navigation', { cancelable: true, detail: { href: destination, history: true } });
    if (!window.dispatchEvent(before)) {
      if (Number.isInteger(targetIndex) && targetIndex !== historyIndex) {
        revertingHistory = true;
        window.history.go(historyIndex - targetIndex);
      } else {
        window.history.pushState({ [HISTORY_KEY]: historyIndex }, '', committedHref);
      }
      return;
    }
    historyIndex = Number.isInteger(targetIndex) ? targetIndex : 0;
    committedHref = destination;
    window.history.replaceState({ ...window.history.state, [HISTORY_KEY]: historyIndex }, '', destination);
    window.dispatchEvent(new Event('cockpit:navigation'));
  });
}
export function RouterProvider({ children, basePath = '' }: { children: ReactNode; basePath?: string }) {
  return <BasePath.Provider value={basePath.replace(/\/$/, '')}>{children}</BasePath.Provider>;
}
function subscribe(callback: () => void) {
  window.addEventListener('cockpit:navigation', callback);
  return () => {
    window.removeEventListener('cockpit:navigation', callback);
  };
}
function locationSnapshot() { return window.location.pathname + window.location.search + window.location.hash; }
export function useLocation() { return useSyncExternalStore(subscribe, locationSnapshot, () => '/'); }
export function usePathname() {
  useLocation();
  const base = useContext(BasePath);
  const pathname = window.location.pathname;
  return base && (pathname === base || pathname.startsWith(base + '/')) ? pathname.slice(base.length) || '/' : pathname;
}
export function useSearchParams() {
  const location = useLocation();
  return useMemo(() => new URLSearchParams(new URL(location, window.location.origin).search), [location]);
}
export function useHref() {
  const base = useContext(BasePath);
  return (href: string) => href.startsWith('/') && !href.startsWith('//') ? base + href : href;
}
export function useRouter() {
  const base = useContext(BasePath);
  return useMemo(() => {
    const navigate = (href: string, replace = false, options?: { scroll?: boolean }) => {
      const destination = new URL(href.startsWith('/') && !href.startsWith('//') ? base + href : href, window.location.href);
      if (destination.origin !== window.location.origin) throw new Error('La navigation du cockpit doit rester locale.');
      const event = new CustomEvent('cockpit:before-navigation', { cancelable: true, detail: { href: destination.href, history: false } });
      if (!window.dispatchEvent(event)) return;
      if (!replace) historyIndex += 1;
      committedHref = destination.href;
      window.history[replace ? 'replaceState' : 'pushState']({ ...(replace ? window.history.state : {}), [HISTORY_KEY]: historyIndex }, '', destination);
      window.dispatchEvent(new Event('cockpit:navigation'));
      if (options?.scroll !== false) window.scrollTo({ top: 0, behavior: 'instant' });
    };
    return {
      push: (href: string, options?: { scroll?: boolean }) => navigate(href, false, options),
      replace: (href: string, options?: { scroll?: boolean }) => navigate(href, true, options),
      back: () => window.history.back(),
      forward: () => window.history.forward(),
      refresh: () => window.dispatchEvent(new Event('cockpit:navigation')),
      prefetch: (_href: string) => Promise.resolve(),
    };
  }, [base]);
}
