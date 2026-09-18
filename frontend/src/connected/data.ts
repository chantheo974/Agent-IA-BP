import { useEffect, useState } from 'react';
import { api, casePath, errorText } from '../api';

export function useCaseData<T>(caseId: string, path: string, version: string | number, keepPrevious = false) {
  const [value, setValue] = useState<{ caseId: string; path: string; version: string | number; data: T } | null>(null);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    const abort = new AbortController();
    setError('');
    if (!caseId) { setValue(null); setLoading(false); return () => abort.abort(); }
    setLoading(true);
    void api<T>(casePath(caseId) + path, 'GET', undefined, abort.signal)
      .then(data => { if (!abort.signal.aborted) setValue({ caseId, path, version, data }); })
      .catch(e => { if (!abort.signal.aborted) setError(errorText(e)); })
      .finally(() => { if (!abort.signal.aborted) setLoading(false); });
    return () => abort.abort();
  }, [caseId, path, version, attempt]);
  return { data: value?.caseId === caseId && value.path === path && (keepPrevious || value.version === version) ? value.data : null, loading, error, retry: () => setAttempt(n => n + 1) };
}
export function textValue(value: unknown): string {
  if (value == null || value === '') return 'À compléter';
  if (typeof value === 'number') return Number.isFinite(value) ? value.toLocaleString('fr-FR', { maximumFractionDigits: 2 }) : 'Indisponible';
  if (typeof value === 'boolean') return value ? 'Oui' : 'Non';
  if (Array.isArray(value)) return value.map(textValue).join(' · ');
  if (typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key} : ${textValue(item)}`).join(' · ');
  return String(value);
}
export function choiceValue(choice: unknown) {
  return typeof choice === 'object' && choice !== null ? String((choice as { value?: unknown }).value ?? '') : String(choice);
}
