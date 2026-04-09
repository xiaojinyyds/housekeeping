<script setup lang="ts">
import { showToast, showDialog } from 'vant'
import type { UploaderFileListItem } from 'vant'
import apiWorker from '@/api/modules/worker'
import apiUpload from '@/api/modules/upload'

definePage({
  name: 'worker-apply',
  meta: {
    title: '申请成为家政阿姨',
    auth: true,
  },
})

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const uploading = ref(false)

// 当前步骤 (0: 基本信息, 1: 技能经验, 2: 实名认证)
const currentStep = ref(0)

// 页面加载时检查是否已有申请
onMounted(async () => {
  try {
    const res = await apiWorker.getMyApplication()
    if (res.code === 200 && res.data) {
      // 已有申请记录，跳转到申请状态页面
      showToast('您已提交过申请')
      router.replace('/worker/application-status')
    }
  }
  catch (error) {
    // 没有申请记录或接口报错，继续显示申请表单
  }
})

// 步骤列表
const steps = [
  { text: '基本信息' },
  { text: '技能经验' },
  { text: '实名认证' },
]

// 表单数据
const formData = reactive({
  real_name: '',
  id_card: '',
  age: '',
  gender: 'female',
  address: '',
  phone: '',
  experience_years: '',
  skills: [] as string[],
  introduction: '',
  id_card_front: '',
  id_card_back: '',
  health_certificate: '',
  health_report: '',
  practice_certificate: '',
  other_certificates: [] as string[],
})

// 技能选项
const skillOptions = [
  { text: '保洁', value: '保洁', icon: 'brush-o' },
  { text: '月嫂', value: '月嫂', icon: 'smile-o' },
  { text: '育儿', value: '育儿', icon: 'friends-o' },
  { text: '护理', value: '护理', icon: 'like-o' },
  { text: '烹饪', value: '烹饪', icon: 'fire-o' },
  { text: '陪护', value: '陪护', icon: 'user-o' },
]

// 性别选项
const genderOptions = [
  { text: '女', value: 'female' },
  { text: '男', value: 'male' },
]

// 文件列表
const idCardFrontList = ref<UploaderFileListItem[]>([])
const idCardBackList = ref<UploaderFileListItem[]>([])
const healthCertList = ref<UploaderFileListItem[]>([])
const healthReportList = ref<UploaderFileListItem[]>([])
const practiceCertList = ref<UploaderFileListItem[]>([])
const otherCertsList = ref<UploaderFileListItem[]>([])

// 上传图片
async function uploadImage(file: File): Promise<string> {
  try {
    const res = await apiUpload.uploadImage(file, 'certificates')
    if (res.code === 200) {
      return res.data.url
    }
    throw new Error('上传失败')
  }
  catch (error: any) {
    showToast(error.message || '上传失败')
    throw error
  }
}

// 上传身份证正面
async function afterReadIdCardFront(file: any) {
  uploading.value = true
  try {
    const url = await uploadImage(file.file)
    formData.id_card_front = url
    showToast('上传成功')
  }
  finally {
    uploading.value = false
  }
}

// 上传身份证反面
async function afterReadIdCardBack(file: any) {
  uploading.value = true
  try {
    const url = await uploadImage(file.file)
    formData.id_card_back = url
    showToast('上传成功')
  }
  finally {
    uploading.value = false
  }
}

// 上传健康证
async function afterReadHealthCert(file: any) {
  uploading.value = true
  try {
    const url = await uploadImage(file.file)
    formData.health_certificate = url
    showToast('上传成功')
  }
  finally {
    uploading.value = false
  }
}

// 上传体检报告
async function afterReadHealthReport(file: any) {
  uploading.value = true
  try {
    const url = await uploadImage(file.file)
    formData.health_report = url
    showToast('上传成功')
  }
  finally {
    uploading.value = false
  }
}

// 上传执业证书
async function afterReadPracticeCert(file: any) {
  uploading.value = true
  try {
    const url = await uploadImage(file.file)
    formData.practice_certificate = url
    showToast('上传成功')
  }
  finally {
    uploading.value = false
  }
}

// 上传其他证书
async function afterReadOtherCerts(file: any) {
  uploading.value = true
  try {
    const files = Array.isArray(file) ? file : [file]
    for (const item of files) {
      const url = await uploadImage(item.file)
      formData.other_certificates.push(url)
    }
    showToast('上传成功')
  }
  finally {
    uploading.value = false
  }
}

// 删除其他证书
function deleteOtherCert(file: UploaderFileListItem) {
  const index = otherCertsList.value.findIndex(item => item.url === file.url)
  if (index > -1) {
    formData.other_certificates.splice(index, 1)
  }
}

// 切换技能选择
function toggleSkill(skill: string) {
  const index = formData.skills.indexOf(skill)
  if (index > -1) {
    formData.skills.splice(index, 1)
  }
  else {
    formData.skills.push(skill)
  }
}

// 验证第一步
function validateStep1() {
  if (!formData.real_name) {
    showToast('请输入真实姓名')
    return false
  }
  if (!formData.id_card || formData.id_card.length !== 18) {
    showToast('请输入正确的身份证号')
    return false
  }
  if (!formData.age || Number(formData.age) < 18 || Number(formData.age) > 65) {
    showToast('年龄必须在18-65岁之间')
    return false
  }
  if (!formData.phone || formData.phone.length !== 11) {
    showToast('请输入正确的手机号')
    return false
  }
  if (!formData.address) {
    showToast('请输入居住地址')
    return false
  }
  return true
}

// 验证第二步
function validateStep2() {
  if (!formData.experience_years) {
    showToast('请输入工作年限')
    return false
  }
  const years = Number(formData.experience_years)
  if (years < 0 || years >= 50) {
    showToast('工作年限必须在0-49年之间')
    return false
  }
  if (formData.skills.length === 0) {
    showToast('请至少选择一项技能')
    return false
  }
  if (!formData.introduction || formData.introduction.length < 20) {
    showToast('个人简介不少于20字')
    return false
  }
  return true
}

// 下一步
function nextStep() {
  if (currentStep.value === 0 && !validateStep1()) {
    return
  }
  if (currentStep.value === 1 && !validateStep2()) {
    return
  }
  if (currentStep.value < 2) {
    currentStep.value++
  }
}

// 上一步
function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 提交申请
async function handleSubmit() {
  // 验证必填项
  if (!formData.real_name) {
    showToast('请输入真实姓名')
    return
  }
  if (!formData.id_card || formData.id_card.length !== 18) {
    showToast('请输入正确的身份证号')
    return
  }
  if (!formData.age || Number(formData.age) < 18 || Number(formData.age) > 65) {
    showToast('年龄必须在18-65岁之间')
    return
  }
  if (!formData.phone || formData.phone.length !== 11) {
    showToast('请输入正确的手机号')
    return
  }
  if (!formData.address) {
    showToast('请输入居住地址')
    return
  }
  if (!formData.experience_years) {
    showToast('请输入工作年限')
    return
  }
  if (formData.skills.length === 0) {
    showToast('请至少选择一项技能')
    return
  }
  if (!formData.introduction) {
    showToast('请填写个人简介')
    return
  }
  if (!formData.id_card_front) {
    showToast('请上传身份证正面')
    return
  }
  if (!formData.id_card_back) {
    showToast('请上传身份证反面')
    return
  }
  if (!formData.health_certificate) {
    showToast('请上传健康证')
    return
  }
  if (!formData.health_report) {
    showToast('请上传体检报告')
    return
  }
  if (!formData.practice_certificate) {
    showToast('请上传执业证书')
    return
  }

  // 确认提交
  await showDialog({
    title: '确认提交',
    message: '请确认信息无误后提交，提交后将进入审核流程',
  })

  loading.value = true
  try {
    const res = await apiWorker.applyWorker({
      ...formData,
      age: Number(formData.age),
      experience_years: Number(formData.experience_years),
    })

    if (res.code === 200) {
      showToast('申请提交成功')
      router.replace('/worker/application-status')
    }
  }
  catch (error: any) {
    showToast(error.message || '提交失败')
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="apply-page">
    <van-nav-bar
      title="申请成为家政阿姨"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    />

    <div class="content">
      <!-- 步骤进度条 -->
      <van-steps :active="currentStep" active-color="#FF9F43" class="steps">
        <van-step v-for="(step, index) in steps" :key="index">
          {{ step.text }}
        </van-step>
      </van-steps>

      <!-- 提示信息 -->
      <van-notice-bar
        left-icon="info-o"
        text="请如实填写以下信息，我们将在1-3个工作日内完成审核"
        class="notice"
      />

      <van-form @submit="handleSubmit">
        <!-- 第一步：基本信息 -->
        <div v-show="currentStep === 0" class="step-content">
          <div class="section">
            <van-cell-group inset>
              <van-field
                v-model="formData.real_name"
                label="真实姓名"
                placeholder="请输入真实姓名"
                required
                clearable
              />
              <van-field
                v-model="formData.id_card"
                label="身份证号"
                placeholder="请输入18位身份证号"
                maxlength="18"
                required
                clearable
              />
              <van-field
                v-model="formData.age"
                type="digit"
                label="年龄"
                placeholder="请输入年龄"
                required
                clearable
              />
              <van-field
                v-model="formData.phone"
                type="tel"
                label="联系电话"
                placeholder="请输入手机号"
                maxlength="11"
                required
                clearable
              />
              <van-field
                v-model="formData.address"
                label="居住地址"
                placeholder="请输入详细地址"
                required
                clearable
              />
            </van-cell-group>

            <!-- 性别选择 - 大按钮样式 -->
            <div class="gender-select">
              <div class="field-label">选择性别 *</div>
              <div class="gender-buttons">
                <div
                  class="gender-button"
                  :class="{ active: formData.gender === 'male' }"
                  @click="formData.gender = 'male'"
                >
                  <van-icon name="manager-o" size="32" />
                  <span>男</span>
                </div>
                <div
                  class="gender-button"
                  :class="{ active: formData.gender === 'female' }"
                  @click="formData.gender = 'female'"
                >
                  <van-icon name="friends-o" size="32" />
                  <span>女</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二步：技能经验 -->
        <div v-show="currentStep === 1" class="step-content">
          <div class="section">
            <van-cell-group inset>
              <van-field
                v-model="formData.experience_years"
                type="digit"
                label="工作年限"
                placeholder="请输入工作年限（0-49年）"
                required
                clearable
                maxlength="2"
              />
            </van-cell-group>

            <!-- 技能标签选择 -->
            <div class="skills-select">
              <div class="field-label">擅长技能 * <span class="tip">（可多选）</span></div>
              <div class="skills-grid">
                <div
                  v-for="skill in skillOptions"
                  :key="skill.value"
                  class="skill-tag"
                  :class="{ active: formData.skills.includes(skill.value) }"
                  @click="toggleSkill(skill.value)"
                >
                  <van-icon :name="skill.icon" size="20" />
                  <span>{{ skill.text }}</span>
                </div>
              </div>
            </div>

            <!-- 个人简介 -->
            <van-cell-group inset>
              <van-field
                v-model="formData.introduction"
                type="textarea"
                label="个人简介"
                placeholder="请介绍您的工作经验、特长等（不少于20字）"
                rows="6"
                maxlength="500"
                show-word-limit
                required
              />
            </van-cell-group>
          </div>
        </div>

        <!-- 第三步：实名认证 -->
        <div v-show="currentStep === 2" class="step-content">
          <div class="section">
            <div class="cert-section-title">
              <van-icon name="certificate" size="18" color="#FF9F43" />
              <span>身份证件</span>
              <span class="required-mark">*</span>
            </div>
            
            <!-- 身份证区域 -->
            <div class="idcard-section">
              <div class="idcard-item">
                <van-uploader
                  v-model="idCardFrontList"
                  :max-count="1"
                  :after-read="afterReadIdCardFront"
                  :disabled="uploading"
                  class="idcard-uploader"
                >
                  <template #default>
                    <div v-if="!formData.id_card_front" class="idcard-placeholder">
                      <van-icon name="user-circle-o" size="36" color="#DCDEE0" />
                      <div class="idcard-text">身份证人像面</div>
                      <div class="idcard-tip">点击上传</div>
                    </div>
                  </template>
                </van-uploader>
              </div>

              <div class="idcard-item">
                <van-uploader
                  v-model="idCardBackList"
                  :max-count="1"
                  :after-read="afterReadIdCardBack"
                  :disabled="uploading"
                  class="idcard-uploader"
                >
                  <template #default>
                    <div v-if="!formData.id_card_back" class="idcard-placeholder">
                      <van-icon name="shield-o" size="36" color="#DCDEE0" />
                      <div class="idcard-text">身份证国徽面</div>
                      <div class="idcard-tip">点击上传</div>
                    </div>
                  </template>
                </van-uploader>
              </div>
            </div>

            <div class="cert-section-title">
              <van-icon name="medal-o" size="18" color="#FF9F43" />
              <span>资质证书</span>
              <span class="required-mark">*</span>
            </div>

            <!-- 其他证书网格 -->
            <div class="cert-grid">
              <!-- 健康证 -->
              <div class="cert-item">
                <van-uploader
                  v-model="healthCertList"
                  :max-count="1"
                  :after-read="afterReadHealthCert"
                  :disabled="uploading"
                  class="cert-uploader"
                >
                  <template #default>
                    <div v-if="!formData.health_certificate" class="cert-placeholder">
                      <van-icon name="like-o" size="32" color="#DCDEE0" />
                      <div class="cert-text">健康证</div>
                      <div class="cert-required">必填</div>
                    </div>
                  </template>
                </van-uploader>
              </div>

              <!-- 体检报告 -->
              <div class="cert-item">
                <van-uploader
                  v-model="healthReportList"
                  :max-count="1"
                  :after-read="afterReadHealthReport"
                  :disabled="uploading"
                  class="cert-uploader"
                >
                  <template #default>
                    <div v-if="!formData.health_report" class="cert-placeholder">
                      <van-icon name="records" size="32" color="#DCDEE0" />
                      <div class="cert-text">体检报告</div>
                      <div class="cert-required">必填</div>
                    </div>
                  </template>
                </van-uploader>
              </div>

              <!-- 执业证书 -->
              <div class="cert-item">
                <van-uploader
                  v-model="practiceCertList"
                  :max-count="1"
                  :after-read="afterReadPracticeCert"
                  :disabled="uploading"
                  class="cert-uploader"
                >
                  <template #default>
                    <div v-if="!formData.practice_certificate" class="cert-placeholder">
                      <van-icon name="award-o" size="32" color="#DCDEE0" />
                      <div class="cert-text">执业证书</div>
                      <div class="cert-required">必填</div>
                    </div>
                  </template>
                </van-uploader>
              </div>

              <!-- 其他证书 -->
              <div class="cert-item">
                <van-uploader
                  v-model="otherCertsList"
                  :max-count="5"
                  multiple
                  :after-read="afterReadOtherCerts"
                  :before-delete="deleteOtherCert"
                  :disabled="uploading"
                  class="cert-uploader"
                >
                  <template #default>
                    <div v-if="otherCertsList.length === 0" class="cert-placeholder">
                      <van-icon name="plus" size="32" color="#DCDEE0" />
                      <div class="cert-text">其他证书</div>
                      <div class="cert-optional">选填</div>
                    </div>
                  </template>
                </van-uploader>
              </div>
            </div>

            <div class="upload-tips">
              <van-icon name="info-o" size="14" color="#999" />
              <span>请确保证件照片清晰完整，支持JPG、PNG格式</span>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="button-section">
          <van-button
            v-if="currentStep > 0"
            round
            block
            plain
            @click="prevStep"
            class="prev-btn"
          >
            上一步
          </van-button>

          <van-button
            v-if="currentStep < 2"
            round
            block
            type="primary"
            @click="nextStep"
            class="next-btn"
          >
            下一步
          </van-button>

          <van-button
            v-if="currentStep === 2"
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            :disabled="uploading"
            class="submit-btn"
          >
            {{ uploading ? '上传中...' : '提交申请' }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<style scoped lang="scss">
.apply-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-bar {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);

  :deep(.van-nav-bar__title) {
    color: #fff;
  }

  :deep(.van-icon) {
    color: #fff;
  }
}

.content {
  padding-bottom: 20px;
}

.steps {
  margin: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
}

.notice {
  margin: 12px;
  border-radius: 8px;
}

.step-content {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.section {
  margin-top: 16px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    font-size: 16px;
    font-weight: bold;
    color: #333;

    .van-icon {
      color: #FF6B6B;
      font-size: 18px;
    }
  }

  :deep(.van-cell-group) {
    margin: 0 12px;
    border-radius: 12px;
    overflow: hidden;
  }

  :deep(.van-field__label) {
    width: 90px;
    color: #666;
  }

  :deep(.van-checkbox-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  :deep(.van-checkbox) {
    margin-right: 0;
  }

  :deep(.van-radio-group) {
    display: flex;
    gap: 24px;
  }

  :deep(.van-uploader) {
    .van-button {
      background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
      border: none;
    }
  }
}

// 性别选择
.gender-select {
  margin: 16px 12px;

  .field-label {
    font-size: 14px;
    color: #666;
    margin-bottom: 12px;
    padding-left: 4px;
  }

  .gender-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;

    .gender-button {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 24px;
      background: #F7F8FA;
      border-radius: 12px;
      border: 2px solid transparent;
      cursor: pointer;
      transition: all 0.3s;

      span {
        font-size: 16px;
        color: #666;
        font-weight: 500;
      }

      &.active {
        background: #FFF5E6;
        border-color: #FF9F43;

        :deep(.van-icon) {
          color: #FF9F43;
        }

        span {
          color: #FF9F43;
        }
      }
    }
  }
}

// 技能选择
.skills-select {
  margin: 16px 12px;

  .field-label {
    font-size: 14px;
    color: #666;
    margin-bottom: 12px;
    padding-left: 4px;

    .tip {
      font-size: 12px;
      color: #999;
    }
  }

  .skills-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;

    .skill-tag {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 16px 8px;
      background: #F7F8FA;
      border-radius: 8px;
      border: 2px solid transparent;
      cursor: pointer;
      transition: all 0.3s;

      span {
        font-size: 14px;
        color: #666;
      }

      :deep(.van-icon) {
        color: #999;
      }

      &.active {
        background: #FF9F43;
        border-color: #FF9F43;

        span {
          color: #fff;
        }

        :deep(.van-icon) {
          color: #fff;
        }
      }
    }
  }
}

// 证件区域标题
.cert-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 16px 12px;
  font-size: 15px;
  font-weight: bold;
  color: #333;

  .required-mark {
    color: #EE0A24;
    font-size: 14px;
  }
}

// 身份证区域
.idcard-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 16px 20px;

  .idcard-item {
    .idcard-uploader {
      :deep(.van-uploader__wrapper) {
        width: 100%;
        display: block;
      }

      :deep(.van-uploader__upload) {
        width: 100%;
        height: 100px;
        margin: 0;
        padding: 0;
        background: #F7F8FA;
        border-radius: 8px;
        border: 2px dashed #DCDEE0;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;

        &:active {
          background: #EBEDF0;
          border-color: #FF9F43;
        }
      }

      :deep(.van-uploader__preview) {
        width: 100%;
        height: 100px;
        margin: 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        border: 2px solid #E8E8E8;
      }

      :deep(.van-uploader__preview-image) {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      :deep(.van-uploader__preview-delete) {
        width: 22px;
        height: 22px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        .van-icon {
          font-size: 12px;
        }
      }

      .idcard-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 12px;

        .idcard-text {
          font-size: 13px;
          color: #666;
          font-weight: 500;
        }

        .idcard-tip {
          font-size: 11px;
          color: #999;
        }
      }
    }
  }
}

// 其他证书网格
.cert-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 16px 16px;

  .cert-item {
    .cert-uploader {
      :deep(.van-uploader__wrapper) {
        width: 100%;
        display: block;
      }

      :deep(.van-uploader__upload) {
        width: 100%;
        height: 120px;
        margin: 0;
        padding: 0;
        background: #F7F8FA;
        border-radius: 8px;
        border: 2px dashed #DCDEE0;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;

        &:active {
          background: #EBEDF0;
          border-color: #FF9F43;
        }
      }

      :deep(.van-uploader__preview) {
        width: 100%;
        height: 120px;
        margin: 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        border: 2px solid #E8E8E8;
      }

      :deep(.van-uploader__preview-image) {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      :deep(.van-uploader__preview-delete) {
        width: 22px;
        height: 22px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        .van-icon {
          font-size: 12px;
        }
      }

      .cert-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 12px;

        .cert-text {
          font-size: 13px;
          color: #666;
          font-weight: 500;
        }

        .cert-required {
          font-size: 11px;
          color: #FF9F43;
        }

        .cert-optional {
          font-size: 11px;
          color: #999;
        }
      }
    }
  }
}

// 上传提示
.upload-tips {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  margin: 0 16px;
  background: #FFF7E6;
  border-radius: 8px;
  font-size: 12px;
  color: #999;
  line-height: 1.5;
}

// 底部按钮
.button-section {
  padding: 24px 16px;
  display: flex;
  gap: 12px;

  .prev-btn {
    flex: 1;
    height: 48px;
    font-size: 16px;
    background: #fff;
    border: 1px solid #DCDEE0;
    color: #666;

    &:active {
      background: #F7F8FA;
    }
  }

  .next-btn,
  .submit-btn {
    flex: 1;
    height: 48px;
    font-size: 16px;
    font-weight: bold;
    background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(255, 159, 67, 0.3);

    &:active {
      opacity: 0.8;
    }
  }
}
</style>
