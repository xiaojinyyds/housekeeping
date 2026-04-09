<script setup lang="ts">
import { showToast, showImagePreview, showConfirmDialog } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'application-status',
  meta: {
    title: '申请状态',
    auth: true,
  },
})

const router = useRouter()

const loading = ref(false)
const application = ref<any>(null)
const collapseActive = ref<string[]>([])

// 状态文本映射
const statusMap = {
  pending: {
    text: '审核中',
    type: 'warning',
    icon: 'clock-o',
    color: '#FF9F43',
    desc: '预计 1-3 个工作日内完成，请留意短信通知',
    step: 1,
  },
  approved: {
    text: '审核通过',
    type: 'success',
    icon: 'checked',
    color: '#07C160',
    desc: '恭喜您！已成功成为家政阿姨',
    step: 2,
  },
  rejected: {
    text: '审核未通过',
    type: 'danger',
    icon: 'close',
    color: '#EE0A24',
    desc: '很抱歉，您的申请未通过审核',
    step: 1,
  },
}

// 获取申请信息
async function getApplication() {
  loading.value = true
  try {
    const res = await apiWorker.getMyApplication()
    if (res.code === 200) {
      application.value = res.data
    }
  }
  catch (error: any) {
    showToast(error.message || '获取失败')
  }
  finally {
    loading.value = false
  }
}

// 身份证脱敏
function maskIdCard(idCard: string) {
  if (!idCard || idCard.length < 18)
    return idCard
  return `${idCard.substring(0, 6)}********${idCard.substring(14)}`
}

// 预览图片
function previewImage(url: string) {
  showImagePreview({
    images: [url],
    closeable: true,
  })
}

// 预览所有证件
function previewAllCerts() {
  const images = [
    application.value.id_card_front,
    application.value.id_card_back,
    application.value.health_certificate,
    application.value.health_report,
    application.value.practice_certificate,
    ...(application.value.other_certificates || []),
  ].filter(Boolean)

  showImagePreview({
    images,
    closeable: true,
  })
}

// 修改申请
async function editApplication() {
  if (application.value.status !== 'pending') {
    showToast('只有待审核的申请可以修改')
    return
  }

  try {
    await showConfirmDialog({
      title: '修改申请',
      message: '修改后需要重新提交审核，确定要修改吗？',
    })
    // TODO: 跳转到编辑页面，需要传递申请ID
    router.push(`/worker/apply?edit=${application.value.id}`)
  }
  catch {
    // 取消
  }
}

// 重新申请
async function reApply() {
  try {
    await showConfirmDialog({
      title: '重新申请',
      message: '将清空当前申请记录，确定要重新申请吗？',
    })
    router.replace('/worker/apply')
  }
  catch {
    // 取消
  }
}

// 查看档案
function goProfile() {
  router.push('/worker/profile')
}

// 联系客服
function contactService() {
  showToast('客服功能开发中')
}

onMounted(() => {
  getApplication()
})
</script>

<template>
  <div class="application-status-page">
    <van-nav-bar
      title="申请状态"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    />

    <van-loading v-if="loading" class="loading" vertical>
      加载中...
    </van-loading>

    <div v-else-if="application" class="content">
      <!-- 头部状态区 -->
      <div
        class="status-header"
        :style="{ background: `linear-gradient(135deg, ${statusMap[application.status as keyof typeof statusMap].color} 0%, ${statusMap[application.status as keyof typeof statusMap].color}CC 100%)` }"
      >
        <van-icon
          :name="statusMap[application.status as keyof typeof statusMap].icon"
          size="64"
          color="#fff"
          class="status-icon"
        />
        <div class="status-title">
          {{ statusMap[application.status as keyof typeof statusMap].text }}
        </div>
        <div class="status-subtitle">
          {{ statusMap[application.status as keyof typeof statusMap].desc }}
        </div>

        <!-- 拒绝原因 -->
        <div v-if="application.status === 'rejected' && application.reject_reason" class="reject-box">
          <van-icon name="warning-o" size="16" />
          <span>{{ application.reject_reason }}</span>
        </div>
      </div>

      <!-- 进度时间线 -->
      <div class="timeline-section">
        <van-steps
          direction="vertical"
          :active="statusMap[application.status as keyof typeof statusMap].step"
          active-color="#FF9F43"
          inactive-color="#DCDEE0"
        >
          <van-step>
            <template #inactive-icon>
              <van-icon name="edit" size="20" />
            </template>
            <template #active-icon>
              <van-icon name="success" size="20" color="#FF9F43" />
            </template>
            <template #finish-icon>
              <van-icon name="success" size="20" color="#FF9F43" />
            </template>
            <h3>提交申请</h3>
            <p>{{ new Date(application.created_at).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }}</p>
          </van-step>

          <van-step>
            <template #inactive-icon>
              <van-icon name="clock-o" size="20" />
            </template>
            <template #active-icon>
              <van-icon name="clock-o" size="20" color="#FF9F43" />
            </template>
            <template #finish-icon>
              <van-icon name="success" size="20" color="#FF9F43" />
            </template>
            <h3>平台审核</h3>
            <p v-if="application.status === 'pending'">
              审核中，请耐心等待
            </p>
            <p v-else-if="application.reviewed_at">
              {{ new Date(application.reviewed_at).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }}
            </p>
            <p v-else>
              等待审核
            </p>
          </van-step>

          <van-step>
            <template #inactive-icon>
              <van-icon name="smile-o" size="20" />
            </template>
            <template #active-icon>
              <van-icon name="success" size="20" color="#07C160" />
            </template>
            <template #finish-icon>
              <van-icon name="success" size="20" color="#07C160" />
            </template>
            <h3>成为家政阿姨</h3>
            <p v-if="application.status === 'approved'">
              审核通过，开始接单
            </p>
            <p v-else>
              等待审核通过
            </p>
          </van-step>
        </van-steps>
      </div>

      <!-- 申请详情折叠卡片 -->
      <div class="detail-section">
        <van-collapse v-model="collapseActive" accordion>
          <van-collapse-item name="detail">
            <template #title>
              <div class="collapse-title">
                <van-icon name="description" size="18" color="#FF9F43" />
                <span>查看申请详情</span>
              </div>
            </template>

            <!-- 基本信息 -->
            <div class="info-group">
              <div class="group-title">基本信息</div>
              <van-cell-group inset>
                <van-cell title="真实姓名" :value="application.real_name" />
                <van-cell title="身份证号" :value="maskIdCard(application.id_card)" />
                <van-cell title="年龄" :value="`${application.age}岁`" />
                <van-cell title="性别" :value="application.gender === 'female' ? '女' : '男'" />
                <van-cell title="联系电话" :value="application.phone" />
                <van-cell title="居住地址" :value="application.address" />
              </van-cell-group>
            </div>

            <!-- 工作信息 -->
            <div class="info-group">
              <div class="group-title">工作信息</div>
              <van-cell-group inset>
                <van-cell title="工作年限" :value="`${application.experience_years}年`" />
                <van-cell title="擅长技能">
                  <template #value>
                    <div class="skills-tags">
                      <van-tag
                        v-for="skill in application.skills"
                        :key="skill"
                        plain
                        color="#FF9F43"
                        size="medium"
                      >
                        {{ skill }}
                      </van-tag>
                    </div>
                  </template>
                </van-cell>
              </van-cell-group>
            </div>

            <!-- 个人简介 -->
            <div class="info-group">
              <div class="group-title">个人简介</div>
              <van-cell-group inset>
                <van-cell>
                  <div class="introduction">
                    {{ application.introduction }}
                  </div>
                </van-cell>
              </van-cell-group>
            </div>

            <!-- 证件照片 -->
            <div class="info-group">
              <div class="group-title">
                证件照片
                <span class="view-all" @click="previewAllCerts">查看全部</span>
              </div>
              <div class="cert-grid">
                <div class="cert-item" @click="previewImage(application.id_card_front)">
                  <van-image
                    :src="application.id_card_front"
                    fit="cover"
                    class="cert-image"
                  >
                    <template #loading>
                      <van-loading type="spinner" size="20" />
                    </template>
                  </van-image>
                  <div class="cert-label">身份证人像面</div>
                </div>

                <div class="cert-item" @click="previewImage(application.id_card_back)">
                  <van-image
                    :src="application.id_card_back"
                    fit="cover"
                    class="cert-image"
                  >
                    <template #loading>
                      <van-loading type="spinner" size="20" />
                    </template>
                  </van-image>
                  <div class="cert-label">身份证国徽面</div>
                </div>

                <div class="cert-item" @click="previewImage(application.health_certificate)">
                  <van-image
                    :src="application.health_certificate"
                    fit="cover"
                    class="cert-image"
                  >
                    <template #loading>
                      <van-loading type="spinner" size="20" />
                    </template>
                  </van-image>
                  <div class="cert-label">健康证</div>
                </div>

                <div class="cert-item" @click="previewImage(application.health_report)">
                  <van-image
                    :src="application.health_report"
                    fit="cover"
                    class="cert-image"
                  >
                    <template #loading>
                      <van-loading type="spinner" size="20" />
                    </template>
                  </van-image>
                  <div class="cert-label">体检报告</div>
                </div>

                <div class="cert-item" @click="previewImage(application.practice_certificate)">
                  <van-image
                    :src="application.practice_certificate"
                    fit="cover"
                    class="cert-image"
                  >
                    <template #loading>
                      <van-loading type="spinner" size="20" />
                    </template>
                  </van-image>
                  <div class="cert-label">执业证书</div>
                </div>

                <div
                  v-for="(cert, index) in application.other_certificates"
                  :key="index"
                  class="cert-item"
                  @click="previewImage(cert)"
                >
                  <van-image
                    :src="cert"
                    fit="cover"
                    class="cert-image"
                  >
                    <template #loading>
                      <van-loading type="spinner" size="20" />
                    </template>
                  </van-image>
                  <div class="cert-label">其他证书{{ index + 1 }}</div>
                </div>
              </div>
            </div>
          </van-collapse-item>
        </van-collapse>
      </div>

      <!-- 底部操作区 -->
      <div class="action-section">
        <van-button
          v-if="application.status === 'pending'"
          block
          round
          plain
          type="primary"
          @click="editApplication"
          class="action-btn"
        >
          修改申请
        </van-button>

        <van-button
          v-if="application.status === 'rejected'"
          block
          round
          type="primary"
          @click="reApply"
          class="action-btn"
        >
          重新申请
        </van-button>

        <van-button
          v-if="application.status === 'approved'"
          block
          round
          type="primary"
          @click="goProfile"
          class="action-btn"
        >
          查看我的档案
        </van-button>

        <van-button
          block
          plain
          round
          @click="contactService"
          class="contact-btn"
        >
          <van-icon name="service-o" />
          联系客服
        </van-button>
      </div>
    </div>

    <van-empty v-else description="暂无申请记录" />
  </div>
</template>

<style scoped lang="scss">
.application-status-page {
  min-height: 100vh;
  background: #F7F8FA;
  padding-bottom: 20px;
}

.nav-bar {
  :deep(.van-nav-bar__title) {
    color: #333;
  }
}

.loading {
  padding: 100px 0;
  text-align: center;
}

.content {
  position: relative;
}

// 头部状态区
.status-header {
  padding: 40px 20px 32px;
  text-align: center;
  color: #fff;
  position: relative;

  .status-icon {
    margin-bottom: 16px;
    animation: pulse 2s ease-in-out infinite;
  }

  .status-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 8px;
  }

  .status-subtitle {
    font-size: 14px;
    opacity: 0.9;
    line-height: 1.6;
  }

  .reject-box {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin-top: 16px;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    font-size: 13px;
    backdrop-filter: blur(10px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

// 进度时间线
.timeline-section {
  margin: -20px 16px 16px;
  padding: 24px 20px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

  :deep(.van-step) {
    padding-bottom: 24px;

    &:last-child {
      padding-bottom: 0;
    }
  }

  :deep(.van-step__title) {
    h3 {
      font-size: 16px;
      font-weight: bold;
      color: #333;
      margin: 0 0 4px 0;
    }

    p {
      font-size: 13px;
      color: #999;
      margin: 0;
    }
  }

  :deep(.van-step__circle-container) {
    background: #fff;
    padding: 4px;
  }
}

// 申请详情折叠卡片
.detail-section {
  margin: 0 16px 16px;

  :deep(.van-collapse) {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }

  :deep(.van-collapse-item__title) {
    padding: 16px;
    background: #fff;
  }

  :deep(.van-collapse-item__content) {
    padding: 0 0 16px;
    background: #F7F8FA;
  }

  .collapse-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 500;
    color: #333;
  }
}

// 信息组
.info-group {
  margin-bottom: 16px;

  .group-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    font-weight: bold;
    color: #333;
    padding: 12px 16px 8px;

    .view-all {
      font-size: 13px;
      font-weight: normal;
      color: #FF9F43;
      cursor: pointer;

      &:active {
        opacity: 0.7;
      }
    }
  }

  :deep(.van-cell-group) {
    margin: 0 12px;
    border-radius: 12px;
    overflow: hidden;
  }

  :deep(.van-cell) {
    font-size: 14px;

    .van-cell__title {
      color: #666;
    }

    .van-cell__value {
      color: #333;
    }
  }

  .skills-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: flex-end;
  }

  .introduction {
    font-size: 14px;
    color: #666;
    line-height: 1.8;
    padding: 8px 0;
    word-break: break-all;
  }
}

// 证件网格
.cert-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 0 16px;

  .cert-item {
    cursor: pointer;
    transition: transform 0.2s;

    &:active {
      transform: scale(0.95);
    }

    .cert-image {
      width: 100%;
      height: 100px;
      border-radius: 8px;
      overflow: hidden;
      background: #F7F8FA;
      border: 1px solid #EBEDF0;
    }

    .cert-label {
      font-size: 12px;
      color: #666;
      text-align: center;
      margin-top: 6px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

// 底部操作区
.action-section {
  padding: 0 16px;
  margin-top: 16px;

  .action-btn {
    height: 48px;
    font-size: 16px;
    font-weight: bold;
    background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(255, 159, 67, 0.3);
    margin-bottom: 12px;

    &:active {
      opacity: 0.8;
    }
  }

  .contact-btn {
    height: 44px;
    font-size: 15px;
    color: #666;
    border-color: #DCDEE0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;

    &:active {
      background: #F7F8FA;
    }
  }
}
</style>
