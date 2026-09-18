'use client';

import Link from 'next/link';
import { themeRoute } from '@/lib/catalog';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  BadgeEuro,
  BriefcaseBusiness,
  Building2,
  Check,
  CircleCheckBig,
  CircleDashed,
  FileQuestion,
  Landmark,
  MessageCircleQuestion,
  PackageCheck,
  RefreshCcw,
  Settings2,
  Sparkles,
  TriangleAlert,
  Users,
  WalletCards,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import { useDemo } from '@/components/cockpit/demo-provider';
import {
  PageHeading,
  StateBadge,
  Surface,
} from '@/components/cockpit/page-elements';
import { themes, type ThemeKey } from '@/lib/demo';

const phaseItems = [
  {
    label: 'Cadrer',
    detail: 'Votre entreprise et vos objectifs',
    href: '/parcours/installation?mode=review&step=0',
  },
  {
    label: 'Sources',
    detail: 'Documents et faits confirmés',
    href: '/parcours/installation?mode=review&step=3',
  },
  {
    label: 'Construire',
    detail: 'Hypothèses par sujet métier',
    href: '/parcours#themes',
  },
  {
    label: 'Simuler',
    detail: 'Décisions avant de les appliquer',
    href: '/simulations',
  },
  {
    label: 'Décider',
    detail: 'Choix et versions officielles',
    href: '/decisions',
  },
  {
    label: 'Piloter',
    detail: 'Écarts et rituel mensuel',
    href: '/suivi-mensuel',
  },
] as const;

const themeIcons: Record<ThemeKey, typeof Building2> = {
  sales: BriefcaseBusiness,
  margin: PackageCheck,
  people: Users,
  investment: Landmark,
  cash: WalletCards,
  summary: BadgeEuro,
};

const controlStates = [
  {
    label: 'Calcul cohérent',
    detail: 'Les contrôles sont passés.',
    icon: CircleCheckBig,
    className: 'bg-[#e4f7f0] text-[#08795e]',
  },
  {
    label: 'Saisie incomplète',
    detail: 'Une information attend encore.',
    icon: CircleDashed,
    className: 'bg-slate-100 text-slate-600',
  },
  {
    label: 'Hypothèse à confirmer',
    detail: 'Le chiffre vient d’une estimation.',
    icon: TriangleAlert,
    className: 'bg-[#fff3dc] text-[#8e580a]',
  },
  {
    label: 'Justificatif manquant',
    detail: 'La source n’a pas été déposée.',
    icon: FileQuestion,
    className: 'bg-[#fff0e6] text-[#a95720]',
  },
  {
    label: 'Décision économique ouverte',
    detail: 'Votre arbitrage est nécessaire.',
    icon: MessageCircleQuestion,
    className: 'bg-[var(--brand-soft)] text-[var(--brand-deep)]',
  },
  {
    label: 'Calcul à actualiser',
    detail: 'Une nouvelle simulation est requise.',
    icon: RefreshCcw,
    className: 'bg-[#ffe8eb] text-[#ad334a]',
  },
] as const;

export default function JourneyPage() {
  const router = useRouter();
  const { state, setThemeMode } = useDemo();
  const phaseIndex = Math.max(
    0,
    phaseItems.findIndex((phase) => phase.label === state.phase),
  );

  return (
    <div className="spatial-page">
      <PageHeading
        eyebrow="Votre parcours"
        title="Votre parcours, à votre rythme."
        description="Chaque sujet conserve son propre niveau d’accompagnement. Vous pouvez demander au copilote de préparer le travail ou reprendre la main quand vous le souhaitez."
        actions={
          <Button
            variant="outline"
            className="h-11 rounded-full bg-white/70"
            onClick={() => router.push('/parcours/installation?mode=review')}
          >
            Modifier mes informations
          </Button>
        }
      />

      <Surface
        variant="floating"
        depth={3}
        className="mt-8 overflow-visible p-3 sm:p-4"
      >
        <div className="px-3 py-4 sm:px-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-500">Avancement</p>
              <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em]">
                De la situation actuelle à la décision
              </h2>
            </div>
            <StateBadge>Phase · {state.phase}</StateBadge>
          </div>
        </div>
        <div className="journey-phase-grid grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {phaseItems.map((phase, index) => {
            const isDone = index < phaseIndex;
            const isCurrent = index === phaseIndex;
            const isAvailable = index <= phaseIndex;
            const actionLabel = isDone
              ? 'Revoir cette étape'
              : isCurrent
                ? 'Continuer ici'
                : 'À venir';
            const phaseContent = (
              <>
                <span
                  className={`grid size-9 place-items-center rounded-full text-sm font-bold ${
                    isDone
                      ? 'bg-[#def5ed] text-[#08795e]'
                      : isCurrent
                        ? 'bg-[var(--brand)] text-white'
                        : 'bg-slate-100 text-slate-400'
                  }`}
                >
                  {isDone ? <Check className="size-4" /> : index + 1}
                </span>
                <h3 className="mt-4 font-semibold text-slate-900">
                  {phase.label}
                </h3>
                <p className="mt-1 text-[13px] leading-5 text-slate-500">
                  {phase.detail}
                </p>
                <span
                  className={`mt-5 flex items-center justify-between gap-2 text-[13px] font-semibold ${
                    isCurrent ? 'text-[var(--brand-deep)]' : 'text-slate-600'
                  }`}
                >
                  {actionLabel}
                  {isAvailable ? (
                    <ArrowRight
                      aria-hidden="true"
                      className="size-4 transition-transform group-hover:translate-x-1"
                    />
                  ) : null}
                </span>
              </>
            );
            const cardClass = `group relative min-h-[178px] w-full rounded-[24px] border border-white/90 p-5 text-left shadow-[0_12px_30px_rgba(54,63,104,.08)] ${
              isCurrent ? 'bg-[var(--brand-soft)]' : 'bg-white/72'
            }`;

            return isAvailable ? (
              <Link
                key={phase.label}
                href={phase.href}
                aria-current={isCurrent ? 'step' : undefined}
                aria-label={`${actionLabel} : ${phase.label}. ${phase.detail}`}
                className={`spatial-interactive cursor-pointer outline-none focus-visible:ring-[3px] focus-visible:ring-[var(--brand)]/35 ${cardClass}`}
              >
                {phaseContent}
              </Link>
            ) : (
              <article
                key={phase.label}
                aria-label={`${phase.label} : ${phase.detail}. À venir.`}
                className={`${cardClass} opacity-70`}
              >
                {phaseContent}
              </article>
            );
          })}
        </div>
      </Surface>

      <section id="themes" className="mt-10 scroll-mt-28">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-[var(--brand)]">
              Vos sujets de travail
            </p>
            <h2 className="mt-1 text-2xl font-semibold tracking-[-0.035em] text-slate-900">
              Choisissez comment avancer sur chaque thème
            </h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Settings2 className="size-4" /> Votre choix est mémorisé
          </div>
        </div>

        <div className="theme-stack-grid mt-6 grid gap-5 lg:grid-cols-2">
          {themes.map((theme) => {
            const Icon = themeIcons[theme.key];
            const mode = state.themeModes[theme.key];
            const modeLabel =
              mode === 'guided' ? 'Guide-moi' : 'Fais-le pour moi';
            const modeSelector = (
              <fieldset className="theme-mode-toggle sales-mode-selector grid grid-cols-2 gap-2 rounded-[18px] p-1.5">
                <legend className="sr-only">
                  Mode de travail pour {theme.label}
                </legend>
                <Button
                  aria-pressed={mode === 'guided'}
                  variant="ghost"
                  className="sales-mode-choice min-h-11 min-w-0 rounded-[14px]"
                  onClick={() => setThemeMode(theme.key, 'guided')}
                >
                  Guide-moi
                </Button>
                <Button
                  aria-pressed={mode === 'auto'}
                  variant="ghost"
                  className="sales-mode-choice min-h-11 min-w-0 rounded-[14px]"
                  onClick={() => setThemeMode(theme.key, 'auto')}
                >
                  <Sparkles data-icon="inline-start" /> Fais-le pour moi
                </Button>
              </fieldset>
            );
            return (
              <article
                key={theme.key}
                className="theme-stack-card spatial-surface spatial-surface--floating min-w-0 rounded-[30px] p-5 sm:p-6"
              >
                <div className="grid grid-cols-[3rem_minmax(0,1fr)] items-start gap-x-4">
                  <span className="grid size-12 shrink-0 place-items-center rounded-[17px] bg-[var(--brand-soft)] text-[var(--brand-deep)]">
                    <Icon className="size-5" />
                  </span>
                  <div className="theme-card-content min-w-0">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-lg font-semibold tracking-[-0.02em] text-slate-900">
                        {theme.label}
                      </h3>
                      {theme.key === 'sales' ? (
                        <StateBadge tone="warning">
                          3 hypothèses à confirmer
                        </StateBadge>
                      ) : (
                        <StateBadge tone="neutral">{state.themeDrafts[theme.key]?.status==='applied'?'Version locale adoptée':'À examiner'}</StateBadge>
                      )}
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      {theme.description}
                    </p>

                    {theme.key === 'sales' ? (
                      <div className="mt-5">{modeSelector}</div>
                    ) : (
                      <>
                        <div className="mt-4 flex flex-wrap items-center justify-between gap-2 rounded-[16px] bg-slate-100/70 px-3.5 py-2.5 text-sm">
                          <span className="text-slate-500">Mode actuel</span>
                          <span className="inline-flex items-center gap-1.5 font-semibold text-slate-800">
                            {mode === 'auto' ? (
                              <Sparkles className="size-4 text-[var(--brand)]" />
                            ) : null}
                            {modeLabel}
                          </span>
                        </div>
                        <details className="mt-2 rounded-[18px] border border-slate-200/70 bg-white/48 px-3.5 py-2.5">
                          <summary className="cursor-pointer text-sm font-semibold text-[var(--brand-deep)]">
                            Modifier l’accompagnement
                          </summary>
                          <div className="pt-3">{modeSelector}</div>
                        </details>
                      </>
                    )}

                    {(
                      <Button
                        variant="ghost"
                        className="mt-4 h-11 rounded-full px-3 text-[var(--brand-deep)]"
                        onClick={() => router.push(themeRoute(theme.key))}
                      >
                        Continuer sur ce thème
                        <ArrowRight data-icon="inline-end" />
                      </Button>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <Surface variant="tinted" depth={2} className="mt-8 rounded-[34px]">
        <details>
          <summary className="cursor-pointer text-base font-semibold text-slate-900">
            Comprendre les statuts
          </summary>
          <div className="mt-5 border-t border-slate-200/70 pt-5">
            <p className="text-sm font-semibold text-[var(--brand)]">
              Des états lisibles, jamais ambigus
            </p>
            <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em] text-slate-900">
              Vous savez toujours ce qui bloque et pourquoi
            </h2>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {controlStates.map((control) => {
                const Icon = control.icon;
                return (
                  <article
                    key={control.label}
                    className="flex min-h-[86px] items-start gap-3 rounded-[20px] border border-slate-200/70 bg-white/65 p-4"
                  >
                    <span
                      className={`grid size-10 shrink-0 place-items-center rounded-[14px] ${control.className}`}
                    >
                      <Icon className="size-4" />
                    </span>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-800">
                        {control.label}
                      </h3>
                      <p className="mt-1 text-[13px] leading-5 text-slate-500">
                        {control.detail}
                      </p>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </details>
      </Surface>
    </div>
  );
}
