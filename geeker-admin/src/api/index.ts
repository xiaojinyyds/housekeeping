import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { ElMessage } from "element-plus";
import { showFullScreenLoading, tryHideFullScreenLoading } from "@/components/Loading/fullScreen";
import { LOGIN_URL } from "@/config";
import { ResultData } from "@/api/interface";
import { ResultEnum } from "@/enums/httpEnum";
import { checkStatus } from "./helper/checkStatus";
import { AxiosCanceler } from "./helper/axiosCancel";
import { useUserStore } from "@/stores/modules/user";
import router from "@/routers";

export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  loading?: boolean;
  cancel?: boolean;
}

const envBaseUrl = (import.meta.env.VITE_API_URL as string) || "";
// All API modules already use paths like "/api/v1/...".
// Avoid duplicating "/api" (e.g. "/api/api/v1/...") when env base is "/api".
const normalizedBaseUrl = envBaseUrl === "/api" ? "" : envBaseUrl;

const config = {
  baseURL: normalizedBaseUrl,
  timeout: ResultEnum.TIMEOUT as number,
  withCredentials: true
};

const axiosCanceler = new AxiosCanceler();

class RequestHttp {
  service: AxiosInstance;

  public constructor(config: AxiosRequestConfig) {
    this.service = axios.create(config);

    this.service.interceptors.request.use(
      (config: CustomAxiosRequestConfig) => {
        const userStore = useUserStore();
        config.cancel ??= true;
        config.cancel && axiosCanceler.addPending(config);
        config.loading ??= true;
        config.loading && showFullScreenLoading();
        if (config.headers && typeof config.headers.set === "function" && userStore.token) {
          config.headers.set("Authorization", `Bearer ${userStore.token}`);
        }
        return config;
      },
      (error: AxiosError) => Promise.reject(error)
    );

    this.service.interceptors.response.use(
      (response: AxiosResponse & { config: CustomAxiosRequestConfig }) => {
        const { data, config } = response;
        const responseType = config.responseType;
        const normalizedData = { ...data, msg: data?.msg ?? data?.message ?? "" };
        const userStore = useUserStore();
        axiosCanceler.removePending(config);
        config.loading && tryHideFullScreenLoading();

        // File download or binary response: return raw data directly.
        if (responseType === "blob" || responseType === "arraybuffer") {
          return data;
        }

        if (normalizedData.code == ResultEnum.OVERDUE) {
          userStore.setToken("");
          userStore.setUserInfo({ name: "" });
          router.replace(LOGIN_URL);
          ElMessage.error(normalizedData.msg || "登录已失效");
          return Promise.reject(normalizedData);
        }

        if (normalizedData.code && normalizedData.code !== ResultEnum.SUCCESS) {
          ElMessage.error(normalizedData.msg || "请求失败");
          return Promise.reject(normalizedData);
        }

        return normalizedData;
      },
      async (error: AxiosError) => {
        const isCanceled =
          (error as any)?.name === "CanceledError" ||
          (error as any)?.code === "ERR_CANCELED" ||
          String(error?.message || "").toLowerCase().includes("canceled");
        if (isCanceled) {
          tryHideFullScreenLoading();
          return Promise.reject(error);
        }

        const { response } = error;
        tryHideFullScreenLoading();
        if (error.message.indexOf("timeout") !== -1) ElMessage.error("请求超时，请稍后重试");
        if (error.message.indexOf("Network Error") !== -1) ElMessage.error("网络错误，请稍后重试");
        if (response?.status === 401) {
          const userStore = useUserStore();
          userStore.setToken("");
          userStore.setUserInfo({ name: "" });
          router.replace(LOGIN_URL);
        }
        if (response) checkStatus(response.status);
        if (!window.navigator.onLine) router.replace("/500");
        return Promise.reject(error);
      }
    );
  }

  get<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>> {
    return this.service.get(url, { params, ..._object });
  }

  post<T>(url: string, params?: object | string | FormData, _object = {}): Promise<ResultData<T>> {
    return this.service.post(url, params, _object);
  }

  put<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>> {
    return this.service.put(url, params, _object);
  }

  delete<T>(url: string, params?: any, _object = {}): Promise<ResultData<T>> {
    return this.service.delete(url, { params, ..._object });
  }

  download(url: string, params?: object, _object = {}): Promise<BlobPart> {
    return this.service.post(url, params, { ..._object, responseType: "blob" });
  }
}

export default new RequestHttp(config);
