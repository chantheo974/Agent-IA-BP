'use client';

import { useState } from 'react';
import { SheetLinks, SourcesPanel } from '../../demo-parts';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CircleHelp,
  FileSpreadsheet,
  Info,
  MonitorUp,
  Sparkles,
  TriangleAlert,
  Undo2,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import { CompanionBadge } from '@/components/cockpit/companion-mark';
import { Input } from '@/components/ui/input';
import { NumberField } from '@/components/cockpit/number-field';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { useDemo } from '@/components/cockpit/demo-provider';
import {
  PageHeading,
  StateBadge,
  Surface,
} from '@/components/cockpit/page-elements';
import { formatEuro, initialContract } from '@/lib/demo';

export default function SalesWorkspacePage() {
  const router = useRouter();
  const {
    state,
    setThemeMode,
    updateContract,
    undoContract,
    discardDraft,
    stageRevenueRule,
    setImpactOpen,
    setCopilotOpen,
  } = useDemo();
  const [discard,setDiscard] = useState(false);
  const mode = state.themeModes.sales;
  const contract = state.contract;
  const nextActionLabel =
    state.rule.status === 'staged'
      ? 'Voir les impacts'
      : mode === 'auto'
        ? state.rule.status === 'needs-review'
          ? 'Corriger et voir les impacts'
          : 'Préparer et voir les impacts'
        : 'Continuer avec le copilote';
  const nextActionDetail =
    state.rule.status === 'staged'
      ? 'Le brouillon est prêt. Vérifiez maintenant ses effets.'
      : mode === 'auto'
        ? 'Le copilote prépare le brouillon, puis vous montre ses effets.'
        : 'Le copilote vous accompagne dans le prochain choix.';

  const continueWork = () => {
    if (state.rule.status === 'staged') {
      setImpactOpen(true);
    } else if (mode === 'auto') {
      stageRevenueRule();
      setImpactOpen(true);
    } else {
      setCopilotOpen(true);
    }
  };

  return (
    <div className="spatial-page">
      <Button
        variant="ghost"
        className="mb-5 h-11 rounded-full px-3 text-slate-500"
        onClick={() => router.push('/parcours')}
      >
        <ArrowLeft data-icon="inline-start" /> Voir le parcours
      </Button>

      <PageHeading
        eyebrow="Ventes et contrats"
        title="Préparer le contrat Atlas."
        description="Faites vos essais ici. Ils restent dans ce brouillon et ne changent pas votre version officielle tant que vous ne les validez pas."
        actions={
          state.contractUndo.length > 0 ? (
            <Button
              variant="outline"
              className="h-11 rounded-full bg-white/70"
              onClick={undoContract}
            >
              <Undo2 data-icon="inline-start" /> Annuler mon dernier changement
            </Button>
          ) : undefined
        }
      />

      <SheetLinks ids={['contracts-data','contracts','revenue','assumptions']}/>
      <Surface><h2 className="text-xl font-semibold">Informations métier et provenance</h2><p>Offre : Inspection industrielle · forfait de {formatEuro(contract.amount)} HT · TVA fictive 20 %. Cas préparé du 01/10/2026 au 31/01/2027. Facturation : acompte à la commande puis solde à la livraison finale.</p><label className="mt-4 block">Probabilité (%)<NumberField value={contract.probability ?? 75} min={0} max={100} onCommit={probability=>updateContract({probability})}/></label><label className="mt-4 block">Statut<select className="w-full rounded-xl border p-3" value={contract.commercialStatus} onChange={e=>updateContract({commercialStatus:e.target.value as 'probable'|'signed'})}><option value="probable">Probable</option><option value="signed">Signé</option></select></label><p className="mt-3">Le délai client est partagé par l’offre. Fixtures couvertes : Atlas probable à 75 %, 480 000 EUR, quatre mois, 20 % / 60 jours ou 40 % / 30 jours. Les autres combinaisons restent sans résultat.</p><Button className="mt-4" variant="outline" onClick={()=>setDiscard(true)}>Abandonner le brouillon Atlas</Button>{discard&&<div role="alertdialog" aria-label="Abandonner le brouillon Atlas"><p>Revenir aux conditions de la version locale ?</p><Button onClick={()=>{discardDraft();setDiscard(false);}}>Confirmer l’abandon</Button><Button variant="ghost" onClick={()=>setDiscard(false)}>Garder</Button></div>}</Surface><Surface><h2 className="font-semibold">Cas représentatifs préparés</h2><p>Atlas : forfait 480 000 EUR HT, probable à 75 %, du 1er octobre 2026 sur quatre mois. Ces boutons préparent toutes les conditions annoncées dans un seul brouillon annulable.</p><div className="mt-4 flex flex-wrap gap-3"><Button variant="outline" onClick={()=>updateContract({...initialContract,revenueRule:'spread'})}>Cas préparé : 20 % / 60 jours</Button><Button variant="outline" onClick={()=>updateContract({...initialContract,revenueRule:'spread',depositPercent:40,paymentDays:30})}>Cas préparé : 40 % / 30 jours</Button></div></Surface><SourcesPanel theme="sales"/>
      <div className="sales-workspace-stage mt-8 grid min-w-0 gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="sales-main-stack min-w-0 space-y-5">
          <Surface variant="tinted" depth={2} className="md:hidden">
            <div className="flex items-start gap-3">
              <span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-[var(--brand-soft)] text-[var(--brand-deep)]">
                <MonitorUp className="size-5" />
              </span>
              <div>
                <h2 className="font-semibold text-slate-900">
                  Saisie sur écran plus large
                </h2>
                <p className="mt-1 text-sm leading-6 text-slate-500">
                  Sur téléphone, vous pouvez comprendre les impacts, simuler et
                  décider. Pour modifier les hypothèses détaillées, ouvrez ce
                  brouillon sur tablette ou ordinateur.
                </p>
                <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <dt className="text-slate-400">Acompte</dt>
                    <dd className="mt-1 font-semibold text-slate-800">
                      {contract.depositPercent} %
                    </dd>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <dt className="text-slate-400">Paiement</dt>
                    <dd className="mt-1 font-semibold text-slate-800">
                      {contract.paymentDays} jours
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </Surface>

          <Surface
            variant="tinted"
            depth={3}
            className="sales-mode-card rounded-[32px]"
          >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <StateBadge>Brouillon</StateBadge>
                  <StateBadge
                    tone={
                      contract.commercialStatus === 'signed'
                        ? 'success'
                        : 'warning'
                    }
                  >
                    {contract.commercialStatus === 'signed'
                      ? 'Signé'
                      : 'Probable · non signé'}
                  </StateBadge>
                </div>
                <h2 className="mt-3 text-xl font-semibold tracking-[-0.025em] text-slate-900">
                  Comment souhaitez-vous avancer ?
                </h2>
              </div>
              <div className="sales-mode-selector grid w-full grid-cols-2 gap-2 rounded-[18px] p-1.5 sm:min-w-[310px] sm:w-auto">
                <Button
                  aria-pressed={mode === 'guided'}
                  variant="ghost"
                  className="sales-mode-choice min-h-11 rounded-[14px]"
                  onClick={() => setThemeMode('sales', 'guided')}
                >
                  <CircleHelp data-icon="inline-start" />
                  Guide-moi
                </Button>
                <Button
                  aria-pressed={mode === 'auto'}
                  variant="ghost"
                  className="sales-mode-choice min-h-11 rounded-[14px]"
                  onClick={() => setThemeMode('sales', 'auto')}
                >
                  <Sparkles data-icon="inline-start" /> Fais-le pour moi
                </Button>
              </div>
            </div>

            <div className="mt-5 rounded-[20px] border border-[var(--brand)]/15 bg-[var(--brand-soft)] p-4">
              <div className="flex items-start gap-3">
                <span className="shrink-0">
                  <CompanionBadge size="small" />
                </span>
                <div>
                  <p className="font-semibold text-[var(--brand-deep)]">
                    {mode === 'auto'
                      ? 'Le copilote peut préparer la version recommandée.'
                      : 'Le copilote vous explique chaque choix.'}
                  </p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    {mode === 'auto'
                      ? 'Il placera la règle sur quatre mois dans le brouillon, vérifiera les garde-fous et vous conduira à la comparaison.'
                      : 'Commencez par le rythme de livraison. Rien ne sera appliqué sans votre validation finale.'}
                  </p>
                </div>
              </div>
            </div>
          </Surface>

          <Surface
            variant="solid"
            depth={2}
            className="sales-form-card hidden rounded-[36px] md:block"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-[var(--brand)]">
                  Hypothèses du contrat
                </p>
                <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em]">
                  Ce qui décrit la décision
                </h2>
              </div>
              <p className="rounded-full bg-slate-100 px-3 py-2 text-[12px] font-semibold text-slate-500">
                Montant négocié conservé
              </p>
            </div>

            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <label htmlFor="contract-customer" className="block">
                <span className="text-sm font-semibold text-slate-700">
                  Client
                </span>
                <Input
                  id="contract-customer"
                  value={contract.customer}
                  onChange={(event) =>
                    updateContract({ customer: event.target.value })
                  }
                  className="mt-2 h-12 rounded-2xl bg-white px-4 text-base"
                />
              </label>
              <label htmlFor="contract-amount" className="block">
                <span className="text-sm font-semibold text-slate-700">
                  Montant du contrat
                </span>
                <div className="relative mt-2">
                  <NumberField
                    id="contract-amount"
                    type="number"
                    value={contract.amount}
                    min={10000}
                    step={10000}
                    onCommit={(amount) => updateContract({ amount })}
                    className="h-12 rounded-2xl bg-white px-4 pr-10 text-base"
                  />
                  <span className="pointer-events-none absolute right-4 top-6 -translate-y-1/2 text-sm font-semibold text-slate-400">
                    €
                  </span>
                </div>
                <span className="mt-1.5 block text-[12px] text-slate-400">
                  {formatEuro(contract.amount, true)}
                </span>
              </label>
              <label htmlFor="contract-start" className="block">
                <span className="text-sm font-semibold text-slate-700">
                  Démarrage prévu
                </span>
                <Select
                  value={contract.startMonth}
                  onValueChange={(value) =>
                    value && updateContract({ startMonth: String(value) })
                  }
                >
                  <SelectTrigger
                    id="contract-start"
                    className="mt-2 h-12 w-full rounded-2xl bg-white px-4 text-base"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {['Octobre 2026', 'Novembre 2026', 'Janvier 2027'].map(
                      (month) => (
                        <SelectItem
                          key={month}
                          value={month}
                          className="min-h-10 px-3"
                        >
                          {month}
                        </SelectItem>
                      ),
                    )}
                  </SelectContent>
                </Select>
              </label>
              <label htmlFor="contract-cycle" className="block">
                <span className="text-sm font-semibold text-slate-700">
                  Cycle de livraison
                </span>
                <Select
                  value={String(contract.deliveryMonths)}
                  onValueChange={(value) =>
                    value && updateContract({ deliveryMonths: Number(value) })
                  }
                >
                  <SelectTrigger
                    id="contract-cycle"
                    className="mt-2 h-12 w-full rounded-2xl bg-white px-4 text-base"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[1, 3, 4, 6, 9, 12].map((months) => (
                      <SelectItem
                        key={months}
                        value={String(months)}
                        className="min-h-10 px-3"
                      >
                        {months} {months === 1 ? 'mois' : 'mois'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </label>
            </div>

            <div className="mt-7 grid gap-6 border-t border-slate-200/70 pt-6 lg:grid-cols-2">
              <div>
                <div className="flex items-center justify-between gap-3">
                  <label
                    htmlFor="deposit-slider"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Acompte à la commande
                  </label>
                  <span className="rounded-full bg-[var(--brand-soft)] px-3 py-1 text-sm font-semibold text-[var(--brand-deep)]">
                    {contract.depositPercent} %
                  </span>
                </div>
                <Slider
                  id="deposit-slider"
                  min={0}
                  max={60}
                  step={5}
                  value={[contract.depositPercent]}
                  onValueChange={(values) =>
                    updateContract({
                      depositPercent: Number((values as number[])[0]),
                    })
                  }
                  className="mt-5"
                />
                <p className="mt-4 text-[13px] leading-5 text-slate-500">
                  Un acompte plus élevé finance une partie des achats avant la
                  livraison.
                </p>
              </div>
              <div>
                <label
                  htmlFor="payment-delay"
                  className="text-sm font-semibold text-slate-700"
                >
                  Délai de paiement du solde
                </label>
                <Select
                  value={String(contract.paymentDays)}
                  onValueChange={(value) =>
                    value && updateContract({ paymentDays: Number(value) })
                  }
                >
                  <SelectTrigger
                    id="payment-delay"
                    className="mt-2 h-12 w-full rounded-2xl bg-white px-4 text-base"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[0, 30, 45, 60, 90].map((days) => (
                      <SelectItem
                        key={days}
                        value={String(days)}
                        className="min-h-10 px-3"
                      >
                        {days === 0 ? 'Comptant' : `${days} jours`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="mt-3 text-[13px] leading-5 text-slate-500">
                  Le montant vendu ne change pas, mais l’argent arrive plus
                  tard.
                </p>
              </div>
            </div>
          </Surface>
        </div>

        <aside className="sales-rule-rail min-w-0 space-y-5">
          <Surface
            variant="floating"
            depth={3}
            className="sales-rule-card rounded-[32px]"
          >
            <div className="flex items-start gap-3">
              <span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-[var(--brand-soft)] text-[var(--brand-deep)]">
                <FileSpreadsheet className="size-5" />
              </span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-semibold text-slate-900">
                    Règle de revenu
                  </h2>
                  <StateBadge
                    tone={
                      state.rule.status === 'staged'
                        ? 'success'
                        : state.rule.status === 'needs-review'
                          ? 'warning'
                          : 'neutral'
                    }
                  >
                    {state.rule.status === 'staged'
                      ? 'Dans le brouillon'
                      : state.rule.status === 'needs-review'
                        ? 'À revalider'
                        : 'Disponible'}
                  </StateBadge>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  {state.rule.businessLabel}
                </p>
              </div>
            </div>

            <div className="mt-5 rounded-[18px] bg-slate-50 p-4">
              <p className="text-[12px] font-semibold uppercase tracking-[0.08em] text-slate-400">
                Ce que le copilote adaptera
              </p>
              <p className="mt-2 text-sm font-semibold text-slate-800">
                {state.rule.proposedRule}
              </p>
              <p className="mt-2 text-[13px] leading-5 text-slate-500">
                Feuilles métier : {state.rule.targetSheets.join(' et ')}. Le
                moteur central reste verrouillé.
              </p>
            </div>

            <ul className="mt-4 space-y-2">
              {state.rule.checks.map((check) => (
                <li
                  key={check.label}
                  className="flex gap-2 text-sm text-slate-600"
                >
                  {check.passed ? (
                    <Check className="mt-1 size-4 shrink-0 text-[#0a8a68]" />
                  ) : (
                    <TriangleAlert className="mt-1 size-4 shrink-0 text-[#99600d]" />
                  )}
                  {check.label}
                </li>
              ))}
            </ul>

            <div className="mt-5 rounded-[22px] border border-white/90 bg-[linear-gradient(145deg,rgba(255,255,255,.84),rgba(255,255,255,.46)),var(--brand-soft)] p-3 shadow-[0_12px_30px_rgba(54,63,104,.08)] backdrop-blur-2xl">
              <div className="flex items-start gap-3 px-1 py-1">
                <span
                  aria-hidden="true"
                  className="grid size-9 shrink-0 place-items-center rounded-[13px] bg-white/78 text-[var(--brand-deep)] shadow-sm"
                >
                  <Sparkles className="size-4" />
                </span>
                <div className="min-w-0">
                  <p className="text-[12px] font-semibold uppercase tracking-[0.08em] text-[var(--brand-deep)]">
                    Prochaine étape
                  </p>
                  <p className="mt-1 text-sm leading-5 text-slate-600">
                    {nextActionDetail}
                  </p>
                </div>
              </div>
              <Button
                className="mt-3 h-11 w-full rounded-[16px] px-4"
                onClick={continueWork}
              >
                {nextActionLabel}
                <ArrowRight data-icon="inline-end" />
              </Button>
            </div>
          </Surface>

          <div
            role="note"
            className="sales-warning-card rounded-[22px] border border-white/90 bg-white/52 p-4 shadow-[0_16px_38px_rgba(54,63,104,.09)] backdrop-blur-[28px] xl:-ml-5 xl:mr-4 xl:-translate-y-2"
          >
            <div className="flex items-start gap-3.5">
              <span
                aria-hidden="true"
                className="grid size-10 shrink-0 place-items-center rounded-[14px] bg-[#fff0dc] text-[#95600e] shadow-[inset_0_1px_0_rgba(255,255,255,.9)]"
              >
                <Info className="size-[18px]" />
              </span>
              <div>
                <h2 className="text-base font-semibold text-slate-800">
                  Probable n’est pas signé
                </h2>
                <p className="mt-1 text-sm leading-5 text-slate-500">
                  Même estimé à 100 %, le contrat reste une hypothèse tant qu’il
                  n’est pas signé.
                </p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
