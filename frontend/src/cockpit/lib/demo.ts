import { sharedInitialState, type SharedDemoState } from './catalog';
export const themeKeys = [
  'sales',
  'margin',
  'people',
  'investment',
  'cash',
  'summary',
] as const;

export type ThemeKey = (typeof themeKeys)[number];
export type ThemeMode = 'auto' | 'guided';
export type ScenarioStatus = 'draft' | 'simulated' | 'saved' | 'applied';
export type ImpactKind = 'direct' | 'downstream' | 'unchanged';
export type ControlKind =
  | 'coherent'
  | 'incomplete'
  | 'to-confirm'
  | 'missing-proof'
  | 'open-decision'
  | 'refresh-needed';

export interface ThemeDefinition {
  key: ThemeKey;
  label: string;
  shortLabel: string;
  description: string;
  specialist: string;
  sheets: string[];
}

export interface BrandPalette {
  id: string;
  label: string;
  accent: string;
  deep: string;
  soft: string;
}

export interface BrandProfile {
  companyName: string;
  firstName: string;
  logoDataUrl?: string;
  palette: BrandPalette;
}

export interface ContractInputs {
  id?: string;
  offer?: string;
  pricing?: 'fixed';
  probability?: number;
  vat?: number;
  sourceId?: string;
  invoiceRule?: 'deposit-balance';
  customer: string;
  amount: number;
  deliveryMonths: number;
  depositPercent: number;
  paymentDays: number;
  startMonth: string;
  commercialStatus: 'probable' | 'signed';
  revenueRule: 'single' | 'spread';
}

export interface ScenarioMetrics {
  revenue: number;
  grossMargin: number;
  cashLowPoint: number;
  runway: number;
  cashTension: number;
}

export interface SavedVariant {
  id: string;
  name: string;
  createdAt: string;
  inputs: ContractInputs;
  metrics: ScenarioMetrics;
}

export interface BusinessRuleChange {
  id: string;
  businessLabel: string;
  status: 'available' | 'staged' | 'needs-review';
  approvedTemplate: boolean;
  targetSheets: string[];
  previousRule: string;
  proposedRule: string;
  schematicFormula: string;
  checks: Array<{ label: string; passed: boolean }>;
}

export interface Impact {
  id: string;
  kind: ImpactKind;
  title: string;
  detail: string;
  horizon: string;
  source: string;
  confirmation: string;
  themes: ThemeKey[];
}

export interface ReferenceVersion {
  id: string;
  label: string;
  createdAt: string;
  reason: string;
  metrics: ScenarioMetrics;
  contract: ContractInputs;
  includesAtlas: boolean;
}

export interface DecisionEntry {
  id: string;
  title: string;
  createdAt: string;
  summary: string;
  status: 'applied' | 'saved' | 'restored';
}

export interface ChatMessage {
  id: string;
  role: 'assistant' | 'user';
  text: string;
}

export interface MonthlyState {
  imported: boolean;
  fileName?: string;
  period: string;
}

export interface DemoState extends SharedDemoState {
  schemaVersion: 2;
  brand: BrandProfile;
  objective: string;
  phase:
    | 'Cadrer'
    | 'Sources'
    | 'Construire'
    | 'Simuler'
    | 'Décider'
    | 'Piloter';
  themeModes: Record<ThemeKey, ThemeMode>;
  contract: ContractInputs;
  contractUndo: ContractInputs[];
  scenarioStatus: ScenarioStatus;
  simulatedMetrics?: ScenarioMetrics;
  savedVariants: SavedVariant[];
  rule: BusinessRuleChange;
  referenceMetrics: ScenarioMetrics;
  referenceIncludesAtlas: boolean;
  referenceVersions: ReferenceVersion[];
  decisions: DecisionEntry[];
  chatMessages: ChatMessage[];
  monthly: MonthlyState;
  onboardingCompleted: boolean;
}

export const themes: ThemeDefinition[] = [
  {
    key: 'sales',
    label: 'Ventes et contrats',
    shortLabel: 'Ventes',
    description: 'Offres, contrats, livraisons, factures et encaissements.',
    specialist: 'Activité',
    sheets: ['DATA Contrats', 'Contrats', 'Revenue'],
  },
  {
    key: 'margin',
    label: 'Coûts et marge',
    shortLabel: 'Marge',
    description: 'Coûts directs, achats, stock et charges d’exploitation.',
    specialist: 'Rentabilité',
    sheets: ['DATA COGS', 'COGS', 'Stock', 'Charges_Externes'],
  },
  {
    key: 'people',
    label: 'Équipe',
    shortLabel: 'Équipe',
    description: 'Recrutements, salaires, capacité et contribution R&D.',
    specialist: 'Équipe',
    sheets: ['Effectifs', 'CALCUL_CIR'],
  },
  {
    key: 'investment',
    label: 'Investissements et financement',
    shortLabel: 'Financement',
    description: 'Achats, crédit-bail, dette, equity et subventions.',
    specialist: 'Investissement',
    sheets: [
      'DATA CAPEX',
      'CAPEX',
      'Financement Dette',
      'DATA Financement',
      'Financement E&S',
      'SUBVENTION_INVEST',
    ],
  },
  {
    key: 'cash',
    label: 'Trésorerie et fiscalité',
    shortLabel: 'Trésorerie',
    description: 'Délais de paiement, BFR, TVA, impôts et point bas de cash.',
    specialist: 'Trésorerie',
    sheets: ['BFR', 'ATELIER_CIR_IS', 'Flux de trésorerie'],
  },
  {
    key: 'summary',
    label: 'Synthèse et valeur',
    shortLabel: 'Synthèse',
    description: 'Résultats, scénarios, indicateurs et valeur d’entreprise.',
    specialist: 'Synthèse',
    sheets: ['KPI Dashboard', 'Contrôles', 'Valorisation', 'Sensi Analyses'],
  },
];

export const expertGroups = [
  {
    title: 'Cadre du projet',
    sheets: ['Légende', 'Control', 'Assumptions', 'Previsionnel'],
  },
  {
    title: 'Ventes et contrats',
    sheets: ['DATA Contrats', 'Contrats', 'Revenue'],
  },
  {
    title: 'Coûts, exploitation et équipe',
    sheets: ['DATA COGS', 'COGS', 'Stock', 'Charges_Externes', 'Effectifs'],
  },
  {
    title: 'Investissements et financements',
    sheets: [
      'DATA CAPEX',
      'CAPEX',
      'Financement Dette',
      'DATA Financement',
      'Financement E&S',
      'SUBVENTION_INVEST',
    ],
  },
  {
    title: 'Fiscalité et besoin d’exploitation',
    sheets: ['CALCUL_CIR', 'ATELIER_CIR_IS', 'BFR'],
  },
  {
    title: 'Résultats et trésorerie',
    sheets: [
      'Modèle financier',
      'Compte de Résultat',
      'Bilan',
      'Flux de trésorerie',
      'Plan de financement',
    ],
  },
  {
    title: 'Scénarios et valeur',
    sheets: [
      'Sensi TCA',
      'Sensi Analyses',
      'Sensi Graphiques',
      'Valorisation',
      'Comparables',
    ],
  },
  {
    title: 'Tableau de bord et validations',
    sheets: ['KPI Dashboard', 'Contrôles'],
  },
] as const;

export const defaultPalettes: BrandPalette[] = [
  {
    id: 'indigo',
    label: 'Clarté',
    accent: '#5263eb',
    deep: '#27357f',
    soft: '#e9edff',
  },
  {
    id: 'lagoon',
    label: 'Élan',
    accent: '#188c87',
    deep: '#145f64',
    soft: '#e1f5f2',
  },
  {
    id: 'copper',
    label: 'Caractère',
    accent: '#b96843',
    deep: '#73422f',
    soft: '#f8e9e1',
  },
];

export const baselineMetrics: ScenarioMetrics = {
  revenue: 2_400_000,
  grossMargin: 46,
  cashLowPoint: 118_000,
  runway: 11,
  cashTension: 0,
};

export const initialContract: ContractInputs = {
  id: 'contract-atlas', offer: 'Inspection industrielle', pricing: 'fixed', probability: 75, vat: 20, sourceId: 'source-atlas', invoiceRule: 'deposit-balance',
  customer: 'Atlas Mobility',
  amount: 480_000,
  deliveryMonths: 4,
  depositPercent: 20,
  paymentDays: 60,
  startMonth: 'Octobre 2026',
  commercialStatus: 'probable',
  revenueRule: 'single',
};

export function calculateScenario(inputs: ContractInputs): ScenarioMetrics {
  const fixture = scenarioFixture(inputs);
  if (!fixture) throw new Error('Combinaison non couverte par une fixture de démonstration.');
  return { ...fixture };
}

/** Preserved legacy example outputs, only for their exact documented inputs. No interpolation. */
export function scenarioFixture(inputs: ContractInputs): ScenarioMetrics | undefined {
  if (inputs.amount !== 480000 || inputs.deliveryMonths !== 4 || inputs.startMonth !== 'Octobre 2026' || inputs.commercialStatus !== 'probable' || inputs.revenueRule !== 'spread' || (inputs.probability ?? 75) !== 75 || (inputs.vat ?? 20) !== 20 || (inputs.offer ?? 'Inspection industrielle') !== 'Inspection industrielle') return undefined;
  if (inputs.depositPercent === 20 && inputs.paymentDays === 60) return {revenue:2779200,grossMargin:47,cashLowPoint:42000,runway:16,cashTension:76000};
  if (inputs.depositPercent === 40 && inputs.paymentDays === 30) return {revenue:2779200,grossMargin:47,cashLowPoint:179500,runway:18,cashTension:0};
  return undefined;
}

const fixtureMonths = ['Octobre 2026','Novembre 2026','Décembre 2026','Janvier 2027','Février 2027','Mars 2027','Avril 2027','Mai 2027','Juin 2027','Juillet 2027'];
export function cashFixtureForLowPoint(value:number) {
  const fixtures:Record<string,number[]> = {
    '118000':[288000,303000,278000,233000,173000,118000,148000,213000,268000,288000],
    '42000':[212000,227000,202000,157000,97000,42000,72000,137000,192000,212000],
    '179500':[209500,234500,259500,244500,219500,179500,229500,299500,334500,359500],
  };
  return (fixtures[String(value)] ?? []).map((amount,index)=>({label:fixtureMonths[index],value:amount}));
}

export function getImpacts(inputs: ContractInputs): Impact[] {
  const isSpread = inputs.revenueRule === 'spread';
  const commercialConfirmation =
    inputs.commercialStatus === 'signed'
      ? 'Confirmé par un contrat signé'
      : 'Hypothèse commerciale à confirmer';

  return [
    {
      id: 'recognized-revenue',
      kind: 'direct',
      title: isSpread
        ? 'Le revenu est reconnu progressivement'
        : 'La reconnaissance progressive reste à préparer',
      detail: isSpread
        ? `${inputs.deliveryMonths} livraisons répartissent l’activité sur ${inputs.deliveryMonths} mois au lieu d’une seule date.`
        : `Le cycle prévoit ${inputs.deliveryMonths} mois, mais la version officielle conserve encore une reconnaissance à la livraison finale.`,
      horizon: `${inputs.startMonth} → ${inputs.deliveryMonths} mois`,
      source: 'Conditions du contrat saisies dans le brouillon',
      confirmation: commercialConfirmation,
      themes: ['sales', 'summary'],
    },
    {
      id: 'cash-delay',
      kind: 'downstream',
      title: 'L’argent arrive après les dépenses de production',
      detail: `Avec ${inputs.depositPercent} % d’acompte et un règlement à ${inputs.paymentDays} jours, un creux temporaire apparaît avant l’encaissement du solde.`,
      horizon: 'Court terme',
      source: 'Simulation locale sur données fictives',
      confirmation: 'Calcul à actualiser après chaque changement',
      themes: ['margin', 'cash'],
    },
    {
      id: 'tax',
      kind: 'downstream',
      title: 'Facturation, TVA et besoin d’exploitation se décalent',
      detail:
        'Le chiffre d’affaires, la facture et l’encaissement suivent des calendriers distincts.',
      horizon: 'Pendant le cycle du contrat',
      source: 'Règle de gestion homologuée de la démonstration',
      confirmation: isSpread
        ? 'Calcul cohérent'
        : 'Règle à confirmer dans le brouillon',
      themes: ['sales', 'cash'],
    },
    {
      id: 'signed-value',
      kind: 'unchanged',
      title: 'La valeur négociée du contrat ne change pas',
      detail: `La nouvelle règle modifie le rythme de reconnaissance, pas le montant de ${formatEuro(inputs.amount, true)}.`,
      horizon: 'Permanent',
      source: `Montant négocié saisi : ${formatEuro(inputs.amount, true)}`,
      confirmation: commercialConfirmation,
      themes: ['sales'],
    },
  ];
}

export function getContractChecks(inputs: ContractInputs) {
  return [
    { label: 'Client renseigné', passed: Boolean(inputs.customer.trim()) },
    {
      label: 'Montant valide (10 000 € minimum)',
      passed: Number.isFinite(inputs.amount) && inputs.amount >= 10_000,
    },
    {
      label: 'Cycle compris entre 1 et 12 mois entiers',
      passed:
        Number.isInteger(inputs.deliveryMonths) &&
        inputs.deliveryMonths >= 1 &&
        inputs.deliveryMonths <= 12,
    },
    {
      label: 'Acompte compris entre 0 et 100 %',
      passed:
        Number.isFinite(inputs.depositPercent) &&
        inputs.depositPercent >= 0 &&
        inputs.depositPercent <= 100,
    },
    {
      label: 'Délai compris entre 0 et 90 jours',
      passed:
        Number.isInteger(inputs.paymentDays) &&
        inputs.paymentDays >= 0 &&
        inputs.paymentDays <= 90,
    },
    {
      label: 'Mois de départ proposé dans la démonstration',
      passed: ['Octobre 2026', 'Novembre 2026', 'Janvier 2027'].includes(
        inputs.startMonth,
      ),
    },
  ];
}

export function getRuleChecks(inputs: ContractInputs) {
  const inputChecks = getContractChecks(inputs);
  const inputErrors = inputChecks.filter((check) => !check.passed);
  const fourMonthSpread =
    inputs.revenueRule === 'spread' && inputs.deliveryMonths === 4;
  return [
    {
      label: inputErrors.length
        ? inputErrors.map((check) => check.label).join(' · ')
        : 'Conditions du contrat complètes et valides',
      passed: inputErrors.length === 0,
    },
    { label: 'Répartition totale égale à 100 %', passed: fourMonthSpread },
    {
      label: 'Dates comprises dans le cycle de quatre mois',
      passed: inputs.deliveryMonths === 4,
    },
    {
      label: 'Engagement signé non altéré',
      passed: inputs.commercialStatus !== 'signed' || inputs.amount === 480_000,
    },
    { label: 'Moteur financier central inchangé', passed: true },
  ];
}

export function createInitialState(): DemoState {
  return {
    ...sharedInitialState(),
    schemaVersion: 2,
    brand: {
      companyName: 'Luméo Systems',
      firstName: 'Claire',
      palette: defaultPalettes[0],
    },
    objective: 'Sécuriser la trésorerie',
    phase: 'Construire',
    themeModes: {
      sales: 'auto',
      margin: 'guided',
      people: 'guided',
      investment: 'auto',
      cash: 'auto',
      summary: 'guided',
    },
    contract: { ...initialContract },
    contractUndo: [],
    scenarioStatus: 'draft',
    savedVariants: [],
    rule: {
      id: 'revenue-spread',
      businessLabel: 'Reconnaître la vente progressivement sur quatre mois',
      status: 'available',
      approvedTemplate: true,
      targetSheets: ['Contrats', 'Revenue'],
      previousRule: '100 % du revenu reconnu à la livraison finale',
      proposedRule: '25 % du revenu reconnu à chaque livraison mensuelle',
      schematicFormula:
        'SI(mois compris dans le cycle ; valeur du contrat ÷ 4 ; 0)',
      checks: getRuleChecks(initialContract),
    },
    referenceMetrics: { ...baselineMetrics },
    referenceIncludesAtlas: false,
    referenceVersions: [
      {
        id: 'reference-2026-09-12',
        label: 'Version officielle du 12 septembre',
        createdAt: '12 sept. 2026 · 17:42',
        reason: 'Embauche décalée à janvier',
        metrics: { ...baselineMetrics },
        contract: { ...initialContract },
        includesAtlas: false,
      },
      {
        id: 'reference-2026-09-05',
        label: 'Version officielle du 5 septembre',
        createdAt: '5 sept. 2026 · 10:16',
        reason: 'Mise à jour des délais fournisseurs',
        metrics: { ...baselineMetrics, cashLowPoint: 96_000, runway: 10 },
        contract: { ...initialContract },
        includesAtlas: false,
      },
    ],
    decisions: [
      {
        id: 'decision-hiring',
        title: 'Embauche décalée à janvier',
        createdAt: '10 sept. 2026',
        summary: 'Préserver 64 k€ de trésorerie avant la signature du contrat.',
        status: 'applied',
      },
      {
        id: 'decision-stock',
        title: 'Stock de sécurité maintenu à six semaines',
        createdAt: '3 sept. 2026',
        summary: 'Choix conservé malgré un impact temporaire sur le cash.',
        status: 'applied',
      },
    ],
    chatMessages: [
      {
        id: 'welcome',
        role: 'assistant',
        text: 'Bonjour Claire. Je peux préparer le contrat Atlas pour vous, ou vous guider étape par étape.',
      },
    ],
    monthly: {
      imported: false,
      period: 'Août 2026',
    },
    onboardingCompleted: true,
  };
}

/** Keep the v1 object and its history; new commands never trust its old illustrative results. */
export function migrateDemoState(raw: string): DemoState | null {
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || ![1,2].includes(parsed.schemaVersion)) return null;
    const seed = createInitialState();
    const contract = {...seed.contract,...parsed.contract};
    return {...seed,...parsed,schemaVersion:2,caseId:parsed.caseId || seed.caseId,
      brand:{...seed.brand,...parsed.brand,palette:{...seed.brand.palette,...parsed.brand?.palette}},
      themeModes:{...seed.themeModes,...parsed.themeModes},contract,
      rule:{...seed.rule,...parsed.rule,checks:getRuleChecks(contract)},
      monthly:{...seed.monthly,...parsed.monthly},
      themeDrafts:{...seed.themeDrafts,...parsed.themeDrafts},
      referenceVersions:(parsed.referenceVersions ?? seed.referenceVersions).map((v:ReferenceVersion)=>({...v,includesAtlas:v.includesAtlas ?? false})),
    };
  } catch { return null; }
}

export function formatEuro(value: number, compact = false): string {
  if (compact && Math.abs(value) >= 1_000_000) {
    const amount = (value / 1_000_000)
      .toLocaleString('fr-FR', { maximumFractionDigits: 2 })
      .replace(/−/g, '-');
    return `${amount} M€`;
  }
  if (compact && Math.abs(value) >= 1_000) {
    const amount = Math.round(value / 1_000).toLocaleString('fr-FR');
    return `${amount} k€`;
  }
  const amount = Math.round(value).toLocaleString('fr-FR');
  return `${amount} €`;
}
