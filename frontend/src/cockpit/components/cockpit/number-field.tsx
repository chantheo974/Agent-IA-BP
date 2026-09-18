'use client';

import * as React from 'react';
import { Input } from '@/components/ui/input';

/** Keep incomplete keystrokes out of the financial draft. */
export function NumberField({
  value,
  onCommit,
  min = 0,
  max,
  step = 1,
  ...props
}: Omit<
  React.ComponentProps<typeof Input>,
  'value' | 'onChange' | 'min' | 'max' | 'step'
> & {
  value: number;
  onCommit: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
}) {
  const [editing, setEditing] = React.useState<string | null>(null);
  const [error, setError] = React.useState('');
  const errorId = React.useId();
  const commit = () => {
    if (editing === null) return;
    const next = Number(editing);
    const valid =
      editing.trim() !== '' &&
      Number.isFinite(next) &&
      next >= min &&
      (max === undefined || next <= max);
    if (valid) {
      if (next !== value) onCommit(next);
      setError('');
    } else {
      setError(
        `Saisissez un nombre ${max === undefined ? `d’au moins ${min.toLocaleString('fr-FR')}` : `entre ${min} et ${max}`}. La dernière valeur valide est conservée.`,
      );
    }
    setEditing(null);
  };
  return (
    <>
      <Input
        {...props}
        type="number"
        inputMode="decimal"
        min={min}
        max={max}
        step={step}
        value={editing ?? value}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : props['aria-describedby']}
        onChange={(event) => {
          setEditing(event.target.value);
          setError('');
        }}
        onBlur={commit}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            event.preventDefault();
            commit();
          }
          if (event.key === 'Escape') {
            setEditing(null);
            setError('');
          }
        }}
      />
      {error ? (
        <span
          id={errorId}
          role="alert"
          className="mt-2 block text-sm leading-6 text-[#9a3b39]"
        >
          {error}
        </span>
      ) : null}
    </>
  );
}
