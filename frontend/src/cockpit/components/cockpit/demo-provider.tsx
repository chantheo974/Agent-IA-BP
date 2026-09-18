'use client';

import * as React from 'react';

import {
  calculateScenario,
  scenarioFixture,
  migrateDemoState,
  createInitialState,
  getContractChecks,
  getRuleChecks,
  type BrandProfile,
  type ContractInputs,
  type DemoState,
  type ThemeKey,
  type ThemeMode,
} from '@/lib/demo';

import { reduceSharedState, sourceConfirmed, type DemoCommand } from '@/lib/catalog';

const STORAGE_KEY = 'cockpit-demo:v2';

// The offer payment term has one draft value across sales, treasury and detailed views.
function syncCashDraft(state: DemoState, contract: ContractInputs) {
  const cash = state.themeDrafts.cash;
  if (cash.value === String(contract.paymentDays)) return state.themeDrafts;
  return {...state.themeDrafts, cash: {...cash, value: String(contract.paymentDays), undo: [...cash.undo, cash.value], status: 'draft' as const, scenarioId: undefined, error: undefined}};
}

interface DemoContextValue {
  state: DemoState;
  command: (command: DemoCommand) => void;
  hydrated: boolean;
  impactOpen: boolean;
  setImpactOpen: (open: boolean) => void;
  copilotOpen: boolean;
  setCopilotOpen: (open: boolean) => void;
  toast?: string;
  notify: (message: string) => void;
  dismissToast: () => void;
  setThemeMode: (theme: ThemeKey, mode: ThemeMode) => void;
  updateContract: (patch: Partial<ContractInputs>) => void;
  undoContract: () => void;
  discardDraft: () => void;
  stageRevenueRule: () => void;
  simulate: (patch?: Partial<ContractInputs>) => void;
  saveScenario: () => void;
  loadSavedVariant: (id: string) => void;
  applyScenario: () => void;
  restoreVersion: (id: string) => void;
  setBrand: (brand: Partial<BrandProfile>) => void;
  addChat: (role: 'assistant' | 'user', text: string) => void;
  importMonthly: (fileName: string) => void;
  completeOnboarding: (
    objective?: string,
    options?: { preservePhase?: boolean },
  ) => void;
  resetDemo: () => void;
}

const DemoContext = React.createContext<DemoContextValue | null>(null);


export function DemoProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = React.useState<DemoState>(() =>
    createInitialState(),
  );
  const [hydrated, setHydrated] = React.useState(false);
  const [impactOpen, setImpactOpen] = React.useState(false);
  const [copilotOpen, setCopilotOpen] = React.useState(false);
  const [toast, setToast] = React.useState<string>();
  const toastTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const storageBlocked = React.useRef(false);
  const lastContractEdit = React.useRef<{ fields: string; at: number } | null>(
    null,
  );

  React.useEffect(() => {
    let restored: DemoState | null = null;
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY) ?? window.localStorage.getItem('cockpit-demo:v1');
      restored = stored ? migrateDemoState(stored) : null;
      if (stored && !restored) {storageBlocked.current=true;setToast('Le stockage existant est illisible. Il est conservé sans écrasement ; cette session ne sera pas enregistrée avant une réinitialisation explicite.');}
    } catch {
      /* Private browsing can disable local storage. */
    }
    // Hydration deliberately reconciles the browser-only demo state after mount.
    // oxlint-disable-next-line react/react-compiler
    if (restored) setState(restored);
    // oxlint-disable-next-line react/react-compiler
    setHydrated(true);
  }, []);

  React.useEffect(() => {
    if (!hydrated || storageBlocked.current) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // Surface the external storage failure instead of silently losing this session.
      // oxlint-disable-next-line react/react-compiler
      setToast(
        'Cet appareil ne peut pas enregistrer vos essais. Gardez cette page ouverte pour ne pas les perdre.',
      );
    }
  }, [hydrated, state]);

  React.useEffect(
    () => () => {
      if (toastTimer.current) clearTimeout(toastTimer.current);
    },
    [],
  );

  const notify = React.useCallback((message: string) => {
    setToast(message);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(undefined), 6500);
  }, []);

  const dismissToast = React.useCallback(() => setToast(undefined), []);

  const command = React.useCallback((request: DemoCommand) => {
    setState(current => {
      const next = { ...current, ...reduceSharedState(current, request) };
      if (next.themeDrafts.cash.value !== current.themeDrafts.cash.value) return {...next,contract:{...current.contract,paymentDays:/^\d+$/.test(next.themeDrafts.cash.value)?Number(next.themeDrafts.cash.value):current.contract.paymentDays},contractUndo:[...current.contractUndo,current.contract].slice(-12),scenarioStatus:'draft' as const,simulatedMetrics:undefined};
      if (request.type === 'source-fact' && next.sources !== current.sources) {
        const fact = current.sources.find(s => s.id === request.sourceId)?.facts.find(f => f.id === request.factId);
        if (fact?.themes.includes('sales') || fact?.themes.includes('cash')) return {...next,scenarioStatus:'draft' as const,simulatedMetrics:undefined};
      }
      return next;
    });
  }, []);

  const addChat = React.useCallback(
    (role: 'assistant' | 'user', text: string) => {
      setState((current) => ({
        ...current,
        chatMessages: [
          ...current.chatMessages,
          { id: `${role}-${Date.now()}-${Math.random()}`, role, text },
        ].slice(-24),
      }));
    },
    [],
  );

  const setThemeMode = React.useCallback(
    (theme: ThemeKey, mode: ThemeMode) => {
      setState((current) => ({
        ...current,
        themeModes: { ...current.themeModes, [theme]: mode },
      }));
      notify(
        mode === 'auto'
          ? 'Le copilote préparera ce thème pour vous.'
          : 'Le copilote vous guidera étape par étape.',
      );
    },
    [notify],
  );

  const updateContract = React.useCallback((patch: Partial<ContractInputs>) => {
    const fields = Object.keys(patch).sort().join('|');
    const now = Date.now();
    const previousEdit = lastContractEdit.current;
    const startsNewUndoStep =
      !previousEdit ||
      previousEdit.fields !== fields ||
      now - previousEdit.at > 1500;
    lastContractEdit.current = { fields, at: now };

    setState((current) => {
      const contract = { ...current.contract, ...patch };
      const checks = getRuleChecks(contract);
      const isApprovedRule =
        contract.revenueRule === 'spread' &&
        contract.deliveryMonths === 4 &&
        checks.every((check) => check.passed);
      const wasPrepared = current.rule.status !== 'available';
      const status =
        contract.revenueRule === 'single'
          ? 'available'
          : wasPrepared
            ? isApprovedRule
              ? 'staged'
              : 'needs-review'
            : 'available';
      return {
        ...current,
        contractUndo: startsNewUndoStep
          ? [...current.contractUndo, current.contract].slice(-12)
          : current.contractUndo,
        contract,
        themeDrafts: syncCashDraft(current, contract),
        rule: { ...current.rule, status, checks },
        scenarioStatus: 'draft',
        simulatedMetrics: undefined,
      };
    });
  }, []);

  const undoContract = React.useCallback(() => {
    lastContractEdit.current = null;
    setState((current) => {
      const previous = current.contractUndo.at(-1);
      if (!previous) return current;
      const checks = getRuleChecks(previous);
      const isApprovedRule =
        previous.revenueRule === 'spread' &&
        previous.deliveryMonths === 4 &&
        checks.every((check) => check.passed);
      return {
        ...current,
        contract: previous,
        themeDrafts: syncCashDraft(current, previous),
        contractUndo: current.contractUndo.slice(0, -1),
        rule: {
          ...current.rule,
          status:
            previous.revenueRule === 'single'
              ? 'available'
              : isApprovedRule
                ? 'staged'
                : 'needs-review',
          checks,
        },
        scenarioStatus: 'draft',
        simulatedMetrics: undefined,
      };
    });
    notify('Dernière modification annulée.');
  }, [notify]);

  const discardDraft = React.useCallback(() => {
    lastContractEdit.current = null;
    setState((current) => {
      const activeReference = current.referenceVersions[0];
      const contract = { ...activeReference.contract };
      const checks = getRuleChecks(contract);
      return {
        ...current,
        contract,
        themeDrafts: syncCashDraft(current, contract),
        contractUndo: [],
        scenarioStatus: activeReference.includesAtlas ? 'applied' : 'draft',
        simulatedMetrics: activeReference.includesAtlas
          ? { ...activeReference.metrics }
          : undefined,
        rule: {
          ...current.rule,
          status:
            contract.revenueRule === 'single'
              ? 'available'
              : checks.every((check) => check.passed)
                ? 'staged'
                : 'needs-review',
          checks,
        },
      };
    });
    notify('Le brouillon a été ramené à la version officielle actuelle.');
  }, [notify]);

  const stageRevenueRule = React.useCallback(() => {
    lastContractEdit.current = null;
    setState((current) => {
      if (current.rule.status === 'staged' && current.contract.revenueRule === 'spread' && current.contract.deliveryMonths === 4) return current;
      const contract: ContractInputs = {
        ...current.contract,
        deliveryMonths: 4,
        revenueRule: 'spread',
      };
      const checks = getRuleChecks(contract);
      return {
        ...current,
        phase: 'Construire',
        contractUndo: [...current.contractUndo, current.contract].slice(-12),
        contract,
        rule: {
          ...current.rule,
          status: checks.every((check) => check.passed)
            ? 'staged'
            : 'needs-review',
          checks,
        },
        scenarioStatus: 'draft',
        simulatedMetrics: undefined,
        chatMessages: [
          ...current.chatMessages,
          {
            id: `assistant-rule-${Date.now()}`,
            role: 'assistant' as const,
            text: 'J’ai placé la règle homologuée « vente reconnue sur quatre mois » dans le brouillon. Le modèle central reste inchangé.',
          },
        ].slice(-24),
      };
    });
    notify(state.rule.status === 'staged' ? 'Le brouillon est déjà prêt. Vous pouvez examiner ses impacts.' : 'Règle homologuée ajoutée au brouillon.');
  }, [notify, state.rule.status]);

  const simulate = React.useCallback(
    (patch?: Partial<ContractInputs>) => {
      const failed = getContractChecks({ ...state.contract, ...patch }).find(
        (check) => !check.passed,
      );
      if (failed) {
        notify(`À vérifier : ${failed.label.toLowerCase()}.`);
        return;
      }
      if (!scenarioFixture({...state.contract,...patch})) { notify('Cas non couvert : seuls Atlas 20 % / 60 jours et 40 % / 30 jours, sur quatre mois, possèdent une fixture. Aucun résultat extrapolé.'); return; }
      if (!sourceConfirmed(state,'sales')) { notify('Confirmez la source fictive Atlas dans Personnaliser / Sources avant la simulation.'); return; }
      if (patch) lastContractEdit.current = null;
      setState((current) => {
        const contract = { ...current.contract, ...patch };
        if (getContractChecks(contract).some((check) => !check.passed))
          return current;
        const metrics = calculateScenario(contract);
        const checks = getRuleChecks(contract);
        return {
          ...current,
          contract,
          themeDrafts: syncCashDraft(current, contract),
          contractUndo: patch
            ? [...current.contractUndo, current.contract].slice(-12)
            : current.contractUndo,
          rule: patch
            ? {
                ...current.rule,
                checks,
                status: checks.every((check) => check.passed)
                  ? 'staged'
                  : 'needs-review',
              }
            : current.rule,
          phase: 'Simuler',
          scenarioStatus: 'simulated',
          simulatedMetrics: metrics,
        };
      });
      notify('Simulation mise à jour avec les données de démonstration.');
    },
    [notify, state.contract, state.sources],
  );

  const saveScenario = React.useCallback(() => {
    if (state.scenarioStatus === 'draft' || !state.simulatedMetrics) {
      notify('Lancez la simulation avant de conserver ce scénario.');
      return;
    }
    if (state.scenarioStatus === 'applied') {
      notify('Cette version est déjà la version officielle.');
      return;
    }
    setState((current) => {
      const signature = JSON.stringify(current.contract);
      const alreadySaved = current.savedVariants.some(
        (variant) => JSON.stringify(variant.inputs) === signature,
      );
      const metrics =
        current.simulatedMetrics ?? calculateScenario(current.contract);
      const nextVariant = {
        id: `variant-${Date.now()}`,
        name: `Atlas · ${Math.round(current.contract.amount / 1_000)} k€ · ${current.contract.depositPercent} % · ${current.contract.paymentDays} j`,
        createdAt: 'À l’instant',
        inputs: { ...current.contract },
        metrics,
      };
      return {
        ...current,
        scenarioStatus: 'saved',
        simulatedMetrics: metrics,
        savedVariants: alreadySaved
          ? current.savedVariants
          : [...current.savedVariants, nextVariant],
        decisions: alreadySaved
          ? current.decisions
          : [
              {
                id: `saved-${Date.now()}`,
                title: 'Scénario Atlas conservé',
                createdAt: 'Aujourd’hui',
                summary: `${current.contract.depositPercent} % d’acompte · règlement à ${current.contract.paymentDays} jours`,
                status: 'saved',
              },
              ...current.decisions,
            ],
      };
    });
    notify('Scénario conservé sans modifier la version officielle.');
  }, [notify, state.scenarioStatus, state.simulatedMetrics]);

  const loadSavedVariant = React.useCallback(
    (id: string) => {
      lastContractEdit.current = null;
      setState((current) => {
        const variant = current.savedVariants.find((item) => item.id === id);
        if (!variant) return current;
        const contract = { ...variant.inputs };
        const checks = getRuleChecks(contract);
        return {
          ...current,
          phase: 'Simuler',
          contract,
          themeDrafts: syncCashDraft(current, contract),
          contractUndo: [...current.contractUndo, current.contract].slice(-12),
          scenarioStatus: 'saved',
          simulatedMetrics: { ...variant.metrics },
          rule: {
            ...current.rule,
            status:
              contract.revenueRule === 'spread' &&
              checks.every((check) => check.passed)
                ? 'staged'
                : contract.revenueRule === 'spread'
                  ? 'needs-review'
                  : 'available',
            checks,
          },
        };
      });
      notify('Scénario conservé chargé dans la comparaison.');
    },
    [notify],
  );

  const applyScenario = React.useCallback(() => {
    const activeReference = state.referenceVersions[0];
    const alreadyOfficial =
      state.referenceIncludesAtlas &&
      activeReference &&
      JSON.stringify(activeReference.contract) ===
        JSON.stringify(state.contract);
    if (
      alreadyOfficial ||
      state.scenarioStatus === 'draft' ||
      !state.simulatedMetrics ||
      state.scenarioStatus === 'applied' ||
      !scenarioFixture(state.contract) || !sourceConfirmed(state,'sales') ||
      state.rule.status !== 'staged' ||
      state.rule.checks.some((check) => !check.passed)
    ) {
      notify(
        'La méthode de calcul doit être revalidée avant de modifier la version officielle.',
      );
      return;
    }
    setState((current) => {
      const metrics =
        current.simulatedMetrics ?? calculateScenario(current.contract);
      const versionId = `reference-${Date.now()}`;
      return {
        ...current,
        phase: 'Décider',
        scenarioStatus: 'applied',
        referenceMetrics: metrics,
        referenceVersions: [
          {
            id: versionId,
            label: 'Version officielle Atlas Mobility',
            createdAt: 'Aujourd’hui · à l’instant',
            reason: 'Contrat Atlas appliqué après simulation',
            metrics,
            contract: { ...current.contract },
            includesAtlas: true,
          },
          ...current.referenceVersions,
        ],
        referenceIncludesAtlas: true,
        decisions: [
          {
            id: `applied-${Date.now()}`,
            title: 'Contrat Atlas ajouté à la version officielle',
            createdAt: 'Aujourd’hui',
            summary: `${current.contract.deliveryMonths} mois · ${current.contract.depositPercent} % d’acompte · ${current.contract.paymentDays} jours`,
            status: 'applied',
          },
          ...current.decisions,
        ],
      };
    });
    notify('Nouvelle version officielle créée. L’ancienne reste disponible.');
  }, [
    notify,
    state.rule.checks,
    state.rule.status,
    state.scenarioStatus,
    state.simulatedMetrics,
    state.contract,
    state.referenceIncludesAtlas,
    state.referenceVersions,
    state.sources,
  ]);

  const restoreVersion = React.useCallback(
    (id: string) => {
      lastContractEdit.current = null;
      setState((current) => {
        const source = current.referenceVersions.find(
          (version) => version.id === id,
        );
        if (!source) return current;
        const contract = { ...source.contract };
        const checks = getRuleChecks(contract);
        return {
          ...current,
          phase: 'Décider',
          referenceMetrics: { ...source.metrics },
          referenceIncludesAtlas: source.includesAtlas ?? false,
          contract,
          themeDrafts: syncCashDraft(current, contract),
          contractUndo: [...current.contractUndo, current.contract].slice(-12),
          rule: {
            ...current.rule,
            status:
              contract.revenueRule === 'single'
                ? 'available'
                : checks.every((check) => check.passed)
                  ? 'staged'
                  : 'needs-review',
            checks,
          },
          simulatedMetrics: source.includesAtlas
            ? { ...source.metrics }
            : undefined,
          scenarioStatus: source.includesAtlas ? 'applied' : 'draft',
          referenceVersions: [
            {
              ...source,
              id: `restored-${Date.now()}`,
              label: `Restauration de ${source.label}`,
              createdAt: 'Aujourd’hui · à l’instant',
              reason: 'Ancienne version restaurée sans effacer l’historique',
            },
            ...current.referenceVersions,
          ],
          decisions: [
            {
              id: `restored-decision-${Date.now()}`,
              title: `${source.label} restaurée`,
              createdAt: 'Aujourd’hui',
              summary:
                'Une nouvelle version officielle a été créée depuis ce jalon.',
              status: 'restored',
            },
            ...current.decisions,
          ],
        };
      });
      notify(
        'Ancienne version réutilisée dans une nouvelle version officielle.',
      );
    },
    [notify],
  );

  const setBrand = React.useCallback((brand: Partial<BrandProfile>) => {
    setState((current) => ({
      ...current,
      brand: { ...current.brand, ...brand },
    }));
  }, []);

  const importMonthly = React.useCallback(
    (fileName: string) => {
      setState((current) => ({
        ...current,
        phase: 'Piloter',
        monthly: { ...current.monthly, imported: true, fileName },
      }));
      notify(
        'Données fictives affichées : le contenu du fichier n’a pas été lu.',
      );
    },
    [notify],
  );

  const completeOnboarding = React.useCallback(
    (objective?: string, options?: { preservePhase?: boolean }) => {
      setState((current) => ({
        ...current,
        objective: objective ?? current.objective,
        phase: options?.preservePhase ? current.phase : 'Construire',
        onboardingCompleted: true,
      }));
      notify(
        options?.preservePhase
          ? 'Vos informations ont été mises à jour sans perdre votre progression.'
          : 'Votre cockpit de démonstration est prêt.',
      );
    },
    [notify],
  );

  const resetDemo = React.useCallback(() => {
    lastContractEdit.current = null;
    storageBlocked.current = false;
    window.localStorage.removeItem(STORAGE_KEY);
    setState(createInitialState());
    setImpactOpen(false);
    setCopilotOpen(false);
    notify('La démonstration a été réinitialisée.');
  }, [notify]);

  React.useEffect(() => {
    const context = document.modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();

    const reportError = () => undefined;

    void Promise.resolve(
      context.registerTool(
        {
          name: 'read_cockpit_status',
          title: 'Lire la situation du cockpit',
          description:
            'Retourne la phase, le statut du scénario Atlas et la version officielle visible dans le prototype.',
          inputSchema: {
            type: 'object',
            properties: {},
            additionalProperties: false,
          },
          annotations: { readOnlyHint: true, untrustedContentHint: false },
          execute() {
            return {
              phase: state.phase,
              scenarioStatus: state.scenarioStatus,
              reference: state.referenceVersions[0]?.label,
            };
          },
        },
        { signal: lifecycle.signal },
      ),
    ).catch(reportError);

    void Promise.resolve(
      context.registerTool(
        {
          name: 'stage_atlas_contract_simulation',
          title: 'Préparer le scénario Atlas',
          description:
            'Place dans le brouillon les conditions du contrat Atlas sans modifier la version officielle.',
          inputSchema: {
            type: 'object',
            properties: {
              depositPercent: { type: 'number', minimum: 0, maximum: 100 },
              paymentDays: { type: 'number', enum: [0, 30, 45, 60, 90] },
              deliveryMonths: { type: 'number', minimum: 1, maximum: 12 },
            },
            required: ['depositPercent', 'paymentDays', 'deliveryMonths'],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: false, untrustedContentHint: false },
          execute(input: unknown) {
            if (!input || typeof input !== 'object') {
              throw new Error(
                'Des conditions de contrat valides sont requises.',
              );
            }
            const values = input as Record<string, unknown>;
            const depositPercent = Number(values.depositPercent);
            const paymentDays = Number(values.paymentDays);
            const deliveryMonths = Number(values.deliveryMonths);
            if (
              depositPercent < 0 ||
              depositPercent > 100 ||
              ![0, 30, 45, 60, 90].includes(paymentDays) ||
              deliveryMonths < 1 ||
              deliveryMonths > 12
            ) {
              throw new Error(
                'Les conditions proposées sortent du cadre de la démo.',
              );
            }
            updateContract({ depositPercent, paymentDays, deliveryMonths });
            return {
              status: 'staged',
              referenceChanged: false,
              depositPercent,
              paymentDays,
              deliveryMonths,
            };
          },
        },
        { signal: lifecycle.signal },
      ),
    ).catch(reportError);

    return () => lifecycle.abort();
  }, [
    state.phase,
    state.referenceVersions,
    state.scenarioStatus,
    updateContract,
  ]);

  const value = React.useMemo<DemoContextValue>(
    () => ({
      state,
      command,
      hydrated,
      impactOpen,
      setImpactOpen,
      copilotOpen,
      setCopilotOpen,
      toast,
      notify,
      setThemeMode,
      updateContract,
      undoContract,
      discardDraft,
      stageRevenueRule,
      simulate,
      saveScenario,
      loadSavedVariant,
      applyScenario,
      restoreVersion,
      setBrand,
      addChat,
      importMonthly,
      completeOnboarding,
      resetDemo,
      dismissToast,
    }),
    [
      state,
      command,
      hydrated,
      impactOpen,
      copilotOpen,
      toast,
      notify,
      setThemeMode,
      updateContract,
      undoContract,
      discardDraft,
      stageRevenueRule,
      simulate,
      saveScenario,
      loadSavedVariant,
      applyScenario,
      restoreVersion,
      setBrand,
      addChat,
      importMonthly,
      completeOnboarding,
      resetDemo,
      dismissToast,
    ],
  );

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
}

export function useDemo() {
  const context = React.useContext(DemoContext);
  if (!context) throw new Error('useDemo doit être utilisé dans DemoProvider.');
  return context;
}
