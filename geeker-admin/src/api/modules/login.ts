import { Login } from "@/api/interface/index";
import http from "@/api";
import businessMenuList from "@/assets/json/businessMenuList.json";
import { useUserStore } from "@/stores/modules/user";

export const loginApi = (params: Login.ReqLoginForm) => {
  return http.post<Login.ResLogin>(
    "/api/v1/auth/login",
    { account: params.username, password: params.password },
    { loading: false }
  );
};

export const getProfileApi = () => {
  return http.get<Login.ResLogin["user"]>("/api/v1/auth/me", {}, { loading: false });
};

export const getAuthMenuListApi = () => {
  const userStore = useUserStore();
  const role = userStore.userInfo.role;
  const fullMenu = businessMenuList.data as Menu.MenuOptions[];

  const menuData =
    role === "staff"
      ? fullMenu.filter(item => ["/home/index", "/lead", "/contract", "/worker"].includes(item.path))
      : fullMenu;

  return Promise.resolve({ code: 200, data: menuData, msg: "success" });
};

export const getAuthButtonListApi = () => {
  const userStore = useUserStore();
  const role = userStore.userInfo.role;

  if (role === "staff") {
    return Promise.resolve({
      code: 200,
      data: {
        dashboardWorkbench: ["view"],
        leadList: ["view", "create", "detail", "follow"],
        createLead: ["create"],
        leadDetail: ["view", "follow"],
        editLead: ["edit"],
        contractList: ["view", "create", "detail", "follow"],
        createContract: ["create"],
        contractDetail: ["view", "follow"],
        workerList: ["view", "toggle", "recommend", "edit"],
        createWorker: ["create"]
      },
      msg: "success"
    });
  }

  return Promise.resolve({
    code: 200,
    data: {
      dashboardWorkbench: ["view"],
      staffList: ["view", "detail", "edit", "toggle", "reset_password"],
      staffDetail: ["view"],
      editStaff: ["edit"],
      createStaff: ["create"],
      leadList: ["view", "create", "detail", "follow"],
      guestLeadList: ["view", "edit"],
      createLead: ["create"],
      leadDetail: ["view", "follow"],
      editLead: ["edit"],
      contractList: ["view", "create", "detail", "follow"],
      createContract: ["create"],
      contractDetail: ["view", "follow"],
      workerList: ["view", "toggle", "recommend", "edit"],
      createWorker: ["create"],
      userList: ["view", "toggle", "reset_password"]
    },
    msg: "success"
  });
};

export const logoutApi = () => {
  return Promise.resolve({ code: 200, data: null, msg: "success" });
};
