import * as React from 'react';

import { Badge } from '@/components/ui/badge';
import type { SiteIconComponent } from '@/components/ui/site-icon';
import { cn } from '@/lib/utils';

export function PageHeading({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow: string;
  title: string;
  description: string;
  actions?: React.ReactNode;
}) {
  return (
    <header className="page-heading flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
      <div className="min-w-0 max-w-3xl">
        <p className="text-[13px] font-semibold uppercase tracking-[0.13em] text-[var(--brand)]">
          {eyebrow}
        </p>
        <h1 className="mt-2 text-[clamp(1.8rem,3vw,2.65rem)] font-semibold leading-[1.12] tracking-[-0.035em] text-[#17203a]">
          {title}
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-slate-500">
          {description}
        </p>
      </div>
      {actions ? (
        <div className="page-heading-actions flex flex-wrap gap-2">
          {actions}
        </div>
      ) : null}
    </header>
  );
}

export function Surface({
  className,
  children,
  variant = 'solid',
  depth = 1,
  ...props
}: React.ComponentProps<'section'> & {
  variant?: 'solid' | 'glass' | 'tinted' | 'floating';
  depth?: 0 | 1 | 2 | 3;
}) {
  return (
    <section
      className={cn(
        'spatial-surface rounded-[30px] p-5 sm:p-6',
        `spatial-surface--${variant}`,
        `spatial-depth-${depth}`,
        className,
      )}
      {...props}
    >
      {children}
    </section>
  );
}

export function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = 'brand',
  className,
}: {
  label: string;
  value: string;
  detail: string;
  icon: SiteIconComponent;
  tone?: 'brand' | 'success' | 'warning' | 'danger';
  className?: string;
}) {
  const tones = {
    brand: 'bg-[var(--brand-soft)] text-[var(--brand-deep)]',
    success: 'bg-[#e4f7f0] text-[#08795e]',
    warning: 'bg-[#fff3dc] text-[#9b6009]',
    danger: 'bg-[#ffe8eb] text-[#ad334a]',
  };

  return (
    <article
      className={cn(
        'spatial-surface spatial-surface--floating rounded-[28px] p-5',
        className,
      )}
    >
      <span
        className={cn(
          'grid size-11 place-items-center rounded-[15px]',
          tones[tone],
        )}
      >
        <Icon className="size-5" />
      </span>
      <p className="mt-5 text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-[1.75rem] font-semibold tracking-[-0.04em] text-slate-900">
        {value}
      </p>
      <p className="mt-1 text-[13px] leading-5 text-slate-500">{detail}</p>
    </article>
  );
}

export function SpatialCluster({
  className,
  children,
  ...props
}: React.ComponentProps<'section'>) {
  return (
    <section className={cn('spatial-cluster', className)} {...props}>
      {children}
    </section>
  );
}

export function CardStack({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div className={cn('spatial-cluster', className)} {...props}>
      {children}
    </div>
  );
}

export function FloatingBubble({
  className,
  children,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div className={cn('floating-bubble px-4 py-2.5', className)} {...props}>
      {children}
    </div>
  );
}

export function StateBadge({
  children,
  tone = 'brand',
}: {
  children: React.ReactNode;
  tone?: 'brand' | 'success' | 'warning' | 'neutral' | 'danger';
}) {
  const tones = {
    brand: 'bg-[var(--brand-soft)] text-[var(--brand-deep)]',
    success: 'bg-[#e4f7f0] text-[#08795e]',
    warning: 'bg-[#fff3dc] text-[#8e580a]',
    neutral: 'bg-slate-100 text-slate-600',
    danger: 'bg-[#ffe8eb] text-[#ad334a]',
  };

  return (
    <Badge
      className={cn(
        'status-label h-auto min-h-7 max-w-full shrink whitespace-normal rounded-xl border-0 px-2.5 py-1 text-left text-[13px] font-medium',
        tones[tone],
      )}
    >
      {children}
    </Badge>
  );
}

export function Delta({
  children,
  tone,
}: {
  children: React.ReactNode;
  tone: 'positive' | 'negative' | 'neutral';
}) {
  return (
    <span
      className={cn(
        'inline-flex rounded-full px-2.5 py-1 text-[12px] font-semibold',
        tone === 'positive' && 'bg-[#e4f7f0] text-[#08795e]',
        tone === 'negative' && 'bg-[#ffe8eb] text-[#ad334a]',
        tone === 'neutral' && 'bg-slate-100 text-slate-600',
      )}
    >
      {children}
    </span>
  );
}

export type CashCurvePoint = {
  label: string;
  value: number;
};

const DEFAULT_CASH_CURVE_POINTS: CashCurvePoint[] = [
  { label: 'Octobre 2026', value: 245_000 },
  { label: 'Novembre 2026', value: 260_000 },
  { label: 'Décembre 2026', value: 235_000 },
  { label: 'Janvier 2027', value: 190_000 },
  { label: 'Février 2027', value: 130_000 },
  { label: 'Mars 2027', value: 75_000 },
  { label: 'Avril 2027', value: 105_000 },
  { label: 'Mai 2027', value: 170_000 },
  { label: 'Juin 2027', value: 225_000 },
  { label: 'Juillet 2027', value: 245_000 },
];

const IMPROVED_CASH_CURVE_POINTS: CashCurvePoint[] = [
  { label: 'Octobre 2026', value: 210_000 },
  { label: 'Novembre 2026', value: 235_000 },
  { label: 'Décembre 2026', value: 260_000 },
  { label: 'Janvier 2027', value: 245_000 },
  { label: 'Février 2027', value: 220_000 },
  { label: 'Mars 2027', value: 180_000 },
  { label: 'Avril 2027', value: 230_000 },
  { label: 'Mai 2027', value: 300_000 },
  { label: 'Juin 2027', value: 335_000 },
  { label: 'Juillet 2027', value: 360_000 },
];

function formatCashLevel(value: number) {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} M€`;
  }

  return `${Math.round(value / 1_000).toLocaleString('fr-FR')} k€`;
}

function buildSmoothCashPath(points: Array<{ x: number; y: number }>) {
  if (points.length === 0) return '';
  if (points.length === 1) return `M${points[0].x} ${points[0].y}`;

  return points.slice(1).reduce((path, point, index) => {
    const previous = points[index];
    const controlX = (previous.x + point.x) / 2;
    return `${path} C${controlX} ${previous.y},${controlX} ${point.y},${point.x} ${point.y}`;
  }, `M${points[0].x} ${points[0].y}`);
}

export function CashCurve({
  improved = false,
  points,
  cashLowPoint,
  ariaLabel,
  domain,
}: {
  improved?: boolean;
  points?: CashCurvePoint[];
  cashLowPoint?: number;
  ariaLabel?: string;
  domain?: readonly [number, number];
}) {
  const areaGradientId = React.useId();
  const lineGradientId = React.useId();
  const instructionId = React.useId();
  const [activeIndex, setActiveIndex] = React.useState<number | null>(null);
  const curvePoints = React.useMemo(() => {
    // Explicitly supplied empty/invalid observations must not become a demo
    // curve. The prepared curves below belong only to the demonstration pages.
    if (points !== undefined) return points.filter(point => Number.isFinite(point.value));

    const template = improved
      ? IMPROVED_CASH_CURVE_POINTS
      : DEFAULT_CASH_CURVE_POINTS;
    if (cashLowPoint === undefined) return template;

    const templateLowPoint = Math.min(...template.map((point) => point.value));
    const adjustment = cashLowPoint - templateLowPoint;
    return template.map((point) => ({
      ...point,
      value: point.value + adjustment,
    }));
  }, [cashLowPoint, improved, points]);
  const chartPoints = React.useMemo(() => {
    const values = curvePoints.map((point) => point.value);
    const minimum = domain?.[0] ?? Math.min(...values);
    const maximum = domain?.[1] ?? Math.max(...values);
    const range = Math.max(maximum - minimum, 1);

    return curvePoints.map((point, index) => ({
      x:
        curvePoints.length === 1
          ? 130
          : 8 + (244 * index) / (curvePoints.length - 1),
      y: 18 + ((maximum - point.value) / range) * 52,
    }));
  }, [curvePoints, domain]);
  const isInteractive = curvePoints.length > 1;
  const minimumIndex = React.useMemo(() => {
    return curvePoints.reduce(
      (lowestIndex, point, index) =>
        point.value < curvePoints[lowestIndex].value ? index : lowestIndex,
      0,
    );
  }, [curvePoints]);
  const resolvedIndex = Math.min(
    activeIndex ?? minimumIndex,
    curvePoints.length - 1,
  );
  const line = buildSmoothCashPath(chartPoints);
  const area = `${line} L${chartPoints.at(-1)?.x ?? 252} 86 L${chartPoints[0]?.x ?? 8} 86 Z`;
  const activePoint = activeIndex === null ? null : curvePoints[resolvedIndex];
  const activeCoordinate =
    activeIndex === null ? null : chartPoints[resolvedIndex];

  const selectFromPointer = (clientX: number, element: HTMLElement) => {
    if (curvePoints.length < 2) return;
    const bounds = element.getBoundingClientRect();
    const ratio = Math.min(
      1,
      Math.max(0, (clientX - bounds.left) / bounds.width),
    );
    setActiveIndex(Math.round(ratio * (curvePoints.length - 1)));
  };

  if (!curvePoints.length) return <p className="rounded-xl border p-4 text-sm text-slate-500">Aucune série mensuelle disponible pour cette version.</p>;

  const chart = (
    <svg
      viewBox="0 0 260 90"
      preserveAspectRatio="none"
      aria-hidden={isInteractive ? true : undefined}
      aria-label={
        isInteractive
          ? undefined
          : (ariaLabel ??
            (improved
              ? 'Courbe de trésorerie améliorée après modification des conditions de paiement'
              : 'Courbe de trésorerie montrant un creux temporaire avant encaissement'))
      }
      className="cash-curve-svg h-[90px] w-full"
    >
      <defs>
        <linearGradient id={lineGradientId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={improved ? '#20b98b' : '#36c8a0'} />
          <stop offset="42%" stopColor="#5f79ee" />
          <stop offset="68%" stopColor="#9882e8" />
          <stop offset="100%" stopColor={improved ? '#ecaa72' : '#ed8c88'} />
        </linearGradient>
        <linearGradient id={areaGradientId} x1="0" x2="0" y1="0" y2="1">
          <stop
            offset="0%"
            stopColor={improved ? '#54d3ad' : '#6bd8bd'}
            stopOpacity="0.28"
          />
          <stop offset="48%" stopColor="#8094f5" stopOpacity="0.19" />
          <stop offset="74%" stopColor="#c5a7ed" stopOpacity="0.14" />
          <stop
            offset="100%"
            stopColor={improved ? '#f4c696' : '#f3aaa5'}
            stopOpacity="0.03"
          />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#${areaGradientId})`} />
      <path
        d={line}
        fill="none"
        stroke={`url(#${lineGradientId})`}
        strokeWidth="9"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
        opacity="0.13"
      />
      <path
        d={line}
        fill="none"
        stroke={`url(#${lineGradientId})`}
        strokeWidth="3.4"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
      <line
        x1="8"
        x2="252"
        y1="78"
        y2="78"
        stroke="#cbd2df"
        strokeDasharray="4 5"
        vectorEffect="non-scaling-stroke"
      />
      {isInteractive
        ? chartPoints.map((point, index) => (
            <circle
              key={`${curvePoints[index].label}-${index}`}
              cx={point.x}
              cy={point.y}
              r="2.6"
              fill="white"
              stroke="var(--brand)"
              strokeWidth="1.25"
              vectorEffect="non-scaling-stroke"
              opacity="0.9"
            />
          ))
        : null}
      {activeCoordinate ? (
        <g aria-hidden="true">
          <line
            x1={activeCoordinate.x}
            x2={activeCoordinate.x}
            y1="10"
            y2="78"
            stroke="var(--brand)"
            strokeDasharray="2.5 3.5"
            strokeWidth="1"
            vectorEffect="non-scaling-stroke"
            opacity="0.42"
          />
          <circle
            cx={activeCoordinate.x}
            cy={activeCoordinate.y}
            r="8"
            fill="var(--brand-soft)"
            opacity="0.82"
          />
          <circle
            cx={activeCoordinate.x}
            cy={activeCoordinate.y}
            r="4"
            fill="white"
            stroke="var(--brand)"
            strokeWidth="2.25"
            vectorEffect="non-scaling-stroke"
          />
        </g>
      ) : null}
    </svg>
  );

  if (!isInteractive) return chart;

  const tooltipLeft = activeCoordinate ? (activeCoordinate.x / 260) * 100 : 50;
  const tooltipTop = activeCoordinate ? (activeCoordinate.y / 90) * 100 : 50;
  const placeTooltipBelow = Boolean(
    activeCoordinate && activeCoordinate.y < 34,
  );
  const tooltipAlignment =
    tooltipLeft < 24 ? 'start' : tooltipLeft > 76 ? 'end' : 'center';

  return (
    <div className="cash-curve-interactive">
      {chart}
      <input
        type="range"
        min={0}
        max={curvePoints.length - 1}
        step={1}
        value={resolvedIndex}
        aria-label={
          ariaLabel ?? 'Évolution mensuelle de la trésorerie prévisionnelle'
        }
        aria-describedby={instructionId}
        aria-valuetext={`${curvePoints[resolvedIndex].label} : ${formatCashLevel(curvePoints[resolvedIndex].value)}`}
        className="cash-curve-range"
        onChange={(event) => setActiveIndex(Number(event.currentTarget.value))}
        onFocus={() => setActiveIndex((current) => current ?? minimumIndex)}
        onBlur={() => setActiveIndex(null)}
        onPointerDown={(event) =>
          selectFromPointer(event.clientX, event.currentTarget)
        }
        onPointerMove={(event) => {
          if (event.pointerType === 'mouse' || event.buttons > 0) {
            selectFromPointer(event.clientX, event.currentTarget);
          }
        }}
        onPointerLeave={(event) => {
          if (event.pointerType === 'mouse') setActiveIndex(null);
        }}
      />
      <span id={instructionId} className="sr-only">
        Survolez ou touchez la courbe. Au clavier, utilisez les flèches pour
        parcourir les mois.
      </span>
      <span className="sr-only">
        Prévision simulée :{' '}
        {curvePoints
          .map((point) => `${point.label}, ${formatCashLevel(point.value)}`)
          .join(' ; ')}
        .
      </span>
      {activePoint && activeCoordinate ? (
        <output
          aria-live="polite"
          className={cn(
            'cash-curve-tooltip',
            `cash-curve-tooltip--${tooltipAlignment}`,
            placeTooltipBelow
              ? 'cash-curve-tooltip--below'
              : 'cash-curve-tooltip--above',
          )}
          style={{
            ...(tooltipAlignment === 'end'
              ? { right: '0.5rem' }
              : {
                  left:
                    tooltipAlignment === 'start' ? '0.5rem' : `${tooltipLeft}%`,
                }),
            top: `${tooltipTop}%`,
          }}
        >
          <span>{activePoint.label}</span>
          <strong>{formatCashLevel(activePoint.value)}</strong>
        </output>
      ) : null}
    </div>
  );
}
