import * as React from 'react';

import { cn } from '@/lib/utils';

export type SiteIconProps = Omit<React.SVGProps<SVGSVGElement>, 'children'> & {
  size?: number | string;
  title?: string;
};

export type SiteIconComponent = React.ForwardRefExoticComponent<
  SiteIconProps & React.RefAttributes<SVGSVGElement>
>;

function createSiteIcon(
  iconName: string,
  displayName: string,
): SiteIconComponent {
  const Icon = React.forwardRef<SVGSVGElement, SiteIconProps>(
    (
      {
        className,
        size = 24,
        strokeWidth = 1.5,
        title,
        role,
        'aria-label': ariaLabel,
        'aria-hidden': ariaHidden,
        ...props
      },
      ref,
    ) => {
      const isDecorative = ariaHidden ?? (!ariaLabel && !title);

      return (
        <svg
          ref={ref}
          viewBox="0 0 24 24"
          width={size}
          height={size}
          fill="none"
          strokeWidth={strokeWidth}
          focusable="false"
          role={role ?? (isDecorative ? undefined : 'img')}
          aria-label={ariaLabel}
          aria-hidden={isDecorative ? true : undefined}
          data-site-icon={iconName}
          className={cn('shrink-0', className)}
          {...props}
        >
          {title ? <title>{title}</title> : null}
          <use href={`/icone/iconoir-sprite.svg#${iconName}`} />
        </svg>
      );
    },
  );

  Icon.displayName = displayName;
  return Icon;
}

export const ArrowDownRight = createSiteIcon(
  'arrow-down-right',
  'ArrowDownRight',
);
export const ArrowRight = createSiteIcon('arrow-right', 'ArrowRight');
export const BadgeCheck = createSiteIcon('badge-check', 'BadgeCheck');
export const Check = createSiteIcon('check', 'Check');
export const CircleEqual = createSiteIcon('pause', 'CircleEqual');
export const Clock3 = createSiteIcon('clock', 'Clock3');
export const Database = createSiteIcon('database', 'Database');
export const FileSpreadsheet = createSiteIcon('table', 'FileSpreadsheet');
export const Link2 = createSiteIcon('link', 'Link2');
export const ShieldCheck = createSiteIcon('shield-check', 'ShieldCheck');
export const TriangleAlert = createSiteIcon(
  'warning-triangle',
  'TriangleAlert',
);
export const X = createSiteIcon('xmark', 'X');

export const Send = createSiteIcon('send-diagonal', 'Send');
export const Sparkles = createSiteIcon('light-bulb', 'Sparkles');
export const WandSparkles = createSiteIcon('page-edit', 'WandSparkles');

export const FileText = createSiteIcon('page', 'FileText');
export const Gauge = createSiteIcon('dashboard-speed', 'Gauge');
export const History = createSiteIcon('clock-rotate-right', 'History');
export const LayoutDashboard = createSiteIcon('dashboard', 'LayoutDashboard');
export const LineChart = createSiteIcon('graph-up', 'LineChart');
export const Palette = createSiteIcon('palette', 'Palette');
export const Route = createSiteIcon('path-arrow', 'Route');
export const RotateCcw = createSiteIcon('refresh', 'RotateCcw');
export const Target = createSiteIcon('archery', 'Target');

export const ArrowLeft = createSiteIcon('arrow-left', 'ArrowLeft');
export const CircleHelp = createSiteIcon('help-circle', 'CircleHelp');
export const Info = createSiteIcon('info-circle', 'Info');
export const MonitorUp = createSiteIcon('stats-up-square', 'MonitorUp');
export const Undo2 = createSiteIcon('undo', 'Undo2');

export const TrendingDown = createSiteIcon('graph-down', 'TrendingDown');
export const TrendingUp = createSiteIcon('graph-up', 'TrendingUp');
export const Upload = createSiteIcon('upload', 'Upload');
export const WalletCards = createSiteIcon('card-wallet', 'WalletCards');
export const ChartNoAxesCombined = createSiteIcon(
  'stats-report',
  'ChartNoAxesCombined',
);
export const ChevronRight = createSiteIcon('nav-arrow-right', 'ChevronRight');
export const CircleAlert = createSiteIcon('warning-circle', 'CircleAlert');

export const BadgeEuro = createSiteIcon('euro-square', 'BadgeEuro');
export const BriefcaseBusiness = createSiteIcon(
  'suitcase',
  'BriefcaseBusiness',
);
export const Building2 = createSiteIcon('building', 'Building2');
export const CircleCheckBig = createSiteIcon('check-circle', 'CircleCheckBig');
export const CircleDashed = createSiteIcon('circle', 'CircleDashed');
export const FileQuestion = createSiteIcon('page-search', 'FileQuestion');
export const Landmark = createSiteIcon('bank', 'Landmark');
export const MessageCircleQuestion = createSiteIcon(
  'chat-bubble-question',
  'MessageCircleQuestion',
);
export const PackageCheck = createSiteIcon('clipboard-check', 'PackageCheck');
export const RefreshCcw = createSiteIcon('refresh', 'RefreshCcw');
export const Settings2 = createSiteIcon('settings', 'Settings2');
export const Users = createSiteIcon('group', 'Users');

export const FileChartColumnIncreasing = createSiteIcon(
  'reports',
  'FileChartColumnIncreasing',
);
export const Presentation = createSiteIcon('presentation', 'Presentation');

export const ArrowDown = createSiteIcon('arrow-down', 'ArrowDown');
export const FileLock2 = createSiteIcon('book-lock', 'FileLock2');
export const LockKeyhole = createSiteIcon('lock-square', 'LockKeyhole');
export const Network = createSiteIcon('network', 'Network');

export const Bookmark = createSiteIcon('bookmark', 'Bookmark');
export const GitBranch = createSiteIcon('git-branch', 'GitBranch');
export const Save = createSiteIcon('floppy-disk', 'Save');
export const GitCompareArrows = createSiteIcon(
  'git-compare',
  'GitCompareArrows',
);
export const CalendarClock = createSiteIcon('calendar', 'CalendarClock');
export const FileCheck2 = createSiteIcon('clipboard-check', 'FileCheck2');
export const ImagePlus = createSiteIcon('media-image-plus', 'ImagePlus');

export const ChevronDownIcon = createSiteIcon(
  'nav-arrow-down',
  'ChevronDownIcon',
);
export const ChevronLeftIcon = createSiteIcon(
  'nav-arrow-left',
  'ChevronLeftIcon',
);
export const ChevronRightIcon = createSiteIcon(
  'nav-arrow-right',
  'ChevronRightIcon',
);
export const ChevronUpIcon = createSiteIcon('nav-arrow-up', 'ChevronUpIcon');
export const MoreHorizontalIcon = createSiteIcon(
  'more-horiz',
  'MoreHorizontalIcon',
);
export const SearchIcon = createSiteIcon('search', 'SearchIcon');
export const CheckIcon = createSiteIcon('check', 'CheckIcon');
export const XIcon = createSiteIcon('xmark', 'XIcon');
export const MinusIcon = createSiteIcon('minus', 'MinusIcon');
export const ArrowDownIcon = createSiteIcon('arrow-down', 'ArrowDownIcon');
export const PanelLeftIcon = createSiteIcon('sidebar-expand', 'PanelLeftIcon');
export const Loader2Icon = createSiteIcon('refresh-double', 'Loader2Icon');
export const CircleCheckIcon = createSiteIcon(
  'check-circle',
  'CircleCheckIcon',
);
export const InfoIcon = createSiteIcon('info-circle', 'InfoIcon');
export const TriangleAlertIcon = createSiteIcon(
  'warning-triangle',
  'TriangleAlertIcon',
);
export const OctagonXIcon = createSiteIcon('xmark-circle', 'OctagonXIcon');
