'use client';

import Link from 'next/link';
import { sourceConfirmed } from '@/lib/catalog';
import { useRouter } from 'next/navigation';
import {
  ArrowDownRight,
  ArrowRight,
  BadgeCheck,
  Check,
  CircleEqual,
  Clock3,
  Database,
  FileSpreadsheet,
  Link2,
  ShieldCheck,
  TriangleAlert,
  X,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { useDemo } from '@/components/cockpit/demo-provider';
import { StateBadge } from '@/components/cockpit/page-elements';
import { formatEuro, getImpacts, themes, scenarioFixture } from '@/lib/demo';

const kindMeta = {
  direct: {
    label: 'Effet direct',
    icon: ArrowRight,
    className: 'bg-[var(--brand-soft)] text-[var(--brand-deep)]',
  },
  downstream: {
    label: 'Effet en chaîne',
    icon: ArrowDownRight,
    className: 'bg-[#fff3dc] text-[#8e580a]',
  },
  unchanged: {
    label: 'Ne change pas',
    icon: CircleEqual,
    className: 'bg-[#e4f7f0] text-[#08795e]',
  },
};

export function ImpactSheet() {
  const router = useRouter();
  const { state, impactOpen, setImpactOpen, simulate } = useDemo();
  const impacts = getImpacts(state.contract);
  const passedChecks = state.rule.checks.filter((check) => check.passed).length;
  const confirmed = sourceConfirmed(state,'sales');
  const allChecksPassed = passedChecks === state.rule.checks.length && confirmed;
  const supported = Boolean(scenarioFixture(state.contract));
  const readyToCompare = allChecksPassed && state.rule.status === 'staged' && supported;

  const compare = () => {
    simulate();
    setImpactOpen(false);
    router.push('/simulations/atlas');
  };

  return (
    <Sheet open={impactOpen} onOpenChange={setImpactOpen}>
      <SheetContent
        side="right"
        showCloseButton={false}
        className="liquid-sheet impact-liquid-sheet w-full gap-0 overflow-y-auto border-white/90 bg-white/78 p-0 backdrop-blur-[28px] sm:rounded-[34px] sm:shadow-[0_38px_100px_rgba(54,63,104,.18)]"
      >
        <SheetHeader className="sticky top-0 z-10 border-b border-white/80 bg-white/90 px-6 py-6 pr-16 backdrop-blur-2xl sm:rounded-t-[34px]">
          <SheetClose
            render={
              <Button
                variant="ghost"
                size="icon"
                className="liquid-control absolute right-3 top-3 z-30 size-11 rounded-full"
              />
            }
          >
            <X />
            <span className="sr-only">Fermer les impacts</span>
          </SheetClose>
          <StateBadge
            tone={
              readyToCompare
                ? 'success'
                : state.rule.status === 'needs-review'
                  ? 'warning'
                  : 'neutral'
            }
          >
            {readyToCompare
              ? 'Essai prêt à comparer'
              : state.rule.status === 'needs-review'
                ? 'Points à vérifier'
                : 'Essai à préparer'}
          </StateBadge>
          <SheetTitle className="mt-3 text-2xl font-semibold tracking-[-0.035em]">
            Impacts estimés de votre scénario
          </SheetTitle>
          <SheetDescription className="mt-1 text-[15px] leading-6">
            Votre version officielle reste inchangée. Les feuilles et la formule
            restent disponibles dans le détail expert.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-6 px-5 py-6 sm:px-6">
          {!supported&&<p role="alert" className="rounded-xl border border-amber-300 bg-amber-50 p-4">Ce cas n’a pas de résultat préparé. Choisissez le contrat Atlas de 480 000 EUR sur quatre mois à partir d’octobre 2026, probable à 75 %, avec 20 % / 60 jours ou 40 % / 30 jours. Aucun résultat ne sera extrapolé.</p>}
          <section className="rounded-[28px] border border-white/90 bg-[linear-gradient(145deg,rgba(255,255,255,.86),rgba(255,255,255,.46)),var(--pastel-lilac)] p-5 text-slate-900 shadow-[0_18px_45px_rgba(54,63,104,.1)]">
            <p className="text-[13px] font-semibold uppercase tracking-[0.11em] text-[var(--brand-deep)]">
              Ce que vous changez
            </p>
            <p className="mt-2 text-lg font-semibold">
              Contrat de {formatEuro(state.contract.amount, true)} prévu sur{' '}
              {state.contract.deliveryMonths} mois
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {state.contract.depositPercent} % d’acompte · solde à{' '}
              {state.contract.paymentDays} jours · démarrage{' '}
              {state.contract.startMonth.toLowerCase()}.
            </p>
          </section>

          <p className="rounded-xl border bg-white p-4">Source : source-atlas · {confirmed?'Exemple confirmé':'Confirmation nécessaire avant simulation'}. <Link className="underline" href="/parcours/installation?mode=review&step=3" onClick={()=>setImpactOpen(false)}>Examiner les sources</Link></p>
          <section aria-labelledby="impact-list-title">
            <h3
              id="impact-list-title"
              className="text-base font-semibold text-slate-900"
            >
              Ce qui changerait avant toute validation
            </h3>
            <div className="impact-chain mt-4 space-y-3">
              {impacts.map((impact) => {
                const meta = kindMeta[impact.kind];
                const Icon = meta.icon;
                return (
                  <article
                    key={impact.id}
                    className="impact-chain-card rounded-[24px] border border-white bg-white/82 p-4 shadow-[0_12px_30px_rgba(54,63,104,.08)]"
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`grid size-10 shrink-0 place-items-center rounded-[14px] ${meta.className}`}
                      >
                        <Icon className="size-4" />
                      </span>
                      <div className="min-w-0">
                        <p className="text-[12px] font-semibold uppercase tracking-[0.08em] text-slate-400">
                          {meta.label}
                        </p>
                        <h4 className="mt-1 font-semibold text-slate-900">
                          {impact.title}
                        </h4>
                        <p className="mt-1 text-sm leading-6 text-slate-500">
                          {impact.detail}
                        </p>
                        <div className="mt-3 flex flex-wrap items-center gap-2">
                          <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-[12px] font-medium text-slate-600">
                            <Clock3 className="size-3" /> {impact.horizon}
                          </span>
                          {impact.themes.map((key) => (
                            <span
                              key={key}
                              className="rounded-full bg-[var(--brand-soft)] px-2.5 py-1 text-[12px] font-medium text-[var(--brand-deep)]"
                            >
                              {
                                themes.find((theme) => theme.key === key)
                                  ?.shortLabel
                              }
                            </span>
                          ))}
                        </div>
                        <details className="mt-3 rounded-2xl bg-slate-50 px-3 py-2.5 text-sm">
                          <summary className="flex min-h-7 cursor-pointer items-center gap-2 font-semibold text-slate-500">
                            <Database className="size-4 shrink-0" /> Source et
                            niveau de confirmation
                          </summary>
                          <dl className="mt-3 grid gap-2 border-t border-slate-200/70 pt-3 sm:grid-cols-2">
                            <div className="flex items-start gap-2">
                              <Database className="mt-1 size-4 shrink-0 text-slate-400" />
                              <div>
                                <dt className="font-semibold text-slate-500">
                                  Source
                                </dt>
                                <dd className="mt-0.5 leading-6 text-slate-700">
                                  {impact.source}
                                </dd>
                              </div>
                            </div>
                            <div className="flex items-start gap-2">
                              <BadgeCheck className="mt-1 size-4 shrink-0 text-slate-400" />
                              <div>
                                <dt className="font-semibold text-slate-500">
                                  Confirmation
                                </dt>
                                <dd className="mt-0.5 leading-6 text-slate-700">
                                  {impact.confirmation}
                                </dd>
                              </div>
                            </div>
                          </dl>
                        </details>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section
            className={`rounded-[22px] border p-4 ${
              allChecksPassed
                ? 'border-[#cfeadf] bg-[#effaf6]'
                : 'border-[#f0d7a9] bg-[#fff8e9]'
            }`}
          >
            <div className="flex items-start gap-3">
              {allChecksPassed ? (
                <ShieldCheck className="mt-0.5 size-5 shrink-0 text-[#08795e]" />
              ) : (
                <TriangleAlert className="mt-0.5 size-5 shrink-0 text-[#99600d]" />
              )}
              <div>
                <h3
                  className={`font-semibold ${allChecksPassed ? 'text-[#086b54]' : 'text-[#784b08]'}`}
                >
                  {allChecksPassed
                    ? 'Les contrôles sont validés'
                    : `${passedChecks} vérifications réussies sur ${state.rule.checks.length}`}
                </h3>
                <ul
                  className={`mt-2 space-y-2 ${allChecksPassed ? 'text-[#386e61]' : 'text-[#7b6542]'}`}
                >
                  {state.rule.checks.map((check) => (
                    <li key={check.label} className="flex gap-2">
                      {check.passed ? (
                        <Check className="mt-1 size-4 shrink-0" />
                      ) : (
                        <TriangleAlert className="mt-1 size-4 shrink-0" />
                      )}
                      {check.label}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          <details className="group rounded-[22px] border border-slate-200 bg-white/70 p-4">
            <summary className="flex min-h-11 cursor-pointer list-none items-center gap-3 font-semibold text-slate-800">
              <FileSpreadsheet className="size-5 text-[var(--brand)]" />
              Voir la règle et les calculs impliqués
              <span className="ml-auto text-sm text-slate-400 group-open:rotate-90">
                ›
              </span>
            </summary>
            <div className="mt-4 border-t border-slate-200 pt-4 text-sm">
              <p className="font-semibold text-slate-800">Règle proposée</p>
              <p className="mt-1 leading-6 text-slate-500">
                {state.rule.proposedRule}
              </p>
              <div className="mt-3 rounded-xl bg-slate-900 p-3 font-mono text-[12px] leading-5 text-slate-100">
                {state.rule.schematicFormula}
              </div>
              <p className="mt-3 flex items-center gap-2 text-slate-500">
                <Link2 className="size-4" /> Feuilles :{' '}
                {state.rule.targetSheets.join(' · ')}
              </p>
              <p className="mt-2 text-[12px] leading-5 text-slate-400">
                Formule schématique de démonstration : aucun classeur réel n’est
                modifié.
              </p>
            </div>
          </details>
        </div>

        <SheetFooter className="sticky bottom-0 border-t border-white/80 bg-white/78 px-6 py-4 backdrop-blur-2xl sm:rounded-b-[34px]">
          <Button
            className="h-12 w-full rounded-full"
            onClick={
              readyToCompare
                ? compare
                : () => {
                    setImpactOpen(false);
                    router.push('/travail/ventes');
                  }
            }
          >
            {readyToCompare
              ? 'Comparer à la version officielle'
              : state.rule.status === 'available'
                ? 'Préparer le brouillon'
                : 'Corriger les points à vérifier'}
            <ArrowRight data-icon="inline-end" />
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
