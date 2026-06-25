<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>编辑阿姨档案</h2>
        <p>这里修改的推荐理由、工作履历和证件图片，会同步影响小程序展示。</p>
      </div>
      <el-button @click="router.push(`/worker/detail/${workerId}`)">返回详情</el-button>
    </div>

    <div class="card form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="worker-form">
        <div class="grid three">
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入 11 位手机号" />
          </el-form-item>
          <el-form-item label="身份证号" prop="id_card">
            <el-input v-model="form.id_card" placeholder="请输入身份证号" />
          </el-form-item>
        </div>

        <div class="grid four">
          <el-form-item label="性别" prop="gender">
            <el-select v-model="form.gender" placeholder="请选择性别">
              <el-option label="女" value="female" />
              <el-option label="男" value="male" />
            </el-select>
          </el-form-item>
          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="form.age" :min="18" :max="70" class="full-width" />
          </el-form-item>
          <el-form-item label="从业年限" prop="experience_years">
            <el-input-number v-model="form.experience_years" :min="0" :max="50" class="full-width" />
          </el-form-item>
          <el-form-item label="期望薪资">
            <el-input-number v-model="form.expected_salary" :min="0" :precision="2" class="full-width" />
          </el-form-item>
        </div>

        <div class="grid three">
          <el-form-item label="微信号">
            <el-input v-model="form.wechat" placeholder="请输入微信号" />
          </el-form-item>
          <el-form-item label="紧急联系人">
            <el-input v-model="form.emergency_contact" placeholder="请输入紧急联系人" />
          </el-form-item>
          <el-form-item label="紧急联系电话">
            <el-input v-model="form.emergency_phone" placeholder="请输入紧急联系电话" />
          </el-form-item>
        </div>

        <div class="grid three">
          <el-form-item label="接单类型" class="span-full">
            <el-checkbox-group v-model="form.job_types">
              <el-checkbox v-for="item in JOB_TYPE_OPTIONS" :key="item" :label="item">{{ item }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="当前状态">
            <el-select v-model="form.current_status" placeholder="请选择当前状态">
              <el-option label="想接单" value="available" />
              <el-option label="上户中" value="on_job" />
              <el-option label="不接单" value="paused" />
              <el-option label="待确认" value="pending_confirm" />
              <el-option label="黑名单" value="blacklisted" />
              <el-option label="停用" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item label="可接单区域">
            <el-cascader
              v-model="form.service_area_codes"
              :options="regionOptions"
              :props="cascaderProps"
              placeholder="请选择可接单区域"
              clearable
              filterable
              multiple
              class="full-width"
            />
          </el-form-item>
        </div>

        <el-form-item label="居住地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入居住地址（现居住地）" />
        </el-form-item>

        <div class="grid four">
          <el-form-item label="属相">
            <el-input v-model="form.zodiac" placeholder="如：龙" />
          </el-form-item>
          <el-form-item label="婚姻状态">
            <el-input v-model="form.marital_status" placeholder="如：已婚" />
          </el-form-item>
          <el-form-item label="学历">
            <el-input v-model="form.education" placeholder="如：高中" />
          </el-form-item>
          <el-form-item label="籍贯">
            <el-input v-model="form.native_place" placeholder="如：四川成都" />
          </el-form-item>
        </div>

        <el-form-item label="专业技能" prop="skills">
          <el-checkbox-group v-model="form.skills">
            <el-checkbox v-for="item in SKILL_OPTIONS" :key="item" :label="item">{{ item }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <div class="section-block">
          <div class="section-head">
            <div>
              <h3>个人介绍</h3>
              <p>分栏填写，小程序详情将按栏目展示。</p>
            </div>
          </div>
          <el-form-item label="家庭情况" prop="family_situation">
            <el-input v-model="form.family_situation" type="textarea" :rows="3" placeholder="如：已婚，三口之家" />
          </el-form-item>
          <el-form-item label="性格描述" prop="personality_desc">
            <el-input v-model="form.personality_desc" type="textarea" :rows="3" placeholder="如：温和耐心、责任心强" />
          </el-form-item>
          <el-form-item label="性格爱好" prop="personality_hobbies">
            <el-input v-model="form.personality_hobbies" type="textarea" :rows="3" placeholder="如：喜欢孩子、热爱烹饪" />
          </el-form-item>
          <el-form-item label="擅长工作" prop="skilled_work">
            <el-input v-model="form.skilled_work" type="textarea" :rows="3" placeholder="如：小月龄照护、家常菜、家务整理" />
          </el-form-item>
        </div>

        <el-form-item label="推荐理由">
          <el-input
            v-model="form.recommendedReasonsText"
            type="textarea"
            :rows="4"
            placeholder="一行一条，如：性格温和&#10;会做宝宝辅食&#10;有高端家庭经验"
          />
        </el-form-item>

        <div class="section-block">
          <div class="section-head">
            <div>
              <h3>工作履历</h3>
              <p>用于小程序详情页展示，可维护多段履历。</p>
            </div>
            <el-button type="primary" plain @click="addExperience">新增履历</el-button>
          </div>

          <div v-if="form.work_experiences.length" class="experience-list">
            <div v-for="(item, index) in form.work_experiences" :key="index" class="experience-card">
              <div class="grid three">
                <el-form-item :label="`开始日期 ${index + 1}`">
                  <el-date-picker v-model="item.start_date" type="date" value-format="YYYY-MM-DD" placeholder="选择开始日期" class="full-width" />
                </el-form-item>
                <el-form-item label="结束日期">
                  <el-date-picker v-model="item.end_date" type="date" value-format="YYYY-MM-DD" placeholder="选择结束日期" class="full-width" />
                </el-form-item>
                <el-form-item label="服务单位/雇主">
                  <el-input v-model="item.company_name" placeholder="选填" />
                </el-form-item>
              </div>
              <el-form-item label="工作内容">
                <el-input v-model="item.job_content" type="textarea" :rows="3" placeholder="请输入这段履历的工作内容" />
              </el-form-item>
              <div class="experience-actions">
                <el-button type="danger" link @click="removeExperience(index)">删除这段履历</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂未添加工作履历" />
        </div>

        <el-form-item label="内部备注">
          <el-input v-model="form.internal_remark" type="textarea" :rows="3" placeholder="仅后台可见" />
        </el-form-item>

        <div class="upload-section avatar-section">
          <div class="section-head">
            <div>
              <h3>头像照片</h3>
              <p>用于小程序列表与详情页顶部展示。</p>
            </div>
            <el-tag type="info" effect="plain">小程序展示</el-tag>
          </div>
          <div class="avatar-upload">
            <ImageUploader v-model="form.avatar_url" folder="avatars" tip="建议上传清晰正面照" />
          </div>
        </div>

        <div class="upload-section life-photo-section">
          <div class="section-head">
            <div>
              <h3>生活工作照片</h3>
              <p>单独展示在小程序详情页「生活工作照片」区域，与下方证件照片无关。下方 5 个格子各上传 1 张，可传 1～5 张。</p>
            </div>
            <div class="section-head-actions">
              <el-tag type="warning" effect="plain">小程序展示</el-tag>
            </div>
          </div>
          <div class="life-photo-grid">
            <div v-for="index in MAX_LIFE_PHOTOS" :key="index" class="life-photo-item">
              <el-form-item :label="`生活照 ${index}`">
                <ImageUploader v-model="form.life_photos[index - 1]" folder="worker-life" tip="日常、工作场景照片（选填）" />
              </el-form-item>
              <el-button v-if="form.life_photos[index - 1]" type="danger" link @click="clearLifePhoto(index - 1)">清空</el-button>
            </div>
          </div>
        </div>

        <div class="upload-section cert-section">
          <div class="section-head">
            <div>
              <h3>证件照片</h3>
              <p>身份证、健康证等内部存档资料，不在小程序生活照区域展示。</p>
            </div>
            <el-tag type="success" effect="plain">内部存档</el-tag>
          </div>
          <div class="certificate-grid">
          <el-form-item label="身份证人像面" prop="id_card_front">
            <ImageUploader v-model="form.id_card_front" folder="worker-id-card" />
          </el-form-item>
          <el-form-item label="身份证国徽面" prop="id_card_back">
            <ImageUploader v-model="form.id_card_back" folder="worker-id-card" />
          </el-form-item>
          <el-form-item label="健康证">
            <ImageUploader v-model="form.health_certificate" folder="worker-certificates" />
          </el-form-item>
          <el-form-item label="体检报告">
            <ImageUploader v-model="form.health_report" folder="worker-certificates" />
          </el-form-item>
          <el-form-item label="职业证书">
            <ImageUploader v-model="form.practice_certificate" folder="worker-certificates" />
          </el-form-item>
          <el-form-item label="其他证件1">
            <ImageUploader v-model="form.other_certificate_1" folder="worker-certificates" />
          </el-form-item>
          <el-form-item label="其他证件2">
            <ImageUploader v-model="form.other_certificate_2" folder="worker-certificates" />
          </el-form-item>
          <el-form-item label="其他证件3">
            <ImageUploader v-model="form.other_certificate_3" folder="worker-certificates" />
          </el-form-item>
          </div>
        </div>

        <div class="switch-row">
          <el-form-item>
            <el-switch v-model="form.is_available" inline-prompt active-text="是" inactive-text="否" />
            <span class="switch-label">当前可接单</span>
          </el-form-item>
          <el-form-item>
            <el-switch v-model="form.is_recommended" inline-prompt active-text="是" inactive-text="否" />
            <span class="switch-label">首页推荐展示</span>
          </el-form-item>
          <el-form-item>
            <el-switch v-model="form.can_drive" inline-prompt active-text="是" inactive-text="否" />
            <span class="switch-label">可驾驶车辆</span>
          </el-form-item>
        </div>

        <div class="actions">
          <el-button @click="loadDetail">重新加载</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">保存修改</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { getWorkerDetailApi, updateWorkerApi } from "@/api/modules/business";
import ImageUploader from "../createWorker/components/ImageUploader.vue";
import { useCascaderAreaData } from "@vant/area-data";
import { JOB_TYPE_OPTIONS, SKILL_OPTIONS } from "@/constants/workerOptions";

const MAX_LIFE_PHOTOS = 5;

const padLifePhotos = (photos: string[] = []) => {
  const filled = photos.map(item => (item || "").trim()).filter(Boolean).slice(0, MAX_LIFE_PHOTOS);
  return Array.from({ length: MAX_LIFE_PHOTOS }, (_, index) => filled[index] || "");
};

interface ExperienceItem {
  start_date: string;
  end_date: string;
  company_name: string;
  job_content: string;
}

interface WorkerEditFormState {
  real_name: string;
  phone: string;
  id_card: string;
  gender: "female" | "male";
  age: number;
  experience_years: number;
  wechat: string;
  emergency_contact: string;
  emergency_phone: string;
  address: string;
  zodiac: string;
  marital_status: string;
  education: string;
  native_place: string;
  life_photos: string[];
  address_codes: string[];
  address_detail: string;
  service_area_codes: string[][];
  skills: string[];
  job_types: string[];
  serviceAreasText: string;
  family_situation: string;
  personality_desc: string;
  personality_hobbies: string;
  skilled_work: string;
  recommendedReasonsText: string;
  internal_remark: string;
  expected_salary?: number;
  current_status: string;
  avatar_url: string;
  id_card_front: string;
  id_card_back: string;
  health_certificate: string;
  health_report: string;
  practice_certificate: string;
  other_certificate_1: string;
  other_certificate_2: string;
  other_certificate_3: string;
  is_available: boolean;
  is_recommended: boolean;
  can_drive: boolean;
  work_experiences: ExperienceItem[];
}

const route = useRoute();
const router = useRouter();
const workerId = String(route.params.workerId || "");
const formRef = ref<FormInstance>();
const loading = ref(false);
const submitting = ref(false);

const createExperience = (): ExperienceItem => ({
  start_date: "",
  end_date: "",
  company_name: "",
  job_content: ""
});

const createDefaultForm = (): WorkerEditFormState => ({
  real_name: "",
  phone: "",
  id_card: "",
  gender: "female",
  age: 30,
  experience_years: 1,
  wechat: "",
  emergency_contact: "",
  emergency_phone: "",
  address: "",
  zodiac: "",
  marital_status: "",
  education: "",
  native_place: "",
  life_photos: padLifePhotos(),
  address_codes: [],
  address_detail: "",
  service_area_codes: [],
  skills: [],
  job_types: [],
  serviceAreasText: "",
  family_situation: "",
  personality_desc: "",
  personality_hobbies: "",
  skilled_work: "",
  recommendedReasonsText: "",
  internal_remark: "",
  expected_salary: undefined,
  current_status: "available",
  avatar_url: "",
  id_card_front: "",
  id_card_back: "",
  health_certificate: "",
  health_report: "",
  practice_certificate: "",
  other_certificate_1: "",
  other_certificate_2: "",
  other_certificate_3: "",
  is_available: true,
  is_recommended: false,
  can_drive: false,
  work_experiences: []
});

const form = reactive<WorkerEditFormState>(createDefaultForm());

// 使用 @vant/area-data 的省市区数据
const regionOptions = useCascaderAreaData();

// 级联选择器配置
const cascaderProps = {
  value: 'value',
  label: 'text',
  children: 'children',
  checkStrictly: false,
  emitPath: true
};

const rules: FormRules<WorkerEditFormState> = {
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  phone: [{ required: true, message: "请输入手机号", trigger: "blur" }],
  gender: [{ required: true, message: "请选择性别", trigger: "change" }],
  age: [{ required: true, message: "请输入年龄", trigger: "change" }],
  experience_years: [{ required: true, message: "请输入从业年限", trigger: "change" }],
  address: [{ required: true, message: "请输入居住地址", trigger: "blur" }],
  skills: [{ type: "array", required: true, min: 1, message: "请至少选择一项专业技能", trigger: "change" }],
  family_situation: [{ validator: validateIntroSection, trigger: "blur" }]
};

function validateIntroSection(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (
    form.family_situation.trim() ||
    form.personality_desc.trim() ||
    form.personality_hobbies.trim() ||
    form.skilled_work.trim()
  ) {
    callback();
    return;
  }
  callback(new Error("请至少填写一项个人介绍"));
}

const splitCommaText = (value: string) =>
  value
    .split(/[\n,，]/)
    .map(item => item.trim())
    .filter(Boolean);

const clearLifePhoto = (index: number) => {
  form.life_photos[index] = "";
};

const buildLifePhotosPayload = () => form.life_photos.map(item => item.trim()).filter(Boolean).slice(0, MAX_LIFE_PHOTOS);

const addExperience = () => {
  form.work_experiences.push(createExperience());
};

const removeExperience = (index: number) => {
  form.work_experiences.splice(index, 1);
};

const buildExperiencePayload = () =>
  form.work_experiences
    .map((item, index) => ({
      start_date: item.start_date || null,
      end_date: item.end_date || null,
      company_name: item.company_name.trim(),
      job_content: item.job_content.trim(),
      sort_order: index
    }))
    .filter(item => item.job_content);

const normalizeServiceAreaCodes = (codes: unknown): string[][] => {
  if (!Array.isArray(codes) || !codes.length) return [];
  if (Array.isArray(codes[0])) return codes as string[][];
  if (typeof codes[0] === "string") return [codes as string[]];
  return [];
};

const loadDetail = async () => {
  if (!workerId) return;
  loading.value = true;
  try {
    const response = (await getWorkerDetailApi(workerId)) as any;
    const data = response?.data ?? response ?? {};
    const otherCertificates = Array.isArray(data.other_certificates) ? data.other_certificates : [];
    const workExperiences = Array.isArray(data.work_experiences) ? data.work_experiences : [];

    Object.assign(form, {
      real_name: data.real_name || "",
      phone: data.phone || "",
      id_card: data.id_card || "",
      gender: data.gender || "female",
      age: Number(data.age || 30),
      experience_years: Number(data.experience_years || 0),
      wechat: data.wechat || "",
      emergency_contact: data.emergency_contact || "",
      emergency_phone: data.emergency_phone || "",
      address: data.address || "",
      zodiac: data.zodiac || "",
      marital_status: data.marital_status || "",
      education: data.education || "",
      native_place: data.native_place || "",
      life_photos: padLifePhotos(Array.isArray(data.life_photos) ? data.life_photos : []),
      address_codes: data.address_codes || [],
      address_detail: data.address_detail || "",
      skills: Array.isArray(data.skills) ? [...data.skills] : [],
      job_types: Array.isArray(data.job_types) ? [...data.job_types] : [],
      serviceAreasText: Array.isArray(data.service_areas) ? data.service_areas.join(",") : "",
      service_area_codes: normalizeServiceAreaCodes(data.service_area_codes),
      family_situation: data.family_situation || "",
      personality_desc: data.personality_desc || "",
      personality_hobbies: data.personality_hobbies || "",
      skilled_work: data.skilled_work || "",
      recommendedReasonsText: Array.isArray(data.recommended_reasons) ? data.recommended_reasons.join("\n") : "",
      internal_remark: data.internal_remark || "",
      expected_salary: data.expected_salary ?? undefined,
      current_status: data.current_status || "available",
      avatar_url: data.avatar_url || "",
      id_card_front: data.id_card_front || "",
      id_card_back: data.id_card_back || "",
      health_certificate: data.health_certificate || "",
      health_report: data.health_report || "",
      practice_certificate: data.practice_certificate || "",
      other_certificate_1: otherCertificates[0] || "",
      other_certificate_2: otherCertificates[1] || "",
      other_certificate_3: otherCertificates[2] || "",
      is_available: Boolean(data.is_available),
      is_recommended: Boolean(data.is_recommended),
      can_drive: Boolean(data.can_drive),
      work_experiences: workExperiences.map((item: any) => ({
        start_date: item.start_date || "",
        end_date: item.end_date || "",
        company_name: item.company_name || "",
        job_content: item.job_content || ""
      }))
    });
    formRef.value?.clearValidate();
  } finally {
    loading.value = false;
  }
};

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid || !workerId) return;

  submitting.value = true;
  try {
    // 构建完整地址
    const getRegionName = (codes: string[]) => {
      if (!codes || codes.length === 0) return "";
      let names: string[] = [];
      let current = regionOptions;

      for (const code of codes) {
        const found = current.find(item => item.value === code);
        if (found) {
          names.push(found.text);
          current = found.children || [];
        }
      }
      return names.join("");
    };

    // 构建服务区域名称
    // service_area_codes 可能是 string[][] (多选) 或 string[] (单选)
    const getServiceAreaNames = (codes: any) => {
      if (!codes || !Array.isArray(codes)) return [];
      // 如果是单选（每个元素是字符串），转换为嵌套数组
      const codeArrays: string[][] = codes.length > 0 && typeof codes[0] === "string"
        ? [codes as string[]]
        : codes as string[][];
      return codeArrays.map(codeArray => getRegionName(codeArray)).filter(Boolean);
    };

    await updateWorkerApi(workerId, {
      real_name: form.real_name,
      phone: form.phone,
      id_card: form.id_card,
      gender: form.gender,
      age: form.age,
      experience_years: form.experience_years,
      wechat: form.wechat,
      emergency_contact: form.emergency_contact,
      emergency_phone: form.emergency_phone,
      address: form.address,
      zodiac: form.zodiac,
      marital_status: form.marital_status,
      education: form.education,
      native_place: form.native_place,
      life_photos: buildLifePhotosPayload(),
      address_codes: form.address_codes || [],
      address_detail: form.address_detail || "",
      skills: form.skills,
      job_types: form.job_types,
      service_areas: getServiceAreaNames(form.service_area_codes || []),
      service_area_codes: form.service_area_codes || [],
      family_situation: form.family_situation.trim(),
      personality_desc: form.personality_desc.trim(),
      personality_hobbies: form.personality_hobbies.trim(),
      skilled_work: form.skilled_work.trim(),
      recommended_reasons: splitCommaText(form.recommendedReasonsText),
      work_experiences: buildExperiencePayload(),
      internal_remark: form.internal_remark,
      expected_salary: form.expected_salary,
      current_status: form.current_status,
      avatar_url: form.avatar_url || "",
      id_card_front: form.id_card_front,
      id_card_back: form.id_card_back,
      health_certificate: form.health_certificate || "",
      health_report: form.health_report || "",
      practice_certificate: form.practice_certificate || "",
      other_certificates: [form.other_certificate_1, form.other_certificate_2, form.other_certificate_3].filter(Boolean),
      is_available: form.is_available,
      is_recommended: form.is_recommended,
      can_drive: form.can_drive
    });
    ElMessage.success("阿姨档案更新成功");
    router.push({ path: `/worker/detail/${workerId}`, query: { refresh: Date.now().toString() } });
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || "更新失败");
  } finally {
    submitting.value = false;
  }
};

loadDetail();
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-card,
.form-card {
  padding: 20px;
}

.header-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.worker-form {
  width: 100%;
}

.grid,
.upload-grid,
.switch-row {
  display: grid;
  gap: 16px;
}

.grid.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid.four {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.upload-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.certificate-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.life-photo-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.upload-section {
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  background: var(--el-fill-color-extra-light);
}

.upload-section .section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.upload-section .section-head h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
}

.upload-section .section-head p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.section-head-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.avatar-upload {
  max-width: 200px;
}

.life-photo-section {
  border-color: rgba(230, 162, 60, 0.45);
  background: rgba(230, 162, 60, 0.04);
}

.cert-section {
  border-color: rgba(103, 194, 58, 0.35);
  background: rgba(103, 194, 58, 0.03);
}

.switch-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.span-full {
  grid-column: 1 / -1;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
}

.life-photo-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-block {
  margin-bottom: 22px;
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  background: var(--el-fill-color-extra-light);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-head h3 {
  margin: 0 0 4px;
}

.section-head p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.experience-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.experience-card {
  padding: 16px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
}

.experience-actions {
  display: flex;
  justify-content: flex-end;
}

.full-width {
  width: 100%;
}

.switch-label {
  margin-left: 12px;
  color: var(--el-text-color-secondary);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 1200px) {
  .grid.four,
  .grid.three,
  .upload-grid,
  .certificate-grid,
  .life-photo-grid,
  .switch-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .header-card,
  .grid.three,
  .grid.four,
  .upload-grid,
  .certificate-grid,
  .life-photo-grid,
  .switch-row,
  .section-head {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
