import type { CompanyProfile } from "./workshopTypes";

/** Canonical API fields win over the historical form aliases, when present. */
export function companyProfileForForm(source: CompanyProfile, defaultYear = new Date().getFullYear()): CompanyProfile {
  const start_year = source.start_year ?? defaultYear;
  const years = source.years ?? source.horizon_years ?? 5;
  const business_model = source.business_model ?? source.revenue_model ?? (source.activity || "services");
  const date = /^(\d{4})-(\d{2})-(\d{2})$/.exec(source.activity_start || "");
  const activity_start_month = source.activity_start_month ?? (date ? Number(date[2]) : 1);
  // The API calendar is monthly. Keep a historical day only when it belongs
  // to that same year/month; otherwise show the first day of the stored month.
  const activity_start = date && Number(date[1]) === start_year && Number(date[2]) === activity_start_month
    ? source.activity_start
    : `${start_year}-${String(activity_start_month).padStart(2, "0")}-01`;
  return { ...source, start_year, years, business_model, activity_start_month,
    horizon_years: years, revenue_model: business_model, activity_start };
}

/** Update the canonical value alongside an explicitly edited form alias. */
export function editCompanyProfile(current: CompanyProfile, key: keyof CompanyProfile, value: unknown): CompanyProfile {
  const result = { ...current, [key]: value };
  if (key === "horizon_years") result.years = value as number;
  if (key === "revenue_model") result.business_model = value as string;
  if (key === "activity_start" && typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    result.activity_start_month = Number(value.slice(5, 7));
  }
  if (key === "start_year") return companyProfileForForm(result);
  return result;
}
