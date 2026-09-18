'use client';

import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronRight,
  CircleAlert,
  GitCompareArrows,
  Landmark,
  Save,
  ShieldCheck,
  TriangleAlert,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useDemo } from '@/components/cockpit/demo-provider';
import {
  CashCurve,
  Delta,
  PageHeading,
  StateBadge,
  Surface,
} from '@/components/cockpit/page-elements';
import { baselineMetrics, calculateScenario, initialContract, scenarioFixture, cashFixtureForLowPoint, formatEuro } from '@/lib/demo';

export default function AtlasComparisonPage() {
  const router = useRouter();
  const { state, simulate, saveScenario, applyScenario } = useDemo();
  const current = state.simulatedMetrics ?? baselineMetrics;
  const improvedInputs = {
    ...initialContract,
    customer: state.contract.customer,
    depositPercent: 40,
    paymentDays: 30,
    deliveryMonths: 4,
    revenueRule: 'spread' as const,
  };
  const improved = calculateScenario(improvedInputs);
  const cashDelta = current.cashLowPoint - state.referenceMetrics.cashLowPoint;
  const recognizedRevenue = current.revenue - baselineMetrics.revenue;
  const improvedCashDelta = improved.cashLowPoint - current.cashLowPoint;
  const recommendationImprovesCash = improvedCashDelta > 0;
  const matchesActiveReference =
    state.referenceIncludesAtlas &&
    JSON.stringify(state.referenceVersions[0]?.contract) ===
      JSON.stringify(state.contract);
  const simulationReady =
    state.scenarioStatus !== 'draft' && Boolean(state.simulatedMetrics) && Boolean(scenarioFixture(state.contract));
  const canApply =
    simulationReady &&
    !matchesActiveReference &&
    state.rule.status === 'staged' &&
    state.rule.checks.every((check) => check.passed);

  const useImproved = () => {
    simulate(improvedInputs);
  };

  const confirmApply = () => {
    applyScenario();
    router.push('/decisions');
  };

  if (!simulationReady) {
    return (
      <div className="spatial-page">
        <PageHeading
          eyebrow="Simulation Atlas"
          title="Votre brouillon attend sa simulation."
          description="Vos dernières modifications sont conservées. Vérifiez leurs impacts pour obtenir une comparaison à jour, sans toucher à la version officielle."
        />
        <Surface className="mt-8 max-w-2xl">
          <h2 className="text-xl font-semibold">Une seule prochaine étape</h2>
          <p className="mt-3 leading-7 text-slate-600">
            Reprenez les conditions du contrat, puis ouvrez « Voir les impacts
            ». Les résultats apparaîtront ici après la simulation.
          </p>
          <Button
            className="mt-5 rounded-full"
            onClick={() => router.push('/travail/ventes')}
          >
            Reprendre mon brouillon <ArrowRight />
          </Button>
        </Surface>
      </div>
    );
  }

  return (
    <div className="spatial-page">
      <Button
        variant="ghost"
        className="mb-5 h-11 rounded-full px-3 text-slate-500"
        onClick={() => router.push('/simulations')}
      >
        <ArrowLeft data-icon="inline-start" /> Toutes les simulations
      </Button>

      <PageHeading
        eyebrow="Simulation Atlas Mobility"
        title="Votre scénario face à la version officielle."
        description={
          state.referenceIncludesAtlas
            ? 'Atlas est déjà inclus dans votre version officielle. Les autres cartes testent de nouvelles conditions sans la modifier.'
            : 'Comparez la version officielle, votre scénario et une option plus protectrice pour la trésorerie. Rien ne change avant votre confirmation.'
        }
        actions={
          <Button
            variant="outline"
            className="h-11 rounded-full bg-white/70"
            onClick={() => router.push('/travail/ventes')}
          >
            Retour au brouillon
          </Button>
        }
      />

      <p className="mt-7 text-sm text-slate-500">
        Trajectoires illustratives d’octobre 2026 à juillet 2027. Touchez une
        courbe ou parcourez ses mois au clavier.
      </p>
      <section className="atlas-scenario-deck mt-2">
        <div className="grid gap-5 xl:grid-cols-3">
          <ComparisonColumn
            label="Version officielle"
            title={
              state.referenceIncludesAtlas
                ? 'Atlas déjà inclus'
                : 'Sans le contrat Atlas'
            }
            revenue={state.referenceMetrics.revenue}
            cash={state.referenceMetrics.cashLowPoint}
            margin={state.referenceMetrics.grossMargin}
            runway={state.referenceMetrics.runway}
            note="Votre trajectoire officielle actuelle."
          />
          <ComparisonColumn
            label="Votre scénario"
            title={`${state.contract.depositPercent} % · ${state.contract.paymentDays} jours`}
            revenue={current.revenue}
            cash={current.cashLowPoint}
            margin={current.grossMargin}
            runway={current.runway}
            note={
              cashDelta < 0
                ? 'Plus de revenu, mais les achats précèdent le paiement.'
                : cashDelta > 0
                  ? 'Ces conditions améliorent aussi le point bas de trésorerie.'
                  : 'Ces conditions préservent le même point bas que la version officielle.'
            }
            highlighted
            delta={
              <Delta
                tone={
                  cashDelta < 0
                    ? 'negative'
                    : cashDelta > 0
                      ? 'positive'
                      : 'neutral'
                }
              >
                {cashDelta > 0 ? '+' : cashDelta < 0 ? '-' : ''}
                {formatEuro(Math.abs(cashDelta), true)} au point bas
              </Delta>
            }
          />
          <ComparisonColumn
            label={
              recommendationImprovesCash
                ? 'Piste recommandée'
                : 'Point de comparaison'
            }
            title="480 k€ · 40 % · 30 jours · 4 mois"
            revenue={improved.revenue}
            cash={improved.cashLowPoint}
            margin={improved.grossMargin}
            runway={improved.runway}
            note={
              recommendationImprovesCash
                ? 'Cas fictif Atlas : 480 k€, probable à 75 %, début octobre 2026, acompte 40 %, solde 30 jours et quatre mois. Un seul essai annulable.'
                : improvedCashDelta < 0
                  ? 'Vos conditions actuelles protègent mieux la trésorerie que cette piste.'
                  : 'Cette piste est déjà reflétée dans vos conditions actuelles.'
            }
            improved={recommendationImprovesCash}
            delta={
              <Delta
                tone={
                  improvedCashDelta > 0
                    ? 'positive'
                    : improvedCashDelta < 0
                      ? 'negative'
                      : 'neutral'
                }
              >
                {improvedCashDelta > 0 ? '+' : improvedCashDelta < 0 ? '-' : ''}
                {formatEuro(Math.abs(improvedCashDelta), true)} au point bas
              </Delta>
            }
            action={
              recommendationImprovesCash ? (
                <Button
                  variant="outline"
                  className="mt-4 h-11 w-full rounded-full bg-white"
                  onClick={useImproved}
                >
                  Utiliser ces conditions
                </Button>
              ) : (
                <output className="mt-4 rounded-[16px] bg-white/70 px-3 py-3 text-center text-sm font-semibold text-slate-600">
                  {improvedCashDelta < 0
                    ? 'Votre scénario protège mieux la trésorerie.'
                    : 'Ces conditions sont déjà dans votre scénario.'}
                </output>
              )
            }
          />
        </div>
      </section>

      <section className="atlas-insight-stack mt-9 grid gap-5 xl:grid-cols-[1.15fr_.85fr] xl:gap-0">
        <Surface variant="solid" depth={2} className="rounded-[34px] xl:pr-12">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-[var(--brand)]">
                Lecture du copilote
              </p>
              <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em]">
                Ce que les chiffres racontent
              </h2>
            </div>
            <StateBadge tone="warning">Décision économique ouverte</StateBadge>
          </div>
          <div className="mt-5 space-y-3">
            {[
              {
                icon: GitCompareArrows,
                title: 'Le contrat améliore bien l’activité',
                detail: `${formatEuro(recognizedRevenue, true)} sont reconnus dans l’horizon présenté.`,
                tone: 'bg-[var(--brand-soft)] text-[var(--brand-deep)]',
              },
              {
                icon: CircleAlert,
                title: 'La tension est temporaire, mais réelle',
                detail:
                  'Les matières et la production sont payées avant le solde client.',
                tone: 'bg-[#fff3dc] text-[#97600e]',
              },
              {
                icon: ShieldCheck,
                title: 'Changer les conditions ne change pas la vente',
                detail:
                  'L’acompte et le délai agissent sur le cash, pas sur le montant négocié.',
                tone: 'bg-[#e4f7f0] text-[#08795e]',
              },
            ].map(({ icon: Icon, title, detail, tone }) => (
              <div
                key={title}
                className="flex items-start gap-3 rounded-[20px] bg-slate-50/80 p-4"
              >
                <span
                  className={`grid size-10 shrink-0 place-items-center rounded-[14px] ${tone}`}
                >
                  <Icon className="size-4" />
                </span>
                <div>
                  <h3 className="font-semibold text-slate-900">{title}</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    {detail}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Surface>

        <Surface
          variant="tinted"
          depth={3}
          className="rounded-[34px] xl:-ml-7 xl:translate-y-8"
        >
          <div className="flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded-2xl bg-[var(--brand-soft)] text-[var(--brand-deep)]">
              <Landmark className="size-5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-500">
                Règle métier
              </p>
              <h2 className="font-semibold text-slate-900">
                {state.rule.status === 'staged'
                  ? 'Reconnaissance sur quatre mois'
                  : state.rule.status === 'needs-review'
                    ? 'Règle à revalider'
                    : 'Règle à préparer'}
              </h2>
            </div>
          </div>
          <ul className="mt-5 space-y-3 text-sm text-slate-600">
            {state.rule.checks.map((check) => (
              <li key={check.label} className="flex gap-2">
                {check.passed ? (
                  <Check className="mt-1 size-4 shrink-0 text-[#0a8a68]" />
                ) : (
                  <TriangleAlert className="mt-1 size-4 shrink-0 text-[#99600d]" />
                )}
                {check.label}
              </li>
            ))}
          </ul>
          <Button
            variant="ghost"
            className="mt-4 h-11 rounded-full px-3 text-[var(--brand-deep)]"
            onClick={() => router.push('/expert')}
          >
            Voir dans le modèle
            <ChevronRight data-icon="inline-end" />
          </Button>
        </Surface>
      </section>

      <div className="decision-action-bar spatial-surface spatial-surface--glass spatial-depth-2 sticky bottom-[84px] z-10 mt-12 flex flex-col gap-3 rounded-[26px] p-4 sm:flex-row sm:items-center sm:justify-between md:bottom-4">
        <div>
          <p className="font-semibold text-slate-800">
            {matchesActiveReference || state.scenarioStatus === 'applied'
              ? 'Ce scénario est votre version officielle.'
              : 'Votre version officielle reste inchangée.'}
          </p>
          <p className="mt-0.5 text-[13px] text-slate-500">
            {canApply
              ? 'Un seul choix final créera une nouvelle version. L’ancienne restera disponible.'
              : matchesActiveReference
                ? 'Ces conditions correspondent déjà à la version officielle.'
                : simulationReady
                  ? 'Corrigez les points signalés avant de faire votre choix final.'
                  : 'Reprenez le brouillon pour examiner les impacts avant de décider.'}
          </p>
          {!matchesActiveReference &&
          state.scenarioStatus !== 'applied' &&
          simulationReady ? (
            state.scenarioStatus === 'saved' ? (
              <p className="mt-2 text-[13px] font-semibold text-[var(--brand-deep)]">
                Une copie est gardée pour plus tard.
              </p>
            ) : (
              <Button
                variant="ghost"
                className="mt-1 h-10 rounded-full px-2 text-[13px] text-slate-500"
                onClick={saveScenario}
              >
                <Save data-icon="inline-start" /> Garder une copie pour plus
                tard
              </Button>
            )
          ) : null}
        </div>
        <div className="shrink-0">
          {canApply ? (
            <Dialog>
              <DialogTrigger
                render={
                  <Button className="h-12 w-full rounded-full px-5 sm:w-auto" />
                }
              >
                Choisir comme version officielle
                <ArrowRight data-icon="inline-end" />
              </DialogTrigger>
              <DialogContent
                showCloseButton={false}
                className="max-w-[470px] rounded-[28px] p-6"
              >
                <DialogHeader>
                  <DialogTitle className="text-xl font-semibold">
                    Utiliser ce scénario comme version officielle ?
                  </DialogTitle>
                  <DialogDescription className="text-[15px] leading-6">
                    Le scénario Atlas deviendra votre nouvelle trajectoire. La
                    version actuelle restera dans l’historique et pourra être
                    réutilisée.
                  </DialogDescription>
                </DialogHeader>
                <div className="rounded-[18px] bg-[var(--brand-soft)] p-4 text-sm text-slate-700">
                  <p className="font-semibold text-[var(--brand-deep)]">
                    Scénario choisi
                  </p>
                  <p className="mt-1">
                    {state.contract.depositPercent} % d’acompte ·{' '}
                    {state.contract.paymentDays} jours · revenu reconnu sur{' '}
                    {state.contract.deliveryMonths} mois.
                  </p>
                </div>
                <DialogFooter className="-mx-6 -mb-6 rounded-b-[28px] px-6">
                  <DialogClose
                    render={
                      <Button variant="outline" className="h-11 rounded-full" />
                    }
                  >
                    Pas encore
                  </DialogClose>
                  <DialogClose
                    render={
                      <Button
                        className="h-11 rounded-full"
                        onClick={confirmApply}
                      />
                    }
                  >
                    Oui, utiliser ce scénario
                  </DialogClose>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          ) : matchesActiveReference || state.scenarioStatus === 'applied' ? (
            <Button
              className="h-12 w-full rounded-full px-5 sm:w-auto"
              onClick={() => router.push('/decisions')}
            >
              Voir le journal des décisions
              <ArrowRight data-icon="inline-end" />
            </Button>
          ) : (
            <Button
              className="h-12 w-full rounded-full px-5 sm:w-auto"
              onClick={() => router.push('/travail/ventes')}
            >
              {simulationReady
                ? 'Corriger les points à vérifier'
                : 'Reprendre le brouillon'}
              <ArrowRight data-icon="inline-end" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

function ComparisonColumn({
  label,
  title,
  revenue,
  cash,
  margin,
  runway,
  note,
  highlighted,
  improved,
  delta,
  action,
}: {
  label: string;
  title: string;
  revenue: number;
  cash: number;
  margin: number;
  runway: number;
  note: string;
  highlighted?: boolean;
  improved?: boolean;
  delta?: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <article
      className={`atlas-scenario-card spatial-surface min-w-0 rounded-[34px] border border-white/90 p-5 sm:p-6 ${
        highlighted
          ? 'atlas-scenario-card--active spatial-surface--tinted spatial-depth-3 bg-[var(--brand-soft)]/72'
          : improved
            ? 'atlas-scenario-card--improved spatial-surface--floating bg-[#effaf6]/88'
            : 'spatial-surface--glass'
      }`}
    >
      <div className="flex min-h-[62px] flex-col items-start gap-2 xl:min-h-[112px]">
        <div>
          <p className="text-[12px] font-semibold uppercase tracking-[0.1em] text-slate-400">
            {label}
          </p>
          <h2 className="mt-1 text-lg font-semibold text-slate-900">{title}</h2>
        </div>
        {delta}
      </div>
      <div className="mt-5 rounded-[18px] bg-white/75 p-3">
        <CashCurve
          improved={improved}
          domain={[0, 400000]}
          points={cashFixtureForLowPoint(cash)}
          ariaLabel={`${label} : trésorerie mensuelle illustrative`}
        />
        <div
          aria-hidden="true"
          className="mt-2 flex justify-between text-sm text-slate-500"
        >
          <span>Oct.</span>
          <span>Mars</span>
          <span>Juil.</span>
        </div>
      </div>
      <dl className="mt-5 grid grid-cols-2 gap-3">
        {[
          ['CA sur l’horizon', formatEuro(revenue, true)],
          ['Marge brute', `${margin.toLocaleString('fr-FR')} %`],
          ['Point bas', formatEuro(cash, true)],
          ['Visibilité', `${runway} mois`],
        ].map(([term, value]) => (
          <div key={term} className="rounded-[16px] bg-white/65 p-3">
            <dt className="text-[12px] text-slate-400">{term}</dt>
            <dd className="mt-1 text-lg font-semibold text-slate-900">
              {value}
            </dd>
          </div>
        ))}
      </dl>
      <p className="mt-4 min-h-[72px] overflow-hidden rounded-[16px] border border-white/80 bg-white/65 px-3 py-3 text-sm leading-6 text-slate-600 [overflow-wrap:anywhere] shadow-[inset_0_1px_0_rgba(255,255,255,.88)]">
        {note}
      </p>
      {action}
    </article>
  );
}
