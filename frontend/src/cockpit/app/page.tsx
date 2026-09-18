'use client';

import { ThemeJourneys } from './demo-parts';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  ChartNoAxesCombined,
  ChevronRight,
  CircleAlert,
  Gauge,
  Sparkles,
  WalletCards,
} from '@/components/ui/site-icon';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CompanionBadge } from '@/components/cockpit/companion-mark';
import { useDemo } from '@/components/cockpit/demo-provider';
import {
  CashCurve,
  MetricCard,
  SpatialCluster,
} from '@/components/cockpit/page-elements';
import { formatEuro, cashFixtureForLowPoint } from '@/lib/demo';

const phaseFlow = [
  { label: 'Cadrer', title: 'Définir votre cap', next: 'réunir vos sources' },
  {
    label: 'Sources',
    title: 'Réunir les faits utiles',
    next: 'construire vos hypothèses',
  },
  {
    label: 'Construire',
    title: 'Construire vos hypothèses',
    next: 'tester vos décisions',
  },
  {
    label: 'Simuler',
    title: 'Comparer vos options',
    next: 'valider une décision',
  },
  {
    label: 'Décider',
    title: 'Valider votre trajectoire',
    next: 'piloter le réalisé',
  },
  {
    label: 'Piloter',
    title: 'Piloter votre trajectoire',
    next: 'poursuivre le rituel mensuel',
  },
] as const;

export default function Home() {
  const router = useRouter();
  const { state, setCopilotOpen } = useDemo();
  const metrics = state.referenceMetrics;
  const officialContract = state.referenceVersions[0].contract;
  const phaseIndex = Math.max(
    0,
    phaseFlow.findIndex((phase) => phase.label === state.phase),
  );
  const completedSteps = phaseIndex;
  const phaseProgress = Math.round((completedSteps / phaseFlow.length) * 100);
  const currentPhase = phaseFlow[phaseIndex];
  const improved =
    state.referenceIncludesAtlas && officialContract.depositPercent >= 30;

  return (
    <div className="spatial-page">
      <header className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div className="max-w-[820px]">
          <Badge className="h-8 rounded-full border border-white/90 bg-white/72 px-3.5 text-[var(--brand-deep)] shadow-[0_8px_22px_rgba(54,63,104,.08)] backdrop-blur-xl hover:bg-white/72">
            <Sparkles data-icon="inline-start" /> Phase · {state.phase}
          </Badge>
          <h1 className="mt-4 text-[clamp(2rem,3.4vw,2.75rem)] font-semibold leading-[1.12] tracking-[-0.035em] text-[#17203a]">
            Bonjour {state.brand.firstName}.
          </h1>
          <p className="mt-2 text-slate-600">
            Votre trésorerie et votre prochaine décision, en un regard.
          </p>
        </div>
      </header>

      <SpatialCluster
        className="decision-stack mt-8"
        aria-label="Décision prioritaire et contexte"
      >
        <aside
          className="decision-stack__phase spatial-surface spatial-surface--tinted rounded-[28px] p-5"
          aria-label={`${completedSteps} phases terminées sur ${phaseFlow.length}`}
        >
          <div className="flex items-center gap-3">
            <div
              className="grid size-14 shrink-0 place-items-center rounded-full"
              style={{
                background: `conic-gradient(var(--brand) ${phaseProgress}%, rgba(255,255,255,.62) 0)`,
              }}
            >
              <span className="grid size-10 place-items-center rounded-full bg-white/92 font-semibold text-[var(--brand-deep)]">
                {completedSteps}/{phaseFlow.length}
              </span>
            </div>
            <div>
              <p className="font-semibold text-slate-900">
                {currentPhase.title}
              </p>
              <p className="mt-1 text-slate-600">Puis {currentPhase.next}.</p>
            </div>
          </div>
        </aside>

        <aside className="decision-stack__watch spatial-surface spatial-surface--floating rounded-[28px] bg-[linear-gradient(145deg,rgba(255,255,255,.86),rgba(255,255,255,.44)),var(--pastel-peach)] p-5">
          <div className="flex items-start gap-3">
            <span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-white/78 text-[#9a542b] shadow-sm">
              <CircleAlert className="size-5" />
            </span>
            <div>
              <p className="font-semibold text-slate-900">À surveiller</p>
              <p className="mt-1 text-slate-600">
                Achats avant encaissement et délai client de{' '}
                {officialContract.paymentDays} jours.
              </p>
            </div>
          </div>
        </aside>

        <article className="decision-stack__main spatial-surface spatial-surface--tinted spatial-depth-3 overflow-hidden rounded-[38px] p-6 sm:p-8 lg:p-9">
          <div
            className="absolute inset-x-16 -top-24 h-52 rounded-full bg-[var(--pastel-sky)]/75 blur-3xl"
            aria-hidden="true"
          />
          <div className="relative grid gap-7">
            <div>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
                <span className="inline-flex h-9 items-center gap-2 px-1 text-sm font-semibold text-[var(--brand-deep)]">
                  <span
                    aria-hidden="true"
                    className="size-2 rounded-full bg-[var(--brand)] shadow-[0_0_0_5px_color-mix(in_srgb,var(--brand)_12%,transparent)]"
                  />
                  {state.referenceIncludesAtlas
                    ? 'Décision appliquée'
                    : 'Décision à préparer'}
                </span>
                <span className="text-sm font-medium text-slate-500">
                  Thème : Ventes et contrats
                </span>
              </div>
              <h2 className="mt-4 max-w-[700px] text-[clamp(1.55rem,2.5vw,2rem)] font-semibold leading-[1.16] tracking-[-0.03em] text-[#17203a]">
                {state.referenceIncludesAtlas
                  ? 'Atlas est dans votre trajectoire. Suivons ses encaissements.'
                  : 'Atlas : choisir les bonnes conditions de paiement.'}
              </h2>
              <p className="mt-4 max-w-[680px] leading-7 text-slate-600">
                {state.referenceIncludesAtlas
                  ? `${formatEuro(officialContract.amount, true)} sur ${officialContract.deliveryMonths} mois · ${officialContract.depositPercent} % d’acompte · solde à ${officialContract.paymentDays} jours. L’ancienne version reste restaurable.`
                  : '480 k€ sur quatre mois. Testez l’acompte et le délai de paiement avant de choisir votre trajectoire.'}
              </p>
              <div className="mt-7 flex flex-col gap-3 sm:flex-row">
                <Button
                  className="h-12 rounded-full bg-[var(--brand-deep)] px-5 font-semibold text-white shadow-[0_12px_28px_color-mix(in_srgb,var(--brand)_22%,transparent)]"
                  onClick={() =>
                    state.referenceIncludesAtlas
                      ? router.push('/suivi-mensuel')
                      : router.push('/travail/ventes')
                  }
                >
                  {state.referenceIncludesAtlas
                    ? 'Préparer le suivi mensuel'
                    : 'Préparer le contrat Atlas'}
                  <ArrowRight data-icon="inline-end" />
                </Button>
              </div>
            </div>

            <div className="rounded-[30px] border border-white/92 bg-white/66 p-5 shadow-[0_18px_45px_rgba(54,63,104,.09)] backdrop-blur-xl">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-700">
                    Point bas de trésorerie
                  </p>
                  <p className="mt-1 text-[2rem] font-semibold tracking-[-0.04em] text-slate-950">
                    {formatEuro(metrics.cashLowPoint, true)}
                  </p>
                </div>
                <span className="rounded-full bg-[var(--pastel-mint)] px-3 py-1.5 font-semibold text-[#176f59]">
                  {metrics.runway} mois
                </span>
              </div>
              <div className="mt-5 rounded-[22px] bg-white/58 px-3 pb-2 pt-4">
                <CashCurve
                  improved={improved}
                  points={cashFixtureForLowPoint(metrics.cashLowPoint)}
                />
              </div>
              <p className="mt-4 leading-6 text-slate-600">
                L’activité progresse, mais le moment des encaissements reste
                décisif.
              </p>
            </div>
          </div>
        </article>

        <button
          type="button"
          onClick={() => setCopilotOpen(true)}
          className="companion-trigger decision-stack__bubble floating-bubble spatial-interactive px-4 py-4 text-left"
        >
          <CompanionBadge shape="round" motion="awake" />
          <span>
            <span className="block font-semibold text-slate-900">
              Un éclairage du compagnon
            </span>
            <span className="block text-slate-600">
              Comprendre le calendrier du contrat
            </span>
          </span>
          <ChevronRight className="ml-auto size-5 shrink-0 text-[var(--brand-deep)]" />
        </button>
      </SpatialCluster>

      <ThemeJourneys/>
      <section aria-labelledby="situation-title" className="mt-14 md:mt-16">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-[var(--brand-deep)]">
              Votre situation
            </p>
            <h2
              id="situation-title"
              className="mt-1 text-2xl font-semibold tracking-[-0.03em] text-slate-950"
            >
              Trois repères, une même trajectoire
            </h2>
          </div>
          <Button
            variant="ghost"
            className="h-11 rounded-full px-3 font-semibold text-[var(--brand-deep)]"
            onClick={() => router.push('/livrables')}
          >
            Voir la synthèse
          </Button>
        </div>
        <div className="metric-stack pb-6">
          <MetricCard
            label="Trésorerie disponible"
            value="320 k€"
            detail="Situation actuelle"
            icon={WalletCards}
            className="bg-[linear-gradient(145deg,rgba(255,255,255,.9),rgba(255,255,255,.56)),var(--pastel-sky)]"
          />
          <MetricCard
            label="Point bas prévisionnel"
            value={formatEuro(metrics.cashLowPoint, true)}
            detail="Sur la trajectoire illustrative"
            icon={ChartNoAxesCombined}
            tone="warning"
            className="bg-[linear-gradient(145deg,rgba(255,255,255,.92),rgba(255,255,255,.5)),var(--pastel-peach)]"
          />
          <MetricCard
            label="Visibilité de trésorerie"
            value={`${metrics.runway} mois`}
            detail="Sans nouveau financement"
            icon={Gauge}
            tone="success"
            className="bg-[linear-gradient(145deg,rgba(255,255,255,.9),rgba(255,255,255,.5)),var(--pastel-mint)]"
          />
        </div>
      </section>
    </div>
  );
}
