<script setup lang="ts">
import { showToast, showDialog } from 'vant'
import type { UploaderFileListItem } from 'vant'
import apiAdmin from '@/api/modules/admin'
import apiUpload from '@/api/modules/upload'

definePage({
  name: 'admin-create-worker',
  meta: {
    title: '添加阿姨',
    auth: true,
  },
})

const router = useRouter()
const userStore = useUserStore()

// 检查权限
if (!userStore.isAdmin) {
  showToast('无权访问')
  router.replace('/')
}

const loading = ref(false)
const uploading = ref(false)

// 当前步骤 (0: 账号信息, 1: 基本信息, 2: 技能经验, 3: 实名认证)
const currentStep = ref(0)

// 步骤列表
const steps = [
  { text: '账号信息' },
  { text: '基本信息' },
  { text: '技能经验' },
  { text: '实名认证' },
]

// 表单数据
const formData = reactive({
  // 账号信息
  email: '',
  password: '',
  // 基本信息
  real_name: '',
  id_card: '',
  age: '',
  gender: 'female',
  address: '',
  phone: '',
  // 技能经验
  work_years: '',
  skills: [] as string[],
  introduction: '',
  // 证件
  id_card_front_url: '',
  id_card_back_url: '',
  health_certificate_url: '',
  other_certificates: '',
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

// 文件列表
const idCardFrontList = ref<UploaderFileListItem[]>([])
const idCardBackList = ref<UploaderFileListItem[]>([])
const healthCertList = ref<UploaderFileListItem[]>([])

// 上传图片
async function uploadImage(file: File): Promise<string> {
  try {
    const res: any = await apiUpload.uploadImage(file, 'certificates')
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
    formData.id_card_front_url = url
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
    formData.id_card_back_url = url
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
    formData.health_certificate_url = url
    showToast('上传成功')
  }
  finally {
    uploading.value = false
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

// 验证账号信息
function validateStep0() {
  if (!formData.email) {
    showToast('请输入邮箱')
    return false
  }
  if (!/^[\w.-]+@[\w.-]+\.\w+$/.test(formData.email)) {
    showToast('请输入正确的邮箱格式')
    return false
  }
  if (!formData.password) {
    showToast('请输入密码')
    return false
  }
  if (formData.password.length < 6) {
    showToast('密码至少6位')
    return false
  }
  return true
}

// 验证基本信息
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

// 验证技能经验
function validateStep2() {
  if (!formData.work_years) {
    showToast('请输入工作年限')
    return false
  }
  const years = Number(formData.work_years)
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
  if (currentStep.value === 0 && !validateStep0()) return
  if (currentStep.value === 1 && !validateStep1()) return
  if (currentStep.value === 2 && !validateStep2()) return
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 上一步
function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 提交
async function handleSubmit() {
  // 验证证件
  if (!formData.id_card_front_url) {
    showToast('请上传身份证正面')
    return
  }
  if (!formData.id_card_back_url) {
    showToast('请上传身份证反面')
    return
  }
  if (!formData.health_certificate_url) {
    showToast('请上传健康证')
    return
  }

  // 确认提交
  await showDialog({
    title: '确认创建',
    message: '确定要创建该阿姨档案吗？',
  })

  loading.value = true
  try {
    const res: any = await apiAdmin.createWorker({
      email: formData.email,
      password: formData.password,
      real_name: formData.real_name,
      phone: formData.phone,
      id_card: formData.id_card,
      gender: formData.gender,
      age: Number(formData.age),
      address: formData.address,
      work_years: Number(formData.work_years),
      skills: formData.skills,
      introduction: formData.introduction,
      health_certificate_url: formData.health_certificate_url,
      id_card_front_url: formData.id_card_front_url,
      id_card_back_url: formData.id_card_back_url,
      other_certificates: formData.other_certificates,
    })

    if (res.code === 200) {
      showToast('创建成功')
      router.back()
    }
  }
  catch (error: any) {
    showToast(error.message || '创建失败')
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="create-worker-page">
    <van-nav-bar
      title="添加阿姨"
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

      <van-form @submit="handleSubmit">
        <!-- 第0步：账号信息 -->
        <div v-show="currentStep === 0" class="step-content">
          <div class="section">
            <div class="section-title">
              <van-icon name="user-o" />
              <span>账号信息</span>
            </div>
            <van-cell-group inset>
              <van-field
                v-model="formData.email"
                label="登录邮箱"
                placeholder="请输入邮箱"
                required
                clearable
              />
              <van-field
                v-model="formData.password"
                type="password"
                label="登录密码"
                placeholder="请输入密码（至少6位）"
                required
                clearable
              />
            </van-cell-group>
            <div class="tips">
              <van-icon name="info-o" />
              <span>此账号将用于阿姨登录系统</span>
            </div>
          </div>
        </div>

        <!-- 第1步：基本信息 -->
        <div v-show="currentStep === 1" class="step-content">
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
                placeholder="请输入年龄（18-65）"
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

            <!-- 性别选择 -->
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

        <!-- 第2步：技能经验 -->
        <div v-show="currentStep === 2" class="step-content">
          <div class="section">
            <van-cell-group inset>
              <van-field
                v-model="formData.work_years"
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
                placeholder="请介绍工作经验、特长等（不少于20字）"
                rows="5"
                maxlength="500"
                show-word-limit
                required
              />
            </van-cell-group>
          </div>
        </div>

        <!-- 第3步：实名认证 -->
        <div v-show="currentStep === 3" class="step-content">
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
                    <div v-if="!formData.id_card_front_url" class="idcard-placeholder">
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
                    <div v-if="!formData.id_card_back_url" class="idcard-placeholder">
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
              <span>健康证</span>
              <span class="required-mark">*</span>
            </div>

            <!-- 健康证 -->
            <div class="cert-single">
              <van-uploader
                v-model="healthCertList"
                :max-count="1"
                :after-read="afterReadHealthCert"
                :disabled="uploading"
                class="cert-uploader"
              >
                <template #default>
                  <div v-if="!formData.health_certificate_url" class="cert-placeholder">
                    <van-icon name="like-o" size="40" color="#DCDEE0" />
                    <div class="cert-text">点击上传健康证</div>
                  </div>
                </template>
              </van-uploader>
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
            v-if="currentStep < 3"
            round
            block
            type="primary"
            @click="nextStep"
            class="next-btn"
          >
            下一步
          </van-button>

          <van-button
            v-if="currentStep === 3"
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            :disabled="uploading"
            class="submit-btn"
          >
            {{ uploading ? '上传中...' : '确认创建' }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>


<style scoped lang="scss">
.create-worker-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-bar {
  background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);

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

  :deep(.van-step__title) {
    font-size: 12px;
  }
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
      color: #FF9F43;
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
}

.tips {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  margin: 12px 12px 0;
  background: #FFF7E6;
  border-radius: 8px;
  font-size: 13px;
  color: #FF9F43;
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

// 健康证单独上传
.cert-single {
  padding: 0 16px 16px;

  .cert-uploader {
    :deep(.van-uploader__wrapper) {
      width: 100%;
      display: block;
    }

    :deep(.van-uploader__upload) {
      width: 100%;
      height: 140px;
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
      height: 140px;
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

    .cert-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 12px;

      .cert-text {
        font-size: 14px;
        color: #666;
        font-weight: 500;
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
