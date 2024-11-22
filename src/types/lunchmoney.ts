export interface LunchmoneyAsset {
  id: number;
  type_name: string;
  subtype_name?: string;
  name: string;
  display_name?: string;
  balance: string;
  balance_as_of: string;
  currency: string;
  status: "active" | "inactive";
  institution_name?: string;
  created_at: string;
  linked_account: string | null;
}

export interface LunchmoneyApiResponse {
  assets: LunchmoneyAsset[];
}