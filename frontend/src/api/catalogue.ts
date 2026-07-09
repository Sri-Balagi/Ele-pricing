import apiClient from "./client";

type Category   = { id: string; name: string; description: string; active: boolean };
type Feature    = { id: string; name: string; description: string; group_id: string; category_id: string; required: boolean; active: boolean };
type FeatureOpt = { id: string; feature_id: string; display_name: string; description: string; active: boolean };

export const catalogueApi = {
  getCategories: (): Promise<Category[]> =>
    apiClient.get<Category[]>("/catalogue/categories"),

  getFeatures: (): Promise<Feature[]> =>
    apiClient.get<Feature[]>("/catalogue/features"),

  getFeatureOptions: (): Promise<FeatureOpt[]> =>
    apiClient.get<FeatureOpt[]>("/catalogue/feature-options"),
};
