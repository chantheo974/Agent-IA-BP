'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  BriefcaseBusiness,
  CalendarClock,
  Clock3,
  GitCompareArrows,
  ShieldCheck,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import { useDemo } from '@/components/cockpit/demo-provider';
import {
  CashCurve,
  PageHeading,
  StateBadge,
  Surface,
} from '@/components/cockpit/page-elements';
import { calculateScenario, initialContract, baselineMetrics, cashFixtureForLowPoint, formatEuro } from '@/lib/demo';

export default function SimulationsPage() {
  const router = useRouter();
  const { state, loadSavedVariant, setImpactOpen } = useDemo();
  const hasSimulation =
    state.scenarioStatus !== 'draft' && Boolean(state.simulatedMetrics);
  const current = state.simulatedMetrics ?? baselineMetrics;
  const revenueDelta = current.revenue - state.referenceMetrics.revenue;
  const cashDelta = current.cashLowPoint - state.referenceMetrics.cashLowPoint;
  const runwayDelta = current.runway - state.referenceMetrics.runway;
  const comparison = calculateScenario({
    ...initialContract,
    revenueRule: 'spread',
    depositPercent: 40,
    paymentDays: 30,
  });
  const comparisonCashGain = comparison.cashLowPoint - current.cashLowPoint;
  const cashEvolution = cashFixtureForLowPoint(current.cashLowPoint);
  const signedValue = (value: number, suffix = '') =>
    `${value > 0 ? '+' : value < 0 ? '-' : ''}${Math.abs(value).toLocaleString('fr-FR')}${suffix}`;
  const scenarioLabel = {
    draft: 'Essai non appliqué',
    simulated: 'Prêt à comparer',
    saved: 'Prêt à comparer',
    applied: 'Version officielle',
  }[state.scenarioStatus];
  const scenarioStatusStyle =
    state.scenarioStatus === 'draft'
      ? 'text-[#81591a] before:bg-[#e3ae54]'
      : state.scenarioStatus === 'applied'
        ? 'text-[#08795e] before:bg-[#45c9a2]'
        : 'text-[var(--brand-deep)] before:bg-[var(--brand)]';
  const primaryLabel =
    state.scenarioStatus === 'applied'
      ? 'Tester d’autres conditions'
      : state.scenarioStatus === 'draft' && state.rule.status === 'staged'
        ? 'Voir les impacts'
        : state.scenarioStatus === 'draft'
          ? 'Préparer le scénario'
          : 'Comparer à la version officielle';

  const continueScenario = () => {
    if (state.scenarioStatus === 'applied') {
      router.push('/travail/ventes');
      return;
    }
    if (state.scenarioStatus === 'draft' && state.rule.status === 'staged') {
      setImpactOpen(true);
      return;
    }
    if (state.scenarioStatus === 'draft') {
      router.push('/travail/ventes');
      return;
    }
    router.push('/simulations/atlas');
  };

  return (
    <div className="spatial-page">
      <PageHeading
        eyebrow="Décisions à tester"
        title="Simulations"
        description="Préparez un scénario, comprenez ses effets, puis comparez-le à votre version officielle."
      />

      <Surface><h2 className="text-xl font-semibold">Scénarios des autres thèmes</h2>{state.themeScenarios.length?state.themeScenarios.map(item=><Link key={item.id} className="mt-3 block rounded-xl border p-4 underline" href={'/simulations/'+item.id}>{item.name} · {item.status} · {item.createdAt}</Link>):<p>Aucune autre simulation pour le moment. Rejoignez un thème dans Parcours.</p>}</Surface>
      <section
        className="premium-scenario-stage mt-8"
        aria-labelledby="atlas-simulation-title"
      >
        <div
          className="premium-scenario-back premium-scenario-back--left"
          aria-hidden="true"
        >
          <span>Version officielle</span>
          <strong>Trajectoire actuelle</strong>
        </div>
        <div
          className="premium-scenario-back premium-scenario-back--right"
          aria-hidden="true"
        >
          <span>Variante corrigée</span>
          <strong>Encaissement accéléré</strong>
        </div>

        <div
          className="premium-orbit-bubble premium-orbit-bubble--runway"
          aria-hidden="true"
        >
          <span className="premium-orbit-bubble__icon">
            <CalendarClock className="size-[18px]" />
          </span>
          <span>
            <small>Visibilité corrigée</small>
            <strong>{comparison.runway} mois</strong>
          </span>
        </div>
        <div
          className="premium-orbit-bubble premium-orbit-bubble--deposit"
          aria-hidden="true"
        >
          <span className="premium-orbit-bubble__icon premium-orbit-bubble__icon--deposit">
            <ShieldCheck className="size-[19px]" />
          </span>
          <span>
            <small>Financement initial</small>
            <strong>40 % à la commande</strong>
          </span>
        </div>

        <article className="premium-scenario-card">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
              <span
                className={`inline-flex items-center gap-2 text-sm font-semibold before:block before:size-2 before:shrink-0 before:rounded-full ${scenarioStatusStyle}`}
              >
                État : {scenarioLabel}
              </span>
              <span
                aria-hidden="true"
                className="hidden h-4 w-px bg-slate-200 sm:block"
              />
              <span className="text-sm font-medium text-slate-500">
                Contrat : Atlas Mobility
              </span>
            </div>
            <span
              aria-hidden="true"
              className="grid size-11 shrink-0 place-items-center rounded-[15px] bg-[var(--brand-soft)] text-[var(--brand-deep)] shadow-[inset_0_0_0_1px_rgba(255,255,255,.72)]"
            >
              <GitCompareArrows className="size-5" />
            </span>
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold text-[var(--brand)]">
              Contrat Atlas
            </p>
            <h2
              id="atlas-simulation-title"
              className="mt-1 text-[clamp(1.9rem,5vw,2.8rem)] font-semibold leading-[1.04] tracking-[-0.045em] text-slate-950"
            >
              {state.scenarioStatus === 'draft'
                ? 'Préparer le scénario Atlas'
                : cashDelta < 0
                  ? 'Sécuriser la trésorerie'
                  : 'Accélérer sans fragiliser'}
            </h2>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-500">
              {state.referenceIncludesAtlas
                ? 'Le contrat est dans la version officielle. Vous testez ici de nouvelles conditions sans la modifier.'
                : 'Les achats commencent avant le paiement du solde. Vérifiez le passage bas avant de décider.'}
            </p>
          </div>

          {hasSimulation ? (
            <>
              <div className="premium-cash-chart mt-6">
                <div className="cash-chart-heading grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
                  <span className="min-w-0 text-sm font-semibold leading-5 text-slate-600">
                    Trésorerie prévisionnelle
                  </span>
                  <span className="cash-chart-low whitespace-nowrap pt-0.5 text-sm font-semibold text-slate-500">
                    Point bas ·{' '}
                    <strong className="text-slate-800">
                      {formatEuro(current.cashLowPoint, true)}
                    </strong>
                  </span>
                </div>
                <div className="mt-4">
                  <CashCurve
                    improved={cashDelta >= 0}
                    points={cashEvolution}
                    ariaLabel="Prévision simulée de la trésorerie d’octobre 2026 à juillet 2027"
                  />
                  <div className="mt-1 flex justify-between text-[12px] font-medium text-slate-400">
                    <span>Oct.</span>
                    <span>Janv.</span>
                    <span>Avr.</span>
                    <span>Juil.</span>
                  </div>
                </div>
              </div>

              <div className="premium-metric-grid mt-5">
                {[
                  [
                    'Point bas de trésorerie',
                    formatEuro(current.cashLowPoint, true),
                    `${cashDelta > 0 ? '+' : cashDelta < 0 ? '-' : ''}${formatEuro(Math.abs(cashDelta), true)}`,
                  ],
                  [
                    'Chiffre d’affaires',
                    formatEuro(current.revenue, true),
                    `${revenueDelta > 0 ? '+' : revenueDelta < 0 ? '-' : ''}${formatEuro(Math.abs(revenueDelta), true)}`,
                  ],
                ].map(([label, value, delta]) => (
                  <div key={label} className="premium-metric-card">
                    <p className="text-sm leading-5 text-slate-500">{label}</p>
                    <p className="mt-2 text-[clamp(1.7rem,6vw,2.3rem)] font-semibold tracking-[-0.045em] text-slate-950">
                      {value}
                    </p>
                    <p className="mt-1 text-[12px] font-semibold text-[var(--brand-deep)]">
                      {delta} vs version officielle
                    </p>
                  </div>
                ))}
              </div>

              <div className="premium-scenario-note mt-5 flex items-start gap-3">
                <Clock3 className="mt-1 hidden size-4 shrink-0 text-[var(--brand)] sm:block" />
                <p className="pl-7 text-sm leading-6 text-slate-600 sm:pl-0">
                  <span className="mb-0.5 block text-[12px] font-semibold uppercase tracking-[0.08em] text-[var(--brand-deep)]">
                    Levier de trésorerie
                  </span>
                  {comparisonCashGain > 0
                    ? `40 % d’acompte et un règlement à 30 jours amélioreraient le point bas de ${formatEuro(comparisonCashGain, true)}.`
                    : `La visibilité reste de ${current.runway} mois (${signedValue(runwayDelta, ' mois')} par rapport à la version officielle).`}
                </p>
              </div>
            </>
          ) : (
            <div className="mt-6 rounded-[24px] border border-white/90 bg-white/68 p-5 shadow-[0_14px_34px_rgba(54,63,104,.07)]">
              <StateBadge tone="neutral">Résultats non calculés</StateBadge>
              <h3 className="mt-4 text-lg font-semibold text-slate-900">
                Votre version officielle n’a pas bougé.
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Préparez d’abord les hypothèses du contrat. Vous verrez ensuite
                les impacts avant toute comparaison.
              </p>
            </div>
          )}

          <div className="mt-6">
            <Button
              className="premium-primary-action min-h-12 w-full rounded-full bg-[var(--brand-deep)] px-5 text-white"
              onClick={continueScenario}
            >
              {primaryLabel}
              <ArrowRight data-icon="inline-end" />
            </Button>
          </div>
        </article>
      </section>

      <section className="mt-8">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-[var(--brand)]">
              Autres pistes
            </p>
            <h2 className="mt-1 text-2xl font-semibold tracking-[-0.035em]">
              Vos scénarios conservés
            </h2>
          </div>
        </div>
        <div className="scenario-card-deck mt-5 grid gap-4 xl:grid-cols-3">
          {state.savedVariants.length === 0 ? (
            <Surface
              variant="solid"
              depth={1}
              className="scenario-card rounded-[30px]"
            >
              <BriefcaseBusiness className="size-6 text-[var(--brand)]" />
              <h3 className="mt-5 font-semibold text-slate-900">
                Aucun scénario gardé pour plus tard
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Vous pourrez garder une variante depuis l’écran de comparaison,
                sans modifier votre version officielle.
              </p>
            </Surface>
          ) : (
            state.savedVariants.map((variant) => (
              <button
                key={variant.id}
                type="button"
                className="scenario-card spatial-surface spatial-surface--floating spatial-interactive group rounded-[30px] p-5 text-left sm:p-6"
                onClick={() => {
                  loadSavedVariant(variant.id);
                  router.push('/simulations/'+variant.id);
                }}
              >
                <BriefcaseBusiness className="size-6 text-[var(--brand)]" />
                <h3 className="mt-5 font-semibold text-slate-900">
                  {variant.name}
                </h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  {variant.inputs.depositPercent} % d’acompte ·{' '}
                  {variant.inputs.paymentDays} jours · point bas{' '}
                  {formatEuro(variant.metrics.cashLowPoint, true)}.
                </p>
                <div className="mt-4 flex items-center justify-between">
                  <StateBadge tone="success">Conservé</StateBadge>
                  <ArrowRight className="size-4 text-slate-400 transition group-hover:translate-x-1" />
                </div>
              </button>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
