import type { CellValue } from "./types";

export type WorkshopPage = "company" | "documents" | "forecast" | "scenarios" | "actuals" | "reports";
export const workshopPages: { id: WorkshopPage; label: string }[] = [{ id: "company", label: "Entreprise" }, { id: "documents", label: "Documents" }, { id: "forecast", label: "Prévisionnel" }, { id: "scenarios", label: "Scénarios" }, { id: "actuals", label: "Réalisé" }, { id: "reports", label: "Livrables" }];
export type CompanyProfile = { name?: string; activity?: string; business_model?: string; years?: number; activity_start_month?: number; revenue_model?: string; start_year?: number; horizon_years?: number; activity_start?: string; objectives?: string; modules?: string[]; [key: string]: unknown };
export type Question = { field_id: string; label?: string; question?: string; value?: CellValue; status?: string; sheet?: string; cell?: string; required?: boolean; value_type?: string; module?: string; evidence_id?: string; options?: string[]; choices?: unknown[]; explanation?: string; unit?: string; calculated?: boolean };
export type Fact = { id?: string; label?: string; value?: CellValue; normalized_value?: CellValue; raw?: string; raw_value?: string; text?: string; page?: number; cell?: string; sheet?: string; field_id?: string; confidence?: number; cached_formula?: string; freshness?: string; evidence_id?: string; location?: { page?: number; sheet?: string; cell?: string; row?: number } };
export type Extraction = { id: string; source_id: string; title?: string; status?: string; text?: string; facts?: Fact[]; warnings?: string[]; diagnostics?: unknown; pages?: { page?: number; text?: string }[] };
export type Preview = { id?: string; approval_token?: string; changes?: Record<string, unknown>[]; diagnostics?: unknown; result?: Record<string, unknown>; [key: string]: unknown };
export type FinancialSeries = { id: string; label?: string; unit?: string; categories: string[]; values: (number | null)[]; status?: string };
export type Scenario = { id: string; name: string; case_id?: string; base_revision?: number; status?: string; metrics?: Record<string, unknown> | unknown[]; annual_metrics?: Record<string, unknown> | unknown[]; series?: FinancialSeries[] };
export type ActualRow = { period: string; metric: string; kind: string; value: number | string | null; unit: string; source_id?: string };
export type Shareholder = { name: string; shares: number };
export type FundingRound = { name: string; pre_money: number; investment: number; pool_percent: number; pool_timing: "before" | "after" };
export type Report = { id: string; revision?: number; status?: string; created_at?: string; formats?: string[]; warnings?: string[] };
