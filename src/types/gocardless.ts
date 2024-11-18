export interface Requisition {
  id: string;
  created: string;
  status: 'CR' | 'LN' | 'RJ' | 'ER' | 'EX' | 'GA';
  institution_id: string;
  agreement: string;
  reference: string;
  accounts: string[];
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
  created_at: string;
  account_holder_name: string;
  account_number_ending: string;
  bank_name: string;
  currency: string;
  status: string;
  metadata: Record<string, string>;
}

export interface AccountsResponse {
  bank_accounts: BankAccount[];
  meta: {
    cursors: {
      before: string | null;
      after: string | null;
    };
    limit: number;
  };
}