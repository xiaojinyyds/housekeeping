import http from "@/api";

export interface PageParams {
  page?: number;
  page_size?: number;
  keyword?: string;
}

export const getStatisticsApi = () => http.get("/api/v1/admin/statistics");

export const getLeadListApi = (
  params: PageParams & {
    status?: string;
    service_type?: string;
    owner_staff_id?: string;
    lead_category?: "A" | "B";
    start_date?: string;
    end_date?: string;
  }
) =>
  http.get("/api/v1/lead/list", params);

export const createLeadApi = (payload: Record<string, any>) => http.post("/api/v1/lead/create", payload);

export const getLeadDetailApi = (leadId: string) => http.get(`/api/v1/lead/${leadId}`);

export const updateLeadApi = (leadId: string, payload: Record<string, any>) => http.put(`/api/v1/lead/${leadId}`, payload);

export const getLeadFollowRecordsApi = (leadId: string) => http.get(`/api/v1/lead/${leadId}/follow-records`);

export const createLeadFollowRecordApi = (leadId: string, payload: Record<string, any>) =>
  http.post(`/api/v1/lead/${leadId}/follow-records`, payload);


export const getContractListApi = (
  params: PageParams & {
    status?: string;
    service_type?: string;
    broker_staff_id?: string;
    start_date?: string;
    end_date?: string;
  }
) => http.get("/api/v1/contract/list", params);

export const getContractStaffSummaryApi = (params?: {
  status?: string;
  service_type?: string;
  broker_staff_id?: string;
  start_date?: string;
  end_date?: string;
}) => http.get("/api/v1/contract/staff-summary", params);

export const createContractApi = (payload: Record<string, any>) => http.post("/api/v1/contract/create", payload);

export const getContractDetailApi = (contractId: string) => http.get(`/api/v1/contract/${contractId}`);

export const getContractFollowupsApi = (contractId: string) => http.get(`/api/v1/contract/${contractId}/followups`);

export const createContractFollowupApi = (contractId: string, payload: Record<string, any>) =>
  http.post(`/api/v1/contract/${contractId}/followups`, payload);

export const exportContractsApi = (params?: {
  broker_staff_id?: string;
  status?: string;
  service_type?: string;
  start_date?: string;
  end_date?: string;
}) =>
  http.get("/api/v1/data/export/contracts", params, {
    responseType: "blob",
    loading: false
  });

export const importContractsApi = (formData: FormData) =>
  http.post("/api/v1/data/import/contracts", formData, {
    loading: false,
    cancel: false,
    headers: { "Content-Type": "multipart/form-data" }
  });

export const downloadContractTemplateApi = () =>
  http.get("/api/v1/data/import/template/contracts", undefined, {
    responseType: "blob",
    loading: false
  });

export const getApplicationsApi = (params: { status?: string; page?: number; page_size?: number }) =>
  http.get("/api/v1/worker/applications", params);

export const reviewApplicationApi = (id: string, payload: { status: "approved" | "rejected"; reject_reason?: string }) =>
  http.post(`/api/v1/worker/applications/${id}/review`, payload);

export const getWorkersApi = (
  params: PageParams & {
    is_available?: boolean;
    address?: string;
    service_area?: string;
    job_type?: string;
    current_status?: string;
    min_age?: number;
    max_age?: number;
  }
) =>
  http.get("/api/v1/admin/workers/list", params);

export const getWorkerDetailApi = (workerId: string) => http.get(`/api/v1/worker/workers/${workerId}`);

export const updateWorkerApi = (workerId: string, payload: Record<string, any>) =>
  http.put(`/api/v1/admin/workers/${workerId}`, payload);

export const updateWorkerAvailableApi = (workerId: string, isAvailable: boolean) =>
  http.put(`/api/v1/admin/workers/${workerId}/available?is_available=${isAvailable}`);

export const updateWorkerRecommendApi = (workerId: string, isRecommended: boolean) =>
  http.put(`/api/v1/admin/workers/${workerId}/recommend?is_recommended=${isRecommended}`);

export const createWorkerApi = (payload: Record<string, any>) =>
  http.post("/api/v1/admin/workers/create", payload);

export const exportWorkersApi = (params?: {
  keyword?: string;
  is_available?: boolean;
  address?: string;
  service_area?: string;
  job_type?: string;
  current_status?: string;
  min_age?: number;
  max_age?: number;
}) =>
  http.get("/api/v1/data/export/workers", params, {
    responseType: "blob",
    loading: false
  });

export const importWorkersApi = (formData: FormData) =>
  http.post("/api/v1/data/import/workers", formData, {
    loading: false,
    cancel: false,
    headers: { "Content-Type": "multipart/form-data" }
  });

export const downloadWorkerTemplateApi = () =>
  http.get("/api/v1/data/import/template/workers", undefined, {
    responseType: "blob",
    loading: false
  });

export const createUserApi = (payload: Record<string, any>) =>
  http.post("/api/v1/admin/users/create", payload);

export const uploadBusinessImageApi = (formData: FormData, folder = "employee-certificates") =>
  http.post(`/api/v1/upload/image?folder=${folder}`, formData, {
    loading: false,
    cancel: false,
    headers: { "Content-Type": "multipart/form-data" }
  });

export const getUsersApi = (params: PageParams & { role?: string; status?: string }) =>
  http.get("/api/v1/admin/users", params);


export const getUserDetailApi = (userId: string) => http.get(`/api/v1/admin/users/${userId}`);

export const updateUserInfoApi = (userId: string, payload: Record<string, any>) =>
  http.put(`/api/v1/admin/users/${userId}/info`, payload);

export const updateUserStatusApi = (userId: string, status: string) =>
  http.put(`/api/v1/admin/users/${userId}/status?new_status=${status}`);

export const resetUserPasswordApi = (userId: string, newPassword: string) =>
  http.post(`/api/v1/admin/users/${userId}/reset-password`, { new_password: newPassword });

export const getGuestLeadsApi = (params: PageParams & { status?: string; customer_name?: string; customer_phone?: string }) =>
  http.get("/api/v1/appointment/guest-leads", params);

export const updateGuestLeadStatusApi = (leadId: string, status: string, remark?: string) =>
  http.put(`/api/v1/appointment/guest-leads/${leadId}/status`, {}, { params: { status, remark } });

export const exportLeadsApi = (params?: {
  owner_staff_id?: string;
  status?: string;
  service_type?: string;
  lead_category?: "A" | "B";
  start_date?: string;
  end_date?: string;
}) =>
  http.get("/api/v1/data/export/leads", params, {
    responseType: "blob",
    loading: false
  });

export const importLeadsApi = (formData: FormData) =>
  http.post("/api/v1/data/import/leads", formData, {
    loading: false,
    cancel: false,
    headers: { "Content-Type": "multipart/form-data" }
  });

export const downloadLeadTemplateApi = () =>
  http.get("/api/v1/data/import/template/leads", undefined, {
    responseType: "blob",
    loading: false
  });
