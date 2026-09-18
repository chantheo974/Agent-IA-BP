'use client';

import Link from 'next/link';
import { themeRoute } from '@/lib/catalog';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  Bookmark,
  Check,
  Clock3,
  GitBranch,
  History,
  RotateCcw,
  ShieldCheck,
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
  PageHeading,
  StateBadge,
  Surface,
} from '@/components/cockpit/page-elements';
import { formatEuro } from '@/lib/demo';

export default function DecisionsPage() {
  const router = useRouter();
  const { state, restoreVersion, command } = useDemo();
  const active = state.referenceVersions[0];

  return (
    <div className="spatial-page">
      <PageHeading
        eyebrow="Décisions"
        title="Vos décisions et leurs versions."
        description="Chaque validation crée un jalon. Réutiliser une ancienne version n’efface rien : une nouvelle version officielle est créée et le chemin reste lisible."
        actions={
          <Button
            className="h-11 rounded-full"
            onClick={() => router.push('/simulations')}
          >
            Tester une décision
            <ArrowRight data-icon="inline-end" />
          </Button>
        }
      />

      <Surface><h2 className="text-xl font-semibold">Décisions des autres thèmes</h2><p>Chaque adoption ou restauration crée une version locale de son thème. Les états financiers consolidés ne sont pas recalculés.</p>{state.themeVersions.map(version=><article key={version.id} className="mt-5 rounded-xl border bg-white p-4"><h3 className="font-semibold">{version.reason}</h3><p>{version.createdAt} · {version.id}</p><div className="mt-3 flex flex-wrap gap-3"><Link className="underline" href={themeRoute(version.theme)}>Hypothèses concernées</Link>{version.scenarioId&&<Link className="underline" href={'/simulations/'+version.scenarioId}>Simulation d’origine</Link>}<Button variant="outline" onClick={()=>{if(window.confirm('Créer une nouvelle version locale depuis ce jalon ? Le brouillon actuel reste récupérable par annulation.'))command({type:'version-restore',id:version.id,versionId:crypto.randomUUID(),at:new Date().toISOString()});}}>Restaurer dans une nouvelle version</Button></div></article>)}{!state.themeVersions.length&&<p className="mt-3">Aucune décision adoptée sur les autres thèmes.</p>}</Surface>
      <section className="decision-history-stack mt-9 grid gap-5 xl:grid-cols-[.82fr_1.18fr] xl:gap-0">
        <Surface
          variant="tinted"
          depth={3}
          className="decision-active-card z-[3] rounded-[36px] bg-[linear-gradient(145deg,rgba(255,255,255,.9),rgba(255,255,255,.48)),var(--pastel-lilac)] text-slate-900"
        >
          <div className="flex items-start justify-between gap-3">
            <span className="grid size-12 place-items-center rounded-[18px] bg-white/76 text-[var(--brand-deep)] shadow-sm">
              <ShieldCheck className="size-6" />
            </span>
            <StateBadge tone="success">Version officielle</StateBadge>
          </div>
          <p className="mt-6 text-sm text-slate-500">
            Votre trajectoire officielle
          </p>
          <h2 className="mt-1 text-2xl font-semibold tracking-[-0.035em]">
            {active.label}
          </h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            {active.reason}
          </p>
          <dl className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-[20px] bg-white/68 p-4 shadow-sm">
              <dt className="text-[12px] text-slate-500">Point bas de cash</dt>
              <dd className="mt-1 text-lg font-semibold">
                {formatEuro(active.metrics.cashLowPoint, true)}
              </dd>
            </div>
            <div className="rounded-[20px] bg-white/68 p-4 shadow-sm">
              <dt className="text-[12px] text-slate-500">Visibilité</dt>
              <dd className="mt-1 text-lg font-semibold">
                {active.metrics.runway} mois
              </dd>
            </div>
          </dl>
          <p className="mt-5 flex items-center gap-2 text-[13px] text-slate-500">
            <Clock3 className="size-4" /> {active.createdAt}
          </p>
        </Surface>

        <Surface
          variant="solid"
          depth={2}
          className="decision-journal-card rounded-[36px] xl:-ml-8 xl:translate-y-9 xl:pl-14"
        >
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-500">Journal</p>
              <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em]">
                Les choix qui expliquent la version officielle
              </h2>
            </div>
            <History className="size-5 text-[var(--brand)]" />
          </div>
          <div className="mt-5 space-y-3">
            {state.decisions.map((decision, index) => (
              <article
                key={decision.id}
                className="relative flex items-start gap-4 rounded-[22px] bg-slate-50/82 p-4"
              >
                <span
                  className={`grid size-10 shrink-0 place-items-center rounded-full ${
                    decision.status === 'applied'
                      ? 'bg-[#e1f6ee] text-[#08795e]'
                      : decision.status === 'restored'
                        ? 'bg-[#fff2dc] text-[#99600d]'
                        : 'bg-[var(--brand-soft)] text-[var(--brand-deep)]'
                  }`}
                >
                  {decision.status === 'applied' ? (
                    <Check className="size-4" />
                  ) : decision.status === 'restored' ? (
                    <RotateCcw className="size-4" />
                  ) : (
                    <Bookmark className="size-4" />
                  )}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h3 className="font-semibold text-slate-900">
                      {decision.title}
                    </h3>
                    <span className="text-[12px] text-slate-400">
                      {decision.createdAt}
                    </span>
                  </div>
                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    {decision.summary}
                  </p>
                </div>
                {index < state.decisions.length - 1 ? (
                  <span className="absolute ml-[19px] mt-10 h-7 w-px bg-slate-200" />
                ) : null}
              </article>
            ))}
          </div>
        </Surface>
      </section>

      <section className="mt-8">
        <div>
          <p className="text-sm font-semibold text-[var(--brand)]">
            Anciennes versions
          </p>
          <h2 className="mt-1 text-2xl font-semibold tracking-[-0.035em] text-slate-900">
            Réutiliser un ancien jalon sans perdre la suite
          </h2>
        </div>
        <div className="version-card-deck mt-5 grid gap-5 xl:grid-cols-2">
          {state.referenceVersions.length === 1 ? (
            <Surface
              variant="solid"
              depth={1}
              className="version-stack-card rounded-[32px]"
            >
              <GitBranch className="size-6 text-[var(--brand)]" />
              <h3 className="mt-5 text-lg font-semibold text-slate-900">
                Aucune ancienne version pour le moment
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                La première version restera ici dès qu’une nouvelle décision
                sera validée.
              </p>
            </Surface>
          ) : (
            state.referenceVersions.slice(1).map((version) => (
              <Surface
                key={version.id}
                variant="floating"
                depth={1}
                className="version-stack-card rounded-[32px]"
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="grid size-11 place-items-center rounded-2xl bg-[var(--brand-soft)] text-[var(--brand-deep)]">
                    <GitBranch className="size-5" />
                  </span>
                  <StateBadge tone="neutral">Ancienne</StateBadge>
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-900">
                  {version.label}
                </h3>
                <p className="mt-1 text-sm leading-6 text-slate-500">
                  {version.reason}
                </p>
                <div className="mt-4 flex flex-wrap gap-2 text-[12px] font-medium text-slate-500">
                  <span className="rounded-full bg-slate-100 px-2.5 py-1">
                    Point bas {formatEuro(version.metrics.cashLowPoint, true)}
                  </span>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1">
                    {version.metrics.runway} mois
                  </span>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1">
                    {version.createdAt}
                  </span>
                </div>
                <Dialog>
                  <DialogTrigger
                    render={
                      <Button
                        variant="outline"
                        className="mt-5 h-11 rounded-full bg-white"
                      />
                    }
                  >
                    <RotateCcw data-icon="inline-start" /> Utiliser comme
                    nouvelle version
                  </DialogTrigger>
                  <DialogContent
                    showCloseButton={false}
                    className="max-w-[450px] rounded-[28px] p-6"
                  >
                    <DialogHeader>
                      <DialogTitle className="text-xl font-semibold">
                        Utiliser cette version comme nouvelle version officielle
                        ?
                      </DialogTitle>
                      <DialogDescription className="text-[15px] leading-6">
                        Un nouveau jalon sera créé à partir de{' '}
                        {version.label.toLowerCase()}. Toutes les versions plus
                        récentes resteront visibles. Le brouillon reprendra ces
                        conditions ; son état précédent restera récupérable avec
                        « Annuler mon dernier changement » dans Ventes et
                        contrats.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="-mx-6 -mb-6 mt-3 rounded-b-[28px] px-6">
                      <DialogClose
                        render={
                          <Button
                            variant="outline"
                            className="h-11 rounded-full"
                          />
                        }
                      >
                        Annuler
                      </DialogClose>
                      <DialogClose
                        render={
                          <Button
                            className="h-11 rounded-full"
                            onClick={() => restoreVersion(version.id)}
                          />
                        }
                      >
                        Utiliser comme version officielle
                      </DialogClose>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </Surface>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
