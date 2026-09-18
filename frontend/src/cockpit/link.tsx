import { forwardRef, type AnchorHTMLAttributes } from 'react';
import { useHref, useRouter } from './router';

type Props = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> & {
  href: string; replace?: boolean; scroll?: boolean; prefetch?: boolean;
};
const Link = forwardRef<HTMLAnchorElement, Props>(function Link({ href, replace, scroll, prefetch: _prefetch, onClick, ...props }, ref) {
  const url = useHref()(href), router = useRouter();
  return <a {...props} ref={ref} href={url} onClick={event => {
    onClick?.(event);
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || props.target === '_blank' || props.download) return;
    if (!href.startsWith('/') || href.startsWith('//')) return;
    event.preventDefault();
    router[replace ? 'replace' : 'push'](href, { scroll });
  }} />;
});
export default Link;
