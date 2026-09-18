import { useEffect, useRef, type ReactNode, type ButtonHTMLAttributes } from "react";

const paths: Record<string, ReactNode> = {
  plus: <path d="M12 5v14M5 12h14"/>, close: <path d="m6 6 12 12M18 6 6 18"/>,
  folder: <path d="M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1v11H3Z"/>,
  file: <><path d="M14 3H5v18h14V8Z"/><path d="M14 3v5h5M8 12h8M8 16h6"/></>,
  table: <><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 9v12M3 15h18"/></>,
  chat: <path d="M20 16a2 2 0 0 1-2 2H8l-5 3V5a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2Z"/>,
  spark: <><path d="m12 3 2.7 6.3L21 12l-6.3 2.7L12 21l-2.7-6.3L3 12l6.3-2.7Z"/><path d="m20 2 .5 1.5L22 4l-1.5.5L20 6l-.5-1.5L18 4l1.5-.5Z"/></>,
  search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
  download: <><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></>,
  upload: <><path d="M12 16V4m-5 5 5-5 5 5M4 16v5h16v-5"/></>,
  refresh: <><path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 6a8 8 0 0 1 13 2M5 16a8 8 0 0 0 13 2"/></>,
  arrow: <path d="M5 12h14m-6-6 6 6-6 6"/>, send: <><path d="m3 3 18 9-18 9 4-9Z"/><path d="M7 12h14"/></>,
  check: <path d="m5 12 4 4L19 6"/>, chevron: <path d="m9 5 7 7-7 7"/>,
  history: <><path d="M3 3v6h6"/><path d="M4 8a9 9 0 1 1-1 7M12 7v5l3 2"/></>,
  settings: <><path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3" fill="currentColor" stroke="none"/><circle cx="16" cy="17" r="3" fill="currentColor" stroke="none"/></>,
  more: <><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,
  info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v1"/></>,
  trash: <><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/></>,
  panel: <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></>,
};
export function Icon({ name, size = 18 }: { name: string; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.info}</svg>;
}
export function Button({ icon, children, className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { icon?: string }) {
  return <button className={"button " + className} {...props}>{icon && <Icon name={icon}/>} {children}</button>;
}
export function PageNavigation({ count, page, onPage, label, size = 200 }: { count: number; page: number; onPage: (page: number) => void; label: string; size?: number }) {
  const pages = Math.ceil(count / size), current = Math.min(page, Math.max(0, pages - 1));
  if (pages <= 1) return null;
  return <nav className="table-pagination" aria-label={"Pages des " + label}><span>{current * size + 1}–{Math.min((current + 1) * size, count)} / {count.toLocaleString("fr-FR")}</span><Button type="button" disabled={current === 0} onClick={() => onPage(current - 1)}>Précédent</Button><label>Page<select aria-label={"Page des " + label} value={current} onChange={event => onPage(Number(event.target.value))}>{Array.from({ length: pages }, (_, index) => <option key={index} value={index}>{index + 1} / {pages}</option>)}</select></label><Button type="button" disabled={current + 1 === pages} onClick={() => onPage(current + 1)}>Suivant</Button></nav>;
}
export function Modal({ title, children, onClose, wide = false }: { title: string; children: ReactNode; onClose: () => void; wide?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { ref.current?.showModal(); }, []);
  return <dialog ref={ref} className={"modal " + (wide ? "wide" : "")} onCancel={onClose} onClick={event => { if (event.target === event.currentTarget) onClose(); }} aria-label={title}>
    <div className="modal-header"><h2>{title}</h2><button className="icon-button" onClick={onClose} aria-label="Fermer"><Icon name="close"/></button></div>
    <div className="modal-content">{children}</div>
  </dialog>;
}
export function Empty({ icon = "folder", title, children }: { icon?: string; title: string; children?: ReactNode }) {
  return <div className="empty"><div className="empty-icon"><Icon name={icon} size={27}/></div><h3>{title}</h3>{children}</div>;
}
export function JsonDetail({ value }: { value: unknown }) {
  if (value == null) return null;
  if (typeof value === "string") return <p className="prewrap">{value}</p>;
  return <pre className="detail-code">{JSON.stringify(value, null, 2)}</pre>;
}
