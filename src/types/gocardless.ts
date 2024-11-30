export interface Requisition {
  id: string;
  created: string;
  status: 'CR' | 'LN' | 'RJ' | 'ER' | 'EX' | 'GA';
  institution_id: string;
  agreement: string;
  reference: string;
  accounts: string[] | BankAccount[];
  user_language: string;
  link: string;
  ssn: string | null;
  account_selection: boolean;
  redirect: string | null;
}

export interface RequisitionsResponse {
  count: number;
  results: Requisition[];
}

export interface TokenResponse {
  access: string;
  access_expires: number;
  refresh: string;
  refresh_expires: number;
}

export interface BankAccount {
  id: string;
  created: string;
  last_accessed: string;
  iban: string;
  institution_id: string;
  status: string;
  owner_name: string;
  currency: string;
  balance: {
    amount: string;
    currency: string;
  };
}

export interface RequisitionDetails extends Requisition {
  accounts: BankAccount[];
}

export interface Institution {
  id: string;
  name: string;
  bic: string;
  transaction_total_days: number;
  countries: string[];
  logo: string;
}

export type InstitutionsResponse = Institution[];