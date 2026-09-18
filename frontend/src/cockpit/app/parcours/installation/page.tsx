'use client';

import * as React from 'react';
import { SourcesPanel } from '../../demo-parts';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  Check,
  FileCheck2,
  FileText,
  ImagePlus,
  Palette,
  Sparkles,
  Target,
  Upload,
} from '@/components/ui/site-icon';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import { useDemo } from '@/components/cockpit/demo-provider';
import { StateBadge, Surface } from '@/components/cockpit/page-elements';
import { defaultPalettes, type BrandPalette } from '@/lib/demo';

const steps = [
  { label: 'Entreprise', icon: Building2 },
  { label: 'Identité', icon: Palette },
  { label: 'Objectif', icon: Target },
  { label: 'Sources', icon: FileText },
  { label: 'Confirmation', icon: FileCheck2 },
];

function mixHex(source: string, target: string, ratio: number) {
  const parse = (hex: string) =>
    [1, 3, 5].map((index) => parseInt(hex.slice(index, index + 2), 16));
  const from = parse(source);
  const to = parse(target);
  return `#${from
    .map((channel, index) =>
      Math.round(channel * (1 - ratio) + to[index] * ratio)
        .toString(16)
        .padStart(2, '0'),
    )
    .join('')}`;
}

function contrastAgainstWhite(color: string) {
  const channels = [1, 3, 5].map((index) => {
    const value = parseInt(color.slice(index, index + 2), 16) / 255;
    return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  const luminance =
    channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
  return 1.05 / (luminance + 0.05);
}

function ensureWhiteTextContrast(color: string) {
  if (contrastAgainstWhite(color) >= 4.5) return color;
  for (let ratio = 0.08; ratio <= 1; ratio += 0.08) {
    const candidate = mixHex(color, '#17203a', ratio);
    if (contrastAgainstWhite(candidate) >= 4.5) return candidate;
  }
  return '#17203a';
}

function palettesFromColor(color: string): BrandPalette[] {
  return [
    {
      id: `logo-original-${color}`,
      label: 'Fidèle au logo',
      accent: color,
      deep: ensureWhiteTextContrast(mixHex(color, '#17203a', 0.52)),
      soft: mixHex(color, '#ffffff', 0.86),
    },
    {
      id: `logo-calm-${color}`,
      label: 'Plus calme',
      accent: mixHex(color, '#5263eb', 0.32),
      deep: ensureWhiteTextContrast(mixHex(color, '#202f78', 0.58)),
      soft: mixHex(color, '#f5f7ff', 0.88),
    },
    {
      id: `logo-fresh-${color}`,
      label: 'Plus fraîche',
      accent: mixHex(color, '#168c87', 0.34),
      deep: ensureWhiteTextContrast(mixHex(color, '#145f64', 0.58)),
      soft: mixHex(color, '#effaf7', 0.88),
    },
  ];
}

async function prepareLogo(file: File) {
  if (!file.type.startsWith('image/')) throw new Error('Choisissez une image.');
  if (file.size > 4 * 1024 * 1024)
    throw new Error('Le logo doit peser moins de 4 Mo.');

  const raw = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') resolve(reader.result);
      else reject(new Error('Le format du logo n’est pas reconnu.'));
    };
    reader.onerror = () => reject(new Error('Le logo ne peut pas être lu.'));
    reader.readAsDataURL(file);
  });
  const image = await new Promise<HTMLImageElement>((resolve, reject) => {
    const element = new Image();
    element.onload = () => resolve(element);
    element.onerror = () =>
      reject(new Error('Le format du logo n’est pas reconnu.'));
    element.src = raw;
  });

  const side = 192;
  const canvas = document.createElement('canvas');
  canvas.width = side;
  canvas.height = side;
  const context = canvas.getContext('2d', { willReadFrequently: true });
  if (!context)
    throw new Error('La prévisualisation du logo est indisponible.');
  context.clearRect(0, 0, side, side);
  const scale = Math.min(side / image.width, side / image.height) * 0.88;
  const width = image.width * scale;
  const height = image.height * scale;
  context.drawImage(
    image,
    (side - width) / 2,
    (side - height) / 2,
    width,
    height,
  );

  const pixels = context.getImageData(0, 0, side, side).data;
  let red = 0;
  let green = 0;
  let blue = 0;
  let count = 0;
  for (let index = 0; index < pixels.length; index += 16) {
    const alpha = pixels[index + 3];
    const brightness =
      (pixels[index] + pixels[index + 1] + pixels[index + 2]) / 3;
    if (alpha > 120 && brightness < 238) {
      red += pixels[index];
      green += pixels[index + 1];
      blue += pixels[index + 2];
      count += 1;
    }
  }
  const color =
    count > 5
      ? `#${[red / count, green / count, blue / count]
          .map((channel) => Math.round(channel).toString(16).padStart(2, '0'))
          .join('')}`
      : '#5263eb';
  return { dataUrl: canvas.toDataURL('image/png', 0.86), color };
}

export default function InstallationPage() {
  const { hydrated } = useDemo();

  if (!hydrated) {
    return (
      <div className="spatial-page mx-auto max-w-5xl" aria-busy="true">
        <Surface
          variant="floating"
          depth={2}
          className="min-h-[520px] animate-pulse rounded-[36px]"
        >
          <span className="sr-only">Chargement de vos informations</span>
        </Surface>
      </div>
    );
  }

  return <InstallationContent />;
}

function InstallationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { state, setBrand, completeOnboarding, command } = useDemo();
  const reviewMode = searchParams.get('mode') === 'review';
  const requestedStep = Number.parseInt(searchParams.get('step') ?? '0', 10);
  const initialStep = Number.isFinite(requestedStep)
    ? Math.min(steps.length - 1, Math.max(0, requestedStep))
    : 0;
  const step = initialStep;
  const [identityError, setIdentityError] = React.useState(false);
  const [exitTo, setExitTo] = React.useState<string>();
  const [logoBusy, setLogoBusy] = React.useState(false);
  const saving = React.useRef(false);
  const stepRef = React.useRef<HTMLDivElement>(null);
  const setStep = (next: number) => {
    if (next > 0 && (!companyName.trim() || !firstName.trim())) {
      setIdentityError(true);
      return;
    }
    const params = new URLSearchParams(searchParams.toString());
    params.set('step', String(next));
    router.push(`/parcours/installation?${params.toString()}`, {
      scroll: false,
    });
  };
  const [companyName, setCompanyName] = React.useState(state.brand.companyName);
  const [firstName, setFirstName] = React.useState(state.brand.firstName);
  const [logoDataUrl, setLogoDataUrl] = React.useState(state.brand.logoDataUrl);
  const [palettes, setPalettes] = React.useState<BrandPalette[]>(
    state.brand.logoDataUrl
      ? [state.brand.palette, ...defaultPalettes.slice(1)]
      : defaultPalettes,
  );
  const [selectedPalette, setSelectedPalette] = React.useState(
    state.brand.palette,
  );
  const [objective, setObjective] = React.useState(state.objective);
  const [documents, setDocuments] = React.useState<string[]>([]);
  const [logoError, setLogoError] = React.useState<string>();
  const logoInputRef = React.useRef<HTMLInputElement>(null);
  const documentInputRef = React.useRef<HTMLInputElement>(null);

  const onLogo = async (file?: File) => {
    if (!file) return;
    setLogoError(undefined);
    setLogoBusy(true);
    try {
      const prepared = await prepareLogo(file);
      const suggestions = palettesFromColor(prepared.color);
      setLogoDataUrl(prepared.dataUrl);
      setPalettes(suggestions);
      setSelectedPalette(suggestions[0]);
    } catch (error) {
      setLogoError(
        error instanceof Error
          ? error.message
          : 'Impossible de préparer ce logo.',
      );
    } finally {
      setLogoBusy(false);
      if (logoInputRef.current) logoInputRef.current.value = '';
    }
  };

  const finish = (destination?: string) => {
    if (!companyName.trim() || !firstName.trim()) {
      setIdentityError(true);
      return;
    }
    saving.current = true;
    setBrand({
      companyName: companyName.trim(),
      firstName: firstName.trim(),
      logoDataUrl,
      palette: selectedPalette,
    });
    for (const fileName of documents) command({type:'source-add',source:{id:'metadata-'+crypto.randomUUID(),caseId:state.caseId,title:fileName,fileName,kind:'metadata',facts:[]}});
    setDocuments([]);
    completeOnboarding(objective, { preservePhase: reviewMode });
    router.push(destination ?? (reviewMode ? '/parcours' : '/'));
  };

  const previewBrandStyle = {
    '--brand': selectedPalette.deep,
    '--brand-accent': selectedPalette.accent,
    '--brand-deep': selectedPalette.deep,
    '--brand-soft': selectedPalette.soft,
    '--primary': selectedPalette.deep,
    '--ring': selectedPalette.deep,
  } as React.CSSProperties;
  const hasUnsavedChanges =
    companyName !== state.brand.companyName ||
    firstName !== state.brand.firstName ||
    logoDataUrl !== state.brand.logoDataUrl ||
    selectedPalette.id !== state.brand.palette.id ||
    objective !== state.objective ||
    documents.length > 0;
  const isFinalStep = step === steps.length - 1;
  const requestExit = (href: string) =>
    hasUnsavedChanges ? setExitTo(href) : router.push(href);

  React.useEffect(() => {
    const onLeave = (event: BeforeUnloadEvent) => {
      if (hasUnsavedChanges && !saving.current) event.preventDefault();
    };
    const onNavigation = (event: Event) => {
      if (!hasUnsavedChanges || saving.current) return;
      const url = new URL((event as CustomEvent<{href:string}>).detail.href, location.href);
      if (url.pathname.endsWith('/parcours/installation')) return;
      event.preventDefault();
      const path = url.pathname.startsWith('/demo') ? url.pathname.slice(5) || '/' : url.pathname;
      setExitTo(path + url.search);
    };
    window.addEventListener('beforeunload', onLeave);
    window.addEventListener('cockpit:before-navigation', onNavigation);
    return () => {
      window.removeEventListener('beforeunload', onLeave);
      window.removeEventListener('cockpit:before-navigation', onNavigation);
    };
  }, [hasUnsavedChanges]);

  const previousStep = React.useRef(step);
  React.useEffect(() => {
    if (previousStep.current === step) return;
    previousStep.current = step;
    stepRef.current?.focus({ preventScroll: true });
    stepRef.current?.scrollIntoView({ block: 'start', behavior: 'auto' });
  }, [step]);

  return (
    <div className="spatial-page mx-auto max-w-5xl" style={previewBrandStyle}>
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Button
          variant="ghost"
          className="h-11 self-start rounded-full px-3 text-slate-500"
          onClick={() => requestExit(reviewMode ? '/parcours' : '/')}
        >
          <ArrowLeft data-icon="inline-start" />
          {hasUnsavedChanges
            ? 'Abandonner les modifications'
            : reviewMode
              ? 'Retour au parcours'
              : 'Quitter l’installation'}
        </Button>
        {reviewMode ? (
          <Button
            className="h-12 w-full rounded-full bg-[var(--brand-deep)] px-5 font-semibold text-white shadow-[0_12px_28px_color-mix(in_srgb,var(--brand)_22%,transparent)] hover:bg-[var(--brand-deep)] hover:brightness-95 sm:w-auto"
            onClick={() => finish()}
            disabled={logoBusy}
          >
            <Check aria-hidden="true" className="size-4" />
            Enregistrer mes changements
          </Button>
        ) : null}
      </div>

      <header className="text-center">
        <StateBadge>
          {reviewMode ? 'Étape à revoir' : 'Installation rejouable'}
        </StateBadge>
        <h1 className="mx-auto mt-4 max-w-3xl text-[clamp(1.8rem,3vw,2.65rem)] font-semibold leading-[1.12] tracking-[-0.035em] text-slate-900">
          Votre entreprise, votre cockpit.
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-base leading-7 text-slate-500">
          Tout ce parcours reste sur cet ordinateur. Les documents financiers
          déposés ici ne sont jamais lus dans la démonstration.
        </p>
      </header>

      <ol
        className="liquid-segmented mx-auto mt-8 grid max-w-4xl grid-cols-5 gap-2 rounded-[28px] p-2"
        aria-label="Étapes de l’installation"
      >
        {steps.map(({ label, icon: Icon }, index) => (
          <li
            key={label}
            className="text-center"
            aria-current={step === index ? 'step' : undefined}
          >
            <button
              type="button"
              onClick={() => setStep(index)}
              disabled={!reviewMode && index > step}
              aria-label={`Étape ${index + 1} : ${label}`}
              className={`flex min-h-[72px] w-full flex-col items-center justify-center gap-1.5 rounded-[20px] px-1 text-[12px] font-semibold text-slate-500 ${
                step === index
                  ? 'bg-white/84 shadow-[0_10px_24px_rgba(54,63,104,.1)]'
                  : ''
              }`}
            >
              <span
                className={`grid size-9 place-items-center rounded-full ${
                  index < step
                    ? 'bg-[#def5ed] text-[#08795e]'
                    : step === index
                      ? 'bg-[var(--brand-deep)] text-white'
                      : 'bg-white text-slate-400'
                }`}
              >
                {index < step ? (
                  <Check className="size-4" />
                ) : (
                  <Icon className="size-4" />
                )}
              </span>
              <span className="hidden sm:block">{label}</span>
            </button>
          </li>
        ))}
      </ol>

      <p className="mt-4 text-center text-sm text-slate-600" aria-live="polite">
        Étape {step + 1} sur {steps.length} : {steps[step].label}
        {hasUnsavedChanges ? ' · Changements à enregistrer' : ''}
      </p>
      {identityError ? (
        <p role="alert" className="mt-3 text-center text-[#9a3b39]">
          Renseignez le nom de l’entreprise et votre prénom à l’étape
          Entreprise.
        </p>
      ) : null}

      <div
        ref={stepRef}
        tabIndex={-1}
        aria-label={steps[step].label}
        className="onboarding-stack mx-auto mt-7 max-w-4xl scroll-mt-28 outline-none"
      >
        <div
          className="onboarding-stack__back onboarding-stack__back--mint"
          aria-hidden="true"
        />
        <div
          className="onboarding-stack__back onboarding-stack__back--lilac"
          aria-hidden="true"
        />
        <Surface
          variant="solid"
          depth={3}
          className="relative z-[3] min-h-[460px] rounded-[36px] p-6 sm:p-8"
        >
          {step === 0 ? (
            <div className="mx-auto max-w-2xl">
              <StepTitle
                icon={Building2}
                title="Commençons par vous"
                description="Ces informations servent uniquement à personnaliser les textes et l’accueil."
              />
              <div className="mt-7 grid gap-5 sm:grid-cols-2">
                <label htmlFor="company-name">
                  <span className="text-sm font-semibold text-slate-700">
                    Nom de l’entreprise
                  </span>
                  <Input
                    id="company-name"
                    required
                    autoComplete="organization"
                    aria-invalid={identityError && !companyName.trim()}
                    value={companyName}
                    onChange={(event) => setCompanyName(event.target.value)}
                    className="mt-2 h-12 rounded-2xl bg-white px-4 text-base"
                  />
                </label>
                <label htmlFor="first-name">
                  <span className="text-sm font-semibold text-slate-700">
                    Votre prénom
                  </span>
                  <Input
                    id="first-name"
                    required
                    autoComplete="given-name"
                    aria-invalid={identityError && !firstName.trim()}
                    value={firstName}
                    onChange={(event) => setFirstName(event.target.value)}
                    className="mt-2 h-12 rounded-2xl bg-white px-4 text-base"
                  />
                </label>
              </div>
              <div className="mt-6 rounded-[20px] bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-800">Aperçu</p>
                <p className="mt-2 text-lg text-slate-600">
                  Bonjour <strong>{firstName || 'vous'}</strong>, voici ce qui
                  mérite votre attention chez{' '}
                  <strong>{companyName || 'votre entreprise'}</strong>.
                </p>
              </div>
            </div>
          ) : null}

          {step === 1 ? (
            <div className="mx-auto max-w-2xl">
              <StepTitle
                icon={Palette}
                title="Votre identité visuelle"
                description="Chargez un logo : le navigateur crée un aperçu léger et trois ambiances cohérentes."
              />
              <input
                ref={logoInputRef}
                type="file"
                accept="image/png,image/jpeg,image/svg+xml"
                aria-hidden="true"
                tabIndex={-1}
                className="hidden"
                onChange={(event) => void onLogo(event.target.files?.[0])}
              />
              <div className="mt-7 flex flex-col items-center gap-5 rounded-[24px] border border-dashed border-[var(--brand)]/30 bg-slate-50/70 p-6 sm:flex-row">
                <div className="grid size-24 shrink-0 place-items-center overflow-hidden rounded-[24px] border border-white bg-white text-slate-400 shadow-sm">
                  {logoDataUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={logoDataUrl}
                      alt="Aperçu du logo"
                      className="size-full object-contain p-2"
                    />
                  ) : (
                    <ImagePlus className="size-7" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">
                    {logoDataUrl
                      ? 'Logo prêt dans ce navigateur'
                      : 'Ajouter votre logo'}
                  </h3>
                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    PNG, JPG ou SVG · 4 Mo maximum. L’image est réduite
                    localement avant d’être mémorisée.
                  </p>
                  <Button
                    type="button"
                    variant="outline"
                    className="mt-3 h-11 rounded-full bg-white"
                    onClick={() => logoInputRef.current?.click()}
                    disabled={logoBusy}
                  >
                    <Upload data-icon="inline-start" />{' '}
                    {logoBusy ? 'Préparation du logo…' : 'Choisir une image'}
                  </Button>
                  {logoDataUrl ? (
                    <Button
                      variant="ghost"
                      className="mt-2 rounded-full"
                      onClick={() => setLogoDataUrl(undefined)}
                    >
                      Retirer le logo
                    </Button>
                  ) : null}
                  {logoError ? (
                    <p role="alert" className="mt-2 text-sm text-[#ad334a]">
                      {logoError}
                    </p>
                  ) : null}
                </div>
              </div>
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {palettes.map((palette) => (
                  <button
                    type="button"
                    key={palette.id}
                    aria-pressed={selectedPalette.id === palette.id}
                    onClick={() => setSelectedPalette(palette)}
                    className={`min-h-[116px] rounded-[20px] border p-4 text-left transition ${
                      selectedPalette.id === palette.id
                        ? 'border-[var(--brand)] bg-white shadow-md'
                        : 'border-slate-200 bg-white/55 hover:bg-white'
                    }`}
                  >
                    <span className="flex gap-1.5">
                      {[palette.deep, palette.accent, palette.soft].map(
                        (color) => (
                          <span
                            key={color}
                            className="h-9 flex-1 rounded-xl"
                            style={{ backgroundColor: color }}
                          />
                        ),
                      )}
                    </span>
                    <span className="mt-3 flex items-center justify-between text-sm font-semibold text-slate-700">
                      {palette.label}
                      {selectedPalette.id === palette.id ? (
                        <Check className="size-4 text-[var(--brand-deep)]" />
                      ) : null}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {step === 2 ? (
            <div className="mx-auto max-w-2xl">
              <StepTitle
                icon={Target}
                title="Quelle décision doit devenir plus simple ?"
                description="Ce choix détermine ce que l’accueil mettra au premier plan."
              />
              <div className="mt-7 grid gap-3">
                {[
                  [
                    'Sécuriser la trésorerie',
                    'Voir les mois sensibles avant qu’ils arrivent.',
                  ],
                  [
                    'Préparer la croissance',
                    'Tester contrats, recrutements et capacité.',
                  ],
                  [
                    'Convaincre des financeurs',
                    'Raconter une trajectoire cohérente et justifiée.',
                  ],
                ].map(([title, detail]) => (
                  <button
                    type="button"
                    key={title}
                    aria-pressed={objective === title}
                    onClick={() => setObjective(title)}
                    className={`flex min-h-[82px] items-center gap-4 rounded-[20px] border p-4 text-left transition ${
                      objective === title
                        ? 'border-[var(--brand)] bg-[var(--brand-soft)]'
                        : 'border-slate-200 bg-white/70 hover:bg-white'
                    }`}
                  >
                    <span
                      className={`grid size-10 shrink-0 place-items-center rounded-full ${objective === title ? 'bg-[var(--brand)] text-white' : 'bg-slate-100 text-slate-400'}`}
                    >
                      {objective === title ? (
                        <Check className="size-4" />
                      ) : (
                        <Target className="size-4" />
                      )}
                    </span>
                    <span>
                      <span className="block font-semibold text-slate-900">
                        {title}
                      </span>
                      <span className="mt-1 block text-sm text-slate-500">
                        {detail}
                      </span>
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {step === 3 ? (
            <div className="mx-auto max-w-2xl">
              <StepTitle
                icon={FileText}
                title="Réunir les premières sources"
                description="Dans le produit final, elles alimenteront les faits à confirmer. Ici, aucun contenu financier n’est lu. Vous pouvez simplement utiliser nos exemples."
              />
              <Button
                variant="outline"
                className="mt-5 w-full rounded-full"
                onClick={() =>
                  setDocuments([
                    'Contrat Atlas (exemple fictif)',
                    'Situation de départ (exemple fictif)',
                  ])
                }
              >
                Utiliser les exemples fictifs
              </Button>
              <input
                ref={documentInputRef}
                type="file"
                accept=".pdf,.xlsx,.xlsm,.csv,.docx,.txt,.png,.jpg,.jpeg"
                multiple
                aria-hidden="true"
                tabIndex={-1}
                className="hidden"
                onChange={(event) =>
                  setDocuments(
                    Array.from(event.target.files ?? []).map(
                      (file) => file.name,
                    ),
                  )
                }
              />
              <button
                type="button"
                aria-label="Choisir des documents de démonstration"
                onClick={() => documentInputRef.current?.click()}
                className="mt-7 flex min-h-[230px] w-full flex-col items-center justify-center rounded-[26px] border-2 border-dashed border-[var(--brand)]/25 bg-slate-50/70 p-6 text-center transition hover:border-[var(--brand)]"
              >
                <span className="grid size-14 place-items-center rounded-[20px] bg-[var(--brand-soft)] text-[var(--brand-deep)]">
                  <Upload className="size-6" />
                </span>
                <h3 className="mt-4 font-semibold text-slate-900">
                  Choisir des documents de démonstration
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  PDF, XLSX/XLSM, CSV, Word, texte ou image · aucun contenu analysé. Convertissez les anciens XLS.
                </p>
              </button>
              <SourcesPanel/>
              {documents.length ? (
                <div className="mt-4 space-y-2">
                  {documents.map((document) => (
                    <div
                      key={document}
                      className="flex min-h-12 items-center gap-3 rounded-[16px] bg-white px-4 text-sm text-slate-600"
                    >
                      <FileCheck2 className="size-4 text-[#08795e]" />{' '}
                      {document}
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}

          {step === 4 ? (
            <div className="mx-auto max-w-2xl">
              <StepTitle
                icon={FileCheck2}
                title="Confirmer ce qui alimentera le modèle"
                description="Ces faits sont fictifs. Ils illustrent la validation qui précédera toujours une simulation."
              />
              <div className="mt-7 space-y-3">
                {[
                  [
                    'Activité',
                    'Équipements d’inspection industrielle et maintenance B2B',
                  ],
                  ['Objectif prioritaire', objective],
                  [
                    'Trésorerie disponible',
                    '320 k€ au démarrage de la démonstration',
                  ],
                  [
                    'Contrat à étudier',
                    'Atlas Mobility · 480 k€ · statut probable',
                  ],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="flex flex-col gap-2 rounded-[18px] bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <span className="text-sm font-semibold text-slate-500">
                      {label}
                    </span>
                    <span className="max-w-md text-sm font-semibold text-slate-800 sm:text-right">
                      {value}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-5 flex items-start gap-3 rounded-[20px] bg-[#effaf6] p-4">
                <Sparkles className="mt-0.5 size-5 shrink-0 text-[#08795e]" />
                <div>
                  <p className="font-semibold text-[#086b54]">
                    Le cockpit est prêt
                  </p>
                  <p className="mt-1 text-sm leading-6 text-[#4b776c]">
                    Vous retrouverez votre logo, votre palette et votre
                    progression après actualisation ou fermeture du navigateur.
                  </p>
                </div>
              </div>
            </div>
          ) : null}
        </Surface>
      </div>

      <footer
        className={`onboarding-step-navigation relative z-10 mb-6 mt-7 flex w-full gap-3 ${
          isFinalStep && !reviewMode
            ? 'flex-col-reverse items-stretch sm:flex-row sm:items-center sm:justify-between'
            : `items-center ${
                step === 0
                  ? 'justify-end'
                  : reviewMode && isFinalStep
                    ? 'justify-start'
                    : 'justify-between'
              }`
        }`}
        aria-label="Navigation entre les étapes"
      >
        {step > 0 ? (
          <Button
            variant="ghost"
            className="onboarding-step-control liquid-control top-glass-control min-h-14 rounded-full pl-2 pr-4 text-[var(--brand-deep)] hover:text-[var(--brand-deep)]"
            onClick={() => setStep(Math.max(0, step - 1))}
          >
            <span className="onboarding-step-control__icon onboarding-step-control__icon--primary">
              <ArrowLeft aria-hidden="true" className="size-4" />
            </span>
            <span className="onboarding-step-label onboarding-step-label--wide">
              Étape précédente
            </span>
            <span className="onboarding-step-label onboarding-step-label--compact">
              Précédent
            </span>
          </Button>
        ) : null}
        {!isFinalStep ? (
          <Button
            variant="ghost"
            className="onboarding-step-control liquid-control top-glass-control min-h-14 rounded-full pl-5 pr-2 text-[var(--brand-deep)] hover:text-[var(--brand-deep)]"
            onClick={() => setStep(Math.min(steps.length - 1, step + 1))}
            disabled={logoBusy}
          >
            <span className="onboarding-step-label">Continuer</span>
            <span className="onboarding-step-control__icon onboarding-step-control__icon--primary">
              <ArrowRight aria-hidden="true" className="size-4" />
            </span>
          </Button>
        ) : !reviewMode ? (
          <Button
            variant="ghost"
            className="onboarding-step-control liquid-control top-glass-control min-h-14 rounded-full pl-5 pr-2 text-[var(--brand-deep)] hover:text-[var(--brand-deep)]"
            onClick={() => finish()}
          >
            <span className="onboarding-step-label">Ouvrir mon cockpit</span>
            <span className="onboarding-step-control__icon onboarding-step-control__icon--primary">
              <ArrowRight aria-hidden="true" className="size-4" />
            </span>
          </Button>
        ) : null}
      </footer>
      <Dialog
        open={Boolean(exitTo)}
        onOpenChange={(open) => {
          if (!open) setExitTo(undefined);
        }}
      >
        <DialogContent showCloseButton={false} className="rounded-[28px] p-6">
          <DialogHeader>
            <DialogTitle>Garder vos changements avant de partir ?</DialogTitle>
            <DialogDescription>
              Votre logo, vos informations et votre objectif n’ont pas encore
              été enregistrés. Votre progression financière reste inchangée.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-wrap gap-3">
            <DialogClose
              render={<Button variant="outline" className="rounded-full" />}
            >
              Rester ici
            </DialogClose>
            <Button
              variant="ghost"
              className="rounded-full"
              onClick={() => {
                saving.current = true;
                router.push(exitTo!);
              }}
            >
              Quitter sans garder
            </Button>
            <Button className="rounded-full" onClick={() => finish(exitTo)}>
              Enregistrer et terminer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StepTitle({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Building2;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <span className="mx-auto grid size-12 place-items-center rounded-[17px] bg-[var(--brand-soft)] text-[var(--brand-deep)]">
        <Icon className="size-5" />
      </span>
      <h2 className="mt-4 text-2xl font-semibold tracking-[-0.035em] text-slate-900">
        {title}
      </h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">
        {description}
      </p>
    </div>
  );
}
