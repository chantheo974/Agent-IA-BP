'use client';

import * as React from 'react';
import { themeRoute, themeWorkspaces, sheetViews } from '@/lib/catalog';
import { usePathname, useRouter } from 'next/navigation';
import {
  ArrowRight,
  Send,
  Sparkles,
  WandSparkles,
  X,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Textarea } from '@/components/ui/textarea';
import { CompanionBadge } from '@/components/cockpit/companion-mark';
import { useDemo } from '@/components/cockpit/demo-provider';

function specialistFor(pathname: string) {
  if (pathname.includes('ventes') || pathname.includes('atlas'))
    return 'À vos côtés pour cette décision';
  if (pathname.includes('suivi')) return 'À vos côtés chaque mois';
  if (pathname.includes('livrables')) return 'À vos côtés pour la synthèse';
  if (pathname.includes('expert')) return 'Traduit le modèle avec vous';
  return 'Votre compagnon de décision';
}

function contextFor(pathname: string, atlasSummary: string) {
  if (pathname.startsWith('/parcours/installation')) {
    return 'Personnalisation du cockpit. Les changements restent locaux jusqu’à leur enregistrement.';
  }
  if (pathname === '/parcours') {
    return 'Vue d’ensemble du parcours. Six thèmes disposent de cas préparés, de sources et de décisions locales dans cette démonstration.';
  }
  if (pathname.startsWith('/decisions')) {
    return 'Journal des décisions et anciennes versions restaurables.';
  }
  if (pathname.startsWith('/suivi-mensuel')) {
    return 'Suivi du réalisé, des écarts et de leur effet sur la trésorerie.';
  }
  if (pathname.startsWith('/livrables')) {
    return 'Synthèse dirigeant et formats de restitution de la version officielle.';
  }
  return atlasSummary;
}

export function CopilotSheet() {
  const router = useRouter();
  const pathname = usePathname();
  const {
    state,
    command,
    copilotOpen,
    setCopilotOpen,
    setImpactOpen,
    addChat,
    stageRevenueRule,
    setThemeMode,
  } = useDemo();
  const [message, setMessage] = React.useState('');
  const [composerFocused, setComposerFocused] = React.useState(false);
  const endRef = React.useRef<HTMLDivElement>(null);
  const sheet = sheetViews.find(s => pathname.endsWith('/feuilles/'+s.id));
  const routedTheme = themeWorkspaces.find(t => pathname.endsWith('/travail/'+t.slug));
  const scenario = state.themeScenarios.find(s => pathname.endsWith('/simulations/'+s.id));
  const themeKey = pathname.includes('ventes') || pathname.includes('/atlas') ? 'sales' : sheet?.theme ?? routedTheme?.key ?? scenario?.theme ?? state.activeTheme;
  const definition = themeWorkspaces.find(t => t.key === themeKey);
  const isAtlasContext = themeKey === 'sales' && !pathname.startsWith('/parcours/installation');
  const currentContext = definition ? `${definition.title} : ${definition.element}. ${definition.field} : ${state.themeDrafts[definition.key].value} ${definition.unit}. ${sheet ? 'Feuille '+sheet.title+'. ' : ''}Source fictive ${definition.sourceId}.` : contextFor(pathname,`Contrat Atlas : ${state.contract.deliveryMonths} mois, ${state.contract.depositPercent} % d’acompte et paiement partagé à ${state.contract.paymentDays} jours.`);

  React.useEffect(() => {
    if (copilotOpen) {
      const reduceMotion = window.matchMedia(
        '(prefers-reduced-motion: reduce)',
      ).matches;
      endRef.current?.scrollIntoView({
        behavior: reduceMotion ? 'auto' : 'smooth',
      });
    }
  }, [copilotOpen, state.chatMessages]);

  const prepare = () => {
    if (definition) { setThemeMode(definition.key,'auto'); command({type:'theme-preview',theme:definition.key}); setCopilotOpen(false); router.push(themeRoute(definition.key)); return; }
    setThemeMode('sales', 'auto');
    stageRevenueRule();
    setCopilotOpen(false);
    setImpactOpen(true);
    router.push('/travail/ventes');
  };

  const guide = () => {
    if (definition) { setThemeMode(definition.key,'guided'); addChat('assistant',`Commençons par la source ${definition.sourceId}, puis ${definition.field.toLowerCase()}. Les seules valeurs préparées sont ${definition.fixtures.map(f=>f.value).join(' ou ')}. Vous examinerez les impacts avant la simulation.`); setCopilotOpen(false); router.push(themeRoute(definition.key)); return; }
    setThemeMode('sales', 'guided');
    addChat(
      'assistant',
      'Je passe en mode guidé. Nous commencerons par le rythme de livraison, puis l’acompte et le délai de paiement.',
    );
    setCopilotOpen(false);
    router.push('/travail/ventes');
  };

  const send = () => {
    const trimmed = message.trim();
    if (!trimmed) return;
    addChat('user', trimmed);
    setMessage('');
    const lower = trimmed.toLocaleLowerCase('fr');
    if (definition) { addChat('assistant',`Pour ${definition.element}, votre hypothèse est ${state.themeDrafts[definition.key].value} ${definition.unit}. ${definition.fixtures.find(f=>f.value===state.themeDrafts[definition.key].value)?.explanation ?? 'Cette combinaison ne possède pas de fixture : aucun chiffre ne sera extrapolé.'} Confirmez d’abord la source. Le bouton Préparer l’essai examine le même brouillon que votre fiche ; il ne valide aucune version.`); return; }
    if (
      isAtlasContext &&
      (lower.includes('4 mois') || lower.includes('quatre mois'))
    ) {
      addChat(
        'assistant',
        'Je peux préparer une reconnaissance du revenu sur quatre mois. Ouvrez le brouillon pour vérifier précisément ce qui changera avant la simulation.',
      );
      return;
    }
    if (
      isAtlasContext &&
      (lower.includes('trésorerie') || lower.includes('cash'))
    ) {
      addChat(
        'assistant',
        'Le contrat augmente l’activité, mais les achats commencent avant le paiement du solde. L’acompte et le délai client sont les deux leviers les plus directs.',
      );
      return;
    }
    addChat(
      'assistant',
      isAtlasContext
        ? 'J’ai compris votre intention. Dans cette démo, je peux la transformer en essai sur le contrat Atlas ou vous guider pour la préciser.'
        : 'J’ai compris votre question. Cette démonstration illustre cette page avec des données préparées ; aucune donnée financière réelle n’est analysée.',
    );
  };

  return (
    <Sheet open={copilotOpen} onOpenChange={setCopilotOpen}>
      <SheetContent
        side="right"
        showCloseButton={false}
        className="liquid-sheet copilot-liquid-sheet w-full gap-0 border-white/90 bg-white/78 p-0 backdrop-blur-[28px] sm:rounded-[34px] sm:shadow-[0_38px_100px_rgba(54,63,104,.18)]"
      >
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
          <span className="sr-only">Fermer le copilote</span>
        </SheetClose>
        <SheetHeader className="border-b border-white/80 bg-white/70 px-5 py-5 pr-14 backdrop-blur-2xl sm:rounded-t-[34px]">
          <div className="flex items-center gap-3">
            <CompanionBadge
              size="large"
              motion={composerFocused || message.trim() ? 'engaged' : 'awake'}
            />
            <div>
              <SheetTitle className="text-lg font-semibold">
                Copilote
              </SheetTitle>
              <SheetDescription className="text-[13px] text-[var(--brand)]">
                {specialistFor(pathname)}
              </SheetDescription>
            </div>
          </div>
        </SheetHeader>

        <div className="flex min-h-0 flex-1 flex-col">
          <div
            role="log"
            aria-label="Conversation avec votre compagnon"
            aria-live="polite"
            aria-relevant="additions"
            className="flex-1 space-y-4 overflow-y-auto px-4 py-5"
          >
            <div className="rounded-[24px] border border-white/90 bg-[linear-gradient(145deg,rgba(255,255,255,.86),rgba(255,255,255,.48)),var(--pastel-sky)] p-4 shadow-[0_12px_30px_rgba(54,63,104,.07)]">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
                <Sparkles className="size-4 text-[var(--brand)]" /> Contexte
                actuel
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                {currentContext}
              </p>
            </div>

            {state.chatMessages.map((item) => (
              <div
                key={item.id}
                className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[88%] rounded-[22px] px-4 py-3 text-sm leading-6 shadow-[0_10px_26px_rgba(54,63,104,.07)] ${
                    item.role === 'user'
                      ? 'rounded-br-md bg-[var(--brand-deep)] text-white'
                      : 'rounded-bl-md border border-white bg-white/86 text-slate-600'
                  }`}
                >
                  {item.text}
                </div>
              </div>
            ))}
            <div ref={endRef} />
          </div>

          <div className="border-t border-white/80 bg-white/72 p-4 backdrop-blur-2xl sm:rounded-b-[34px]">
            {(isAtlasContext || definition) ? (
              <div className="mb-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                <Button
                  variant="outline"
                  className="min-h-12 rounded-2xl border-[var(--brand)]/20 bg-[var(--brand-soft)] text-[var(--brand-deep)]"
                  onClick={guide}
                >
                  Guide-moi
                </Button>
                <Button className="min-h-12 rounded-2xl" onClick={prepare}>
                  <WandSparkles data-icon="inline-start" /> Préparer l’essai
                </Button>
              </div>
            ) : null}
            <div className="flex items-end gap-2">
              <Textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onFocus={() => setComposerFocused(true)}
                onBlur={() => setComposerFocused(false)}
                onKeyDown={(event) => {
                  if (
                    event.key === 'Enter' &&
                    !event.shiftKey &&
                    !event.nativeEvent.isComposing
                  ) {
                    event.preventDefault();
                    send();
                  }
                }}
                placeholder={
                  isAtlasContext
                    ? 'Ex. : la vente doit s’étaler sur quatre mois…'
                    : 'Posez une question sur cette page…'
                }
                aria-label="Votre message au copilote"
                className="min-h-12 max-h-32 resize-none overflow-y-auto rounded-2xl bg-white text-base"
              />
              <Button
                size="icon"
                className="size-12 shrink-0 rounded-2xl"
                onClick={send}
                disabled={!message.trim()}
                aria-label="Envoyer le message"
              >
                <Send className="size-4" />
              </Button>
            </div>
            <p className="mt-2 flex items-center gap-1.5 text-[12px] text-slate-400">
              <ArrowRight className="size-3" /> Démo locale : réponses
              préparées, aucun service d’IA connecté.
            </p>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
