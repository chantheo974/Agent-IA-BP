import type { ReactNode } from 'react';
import type { Agent, Case, Draft, Job, Sheet, Source, CellValue } from '../types';
import type { WorkshopPage, FinancialSeries } from '../workshopTypes';

export type ConnectedProps = {
  cases: Case[]; caseId: string; active: Case | null; initializing: boolean;
  connection: string; sources: Source[]; agents: Agent[]; sheets: Sheet[];
  sheetName: string; jobs: Job[]; draft: Draft; refresh: number; blocked: boolean;
  error: string; notice: string; onDismiss: () => void; onRefresh: () => Promise<void>;
  onCase: (id: string) => void; onNew: () => void; onSettings: () => void;
  onSource: () => void; onDraft: () => void; onVersions: () => void;
  onDownload: () => void; onJobs: () => void;
  onSheet: (name: string, cell?: string) => void;
  onContext: (sheet: string, prompt?: string) => void;
  toolbar: ReactNode; draftBar: ReactNode; dialogs: ReactNode; dialogsOpen: boolean; chat: ReactNode;
  workshop: (page: WorkshopPage, onSheet: (name: string, cell?: string) => void) => ReactNode;
  grid: (onDiscuss: () => void) => ReactNode;
};
export type BusinessField = {
  field_id: string; label: string; value_type?: string; unit?: string;
  choices?: unknown[]; can_propose: boolean; binding_count: number;
};
export type CatalogSheet = {
  id: string; name: string; original_name: string; label: string; purpose: string;
  role: string; group_id: string; theme_ids: string[]; view_kind: string;
  field_count: number; binding_count: number;
  dependencies: { id: string; name: string; label: string }[];
  dependency_basis: string; fields: BusinessField[];
  register: null | { start_row: number; end_row: number; can_add: boolean };
};
export type Catalog = {
  schema: string; case_id: string; revision: number; calculation_status: string;
  profile_version: string; profile_sha256: string;
  groups: { id: string; label: string }[]; themes: { id: string; label: string }[];
  sheets: CatalogSheet[];
};
export type SheetEntry = {
  binding_id: string; field_id: string; sheet_id: string; sheet: string; cell: string;
  label: string; value: CellValue; current_value: CellValue; proposed: boolean;
  formula: string | null; unit?: string; value_type?: string; choices?: unknown[];
  evidence_id?: string; status?: string; calculated: boolean; editable: boolean; reason?: string;
};
export type SheetView = {
  case_id: string; revision: number; calculation_status: string; sheet: CatalogSheet;
  entries: SheetEntry[]; total: number; offset: number; limit: number;
  draft: { id?: string; status: string; current: boolean };
};
export type Metric = { id: string; label: string; value: unknown; unit?: string; status?: string; period?: string };
export type Comparison = { scenarios?: { id: string; name: string; case_id?: string; metrics?: Metric[]; series?: FinancialSeries[] }[]; metrics?: Metric[]; calendars_identical?: boolean };
