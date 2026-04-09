<template>
  <div class="page">
    <div class="card header-card">
      <div>
        <h2>新建阿姨档案</h2>
        <p>系统自动生成内部登录账号，前台展示与小程序展示会直接复用这里的内容。</p>
      </div>
      <el-button @click="router.push('/worker/list')">返回列表</el-button>
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
          <el-form-item label="接单类型">
            <el-input v-model="form.jobTypesText" placeholder="多个类型请用逗号分隔，如：住家保姆,月嫂" />
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
          <el-form-item label="服务区域">
            <el-input v-model="form.serviceAreasText" placeholder="多个区域请用逗号分隔，如：浦东新区,徐汇区" />
          </el-form-item>
        </div>

        <el-form-item label="居住地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入居住地址" />
        </el-form-item>

        <el-form-item label="技能标签" prop="skillsText">
          <el-input v-model="form.skillsText" placeholder="多个标签请用逗号分隔，如：做饭,保洁,带娃" />
        </el-form-item>

        <el-form-item label="个人简介" prop="introduction">
          <el-input v-model="form.introduction" type="textarea" :rows="4" placeholder="请输入阿姨的经验、擅长方向和服务特点" />
        </el-form-item>

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
              <p>用于小程序详情页展示，可录入多段经历。</p>
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

        <el-form-item label="头像">
          <ImageUploader v-model="form.avatar_url" folder="avatars" tip="建议上传清晰正面照" />
        </el-form-item>

        <div class="upload-grid">
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
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">创建阿姨档案</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { createWorkerApi } from "@/api/modules/business";
import ImageUploader from "./components/ImageUploader.vue";

interface ExperienceItem {
  start_date: string;
  end_date: string;
  company_name: string;
  job_content: string;
}

interface WorkerFormState {
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
  skillsText: string;
  jobTypesText: string;
  serviceAreasText: string;
  introduction: string;
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

const router = useRouter();
const formRef = ref<FormInstance>();
const submitting = ref(false);

const createExperience = (): ExperienceItem => ({
  start_date: "",
  end_date: "",
  company_name: "",
  job_content: ""
});

const createDefaultForm = (): WorkerFormState => ({
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
  skillsText: "",
  jobTypesText: "",
  serviceAreasText: "",
  introduction: "",
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

const form = reactive<WorkerFormState>(createDefaultForm());

const rules: FormRules<WorkerFormState> = {
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  phone: [{ required: true, message: "请输入手机号", trigger: "blur" }],
  id_card: [{ required: true, message: "请输入身份证号", trigger: "blur" }],
  gender: [{ required: true, message: "请选择性别", trigger: "change" }],
  age: [{ required: true, message: "请输入年龄", trigger: "change" }],
  experience_years: [{ required: true, message: "请输入从业年限", trigger: "change" }],
  address: [{ required: true, message: "请输入居住地址", trigger: "blur" }],
  skillsText: [{ required: true, message: "请至少输入一项技能", trigger: "blur" }],
  introduction: [{ required: true, message: "请输入个人简介", trigger: "blur" }],
  id_card_front: [{ required: true, message: "请上传身份证人像面", trigger: "change" }],
  id_card_back: [{ required: true, message: "请上传身份证国徽面", trigger: "change" }]
};

const splitCommaText = (value: string) =>
  value
    .split(/[\n,，]/)
    .map(item => item.trim())
    .filter(Boolean);

const resetForm = () => {
  Object.assign(form, createDefaultForm());
  formRef.value?.clearValidate();
};

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

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    await createWorkerApi({
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
      skills: splitCommaText(form.skillsText),
      job_types: splitCommaText(form.jobTypesText),
      service_areas: splitCommaText(form.serviceAreasText),
      introduction: form.introduction,
      recommended_reasons: splitCommaText(form.recommendedReasonsText),
      work_experiences: buildExperiencePayload(),
      internal_remark: form.internal_remark,
      expected_salary: form.expected_salary,
      current_status: form.current_status,
      avatar_url: form.avatar_url || undefined,
      id_card_front: form.id_card_front,
      id_card_back: form.id_card_back,
      health_certificate: form.health_certificate || undefined,
      health_report: form.health_report || undefined,
      practice_certificate: form.practice_certificate || undefined,
      other_certificates: [form.other_certificate_1, form.other_certificate_2, form.other_certificate_3].filter(Boolean),
      is_available: form.is_available,
      is_recommended: form.is_recommended,
      can_drive: form.can_drive
    });

    ElMessage.success("阿姨档案创建成功");
    router.push("/worker/list");
  } finally {
    submitting.value = false;
  }
};
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

.switch-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
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
  .switch-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .header-card,
  .grid.three,
  .grid.four,
  .upload-grid,
  .switch-row,
  .section-head {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
