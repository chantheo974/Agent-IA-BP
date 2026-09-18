import * as React from 'react';

import { cn } from '@/lib/utils';

type CompanionMarkProps = Omit<React.SVGProps<SVGSVGElement>, 'children'> & {
  title?: string;
};

export function CompanionMark({
  className,
  title,
  ...props
}: CompanionMarkProps) {
  const bodyClipId = React.useId();
  const bodyGradientId = React.useId();
  const veinGradientId = React.useId();
  const pearlGradientId = React.useId();
  const sheenGradientId = React.useId();
  const rimGradientId = React.useId();
  const bodyPath =
    'M21.6 4.6C29.2 3.5 35.6 7.4 38.3 13.2C39.1 11.6 41 10.8 42.5 11.6C44.5 12.6 44.6 15.5 43.2 17.2C42.1 18.6 40.8 19 39.5 18.9C41.4 26.7 38.1 35.6 31.5 40.1C24.7 44.7 15.2 43.8 9.6 38C4.2 32.4 3.7 23.3 7.7 16.3C10.7 10.8 15.8 5.5 21.6 4.6Z';
  const veinPath =
    'M3 37C11.5 27.2 18.3 29.5 25.6 33.2C33.6 37.3 39 31.8 46 25.7';

  return (
    <svg
      {...props}
      viewBox="0 0 48 48"
      fill="none"
      focusable="false"
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
      className={cn('companion-mark', className)}
    >
      {title ? <title>{title}</title> : null}
      <defs>
        <clipPath id={bodyClipId}>
          <path d={bodyPath} />
        </clipPath>
        <linearGradient
          id={bodyGradientId}
          x1="8"
          y1="8"
          x2="39"
          y2="41"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#a7b5ff" />
          <stop offset="0.3" stopColor="var(--brand)" />
          <stop offset="0.6" stopColor="#737bdb" />
          <stop offset="1" stopColor="#86dcca" />
        </linearGradient>
        <linearGradient
          id={veinGradientId}
          x1="8"
          y1="31"
          x2="41"
          y2="29"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#9beae1" />
          <stop offset="0.32" stopColor="#b8bbff" />
          <stop offset="0.58" stopColor="#edc7fa" />
          <stop offset="0.8" stopColor="#ffd9c7" />
          <stop offset="1" stopColor="#b0fff0" />
        </linearGradient>
        <radialGradient id={pearlGradientId}>
          <stop stopColor="#e6fff8" stopOpacity="0.96" />
          <stop offset="0.4" stopColor="#84e6d5" stopOpacity="0.76" />
          <stop offset="0.74" stopColor="#d4bdff" stopOpacity="0.38" />
          <stop offset="1" stopColor="#d4bdff" stopOpacity="0" />
        </radialGradient>
        <radialGradient
          id={sheenGradientId}
          cx="0.32"
          cy="0.18"
          r="0.8"
        >
          <stop stopColor="white" stopOpacity="0.68" />
          <stop offset="0.36" stopColor="#e7eeff" stopOpacity="0.24" />
          <stop offset="0.66" stopColor="white" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={rimGradientId} x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="white" stopOpacity="0.95" />
          <stop offset="0.3" stopColor="#dadfff" stopOpacity="0.36" />
          <stop offset="0.65" stopColor="#fff0ff" stopOpacity="0.72" />
          <stop offset="1" stopColor="#beffed" stopOpacity="0.96" />
        </linearGradient>
      </defs>

      <g className="companion-mark__form">
        <path
          d={bodyPath}
          fill={`url(#${bodyGradientId})`}
          className="companion-mark__body"
        />
        <g clipPath={`url(#${bodyClipId})`}>
          <ellipse
            cx="29"
            cy="37"
            rx="24"
            ry="14"
            fill={`url(#${pearlGradientId})`}
            className="companion-mark__pearl"
          />
          <g className="companion-mark__vein">
            <path
              d={veinPath}
              stroke={`url(#${veinGradientId})`}
              strokeWidth="10.5"
              strokeLinecap="round"
              opacity="0.7"
              className="companion-mark__vein-color"
            />
            <path
              d={veinPath}
              stroke="rgba(255,255,255,.82)"
              strokeWidth="1.2"
              strokeLinecap="round"
              pathLength="1"
              strokeDasharray="0.22 0.78"
              className="companion-mark__flow"
            />
          </g>
          <ellipse
            cx="21"
            cy="9.5"
            rx="17"
            ry="11"
            fill={`url(#${sheenGradientId})`}
            className="companion-mark__sheen"
          />
        </g>
        <path
          d={bodyPath}
          stroke={`url(#${rimGradientId})`}
          strokeWidth="1.25"
        />
        <path
          d={bodyPath}
          stroke="rgba(255,255,255,.92)"
          strokeWidth="1.65"
          strokeLinecap="round"
          pathLength="1"
          strokeDasharray="0.14 0.86"
          className="companion-mark__rim-light"
        />

        <g className="companion-mark__face">
          <g className="companion-mark__eyes">
            <rect x="17.7" y="17.9" width="3.1" height="4.4" rx="1.55" />
            <rect x="25.4" y="17.4" width="3.1" height="4.4" rx="1.55" />
          </g>
          <path
            d="M19.1 25C21.2 27.5 25.2 27.6 27.7 24.8"
            stroke="currentColor"
            strokeWidth="1.65"
            strokeLinecap="round"
            className="companion-mark__smile"
          />
        </g>
        <g className="companion-mark__ear">
          <circle cx="40.1" cy="14.7" r="2.6" fill="rgba(255,255,255,.2)" />
          <circle cx="40.1" cy="14.7" r="1.1" fill="rgba(255,255,255,.92)" />
        </g>
        <path
          d="M12 14.4C14.5 10.5 18.1 8.3 22.3 7.7"
          stroke="rgba(255,255,255,.68)"
          strokeWidth="1.7"
          strokeLinecap="round"
          className="companion-mark__highlight"
        />
      </g>
    </svg>
  );
}

export function CompanionBadge({
  className,
  markClassName,
  size = 'medium',
  shape = 'squircle',
  motion = 'calm',
}: {
  className?: string;
  markClassName?: string;
  size?: 'small' | 'medium' | 'large';
  shape?: 'round' | 'squircle';
  motion?: 'calm' | 'awake' | 'engaged';
}) {
  return (
    <span
      aria-hidden="true"
      data-motion={motion}
      className={cn(
        'companion-badge',
        size === 'small' && 'size-10',
        size === 'medium' && 'size-11',
        size === 'large' && 'size-12',
        shape === 'round' ? 'rounded-full' : 'rounded-[18px]',
        className,
      )}
    >
      <CompanionMark
        className={cn(
          size === 'small' && 'size-[38px]',
          size === 'medium' && 'size-[42px]',
          size === 'large' && 'size-12',
          markClassName,
        )}
      />
    </span>
  );
}
