<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>阿姨档案详情</h2>
        <p>查看阿姨完整资料、服务信息和证件内容，便于管理员统一管理。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="router.push(`/worker/edit/${route.params.workerId}`)">编辑档案</el-button>
        <el-button @click="router.push('/worker/list')">返回列表</el-button>
      </div>
    </div>

    <template v-if="detail">
      <div class="grid two">
        <div class="card section-card">
          <div class="profile-top">
            <el-avatar :size="88" :src="detail.avatar_url || ''">{{ (detail.real_name || "阿").slice(0, 1) }}</el-avatar>
            <div class="profile-top-text">
              <strong>{{ detail.real_name || "-" }}</strong>
              <span>{{ detail.current_status_text }}</span>
            </div>
          </div>

          <div class="section-title">基础信息</div>
          <div class="info-grid">
            <div class="info-item"><label>姓名</label><span>{{ detail.real_name || "-" }}</span></div>
            <div class="info-item"><label>手机号</label><span>{{ detail.phone || "-" }}</span></div>
            <div class="info-item"><label>微信号</label><span>{{ detail.wechat || "-" }}</span></div>
            <div class="info-item"><label>身份证号</label><span>{{ detail.id_card || "-" }}</span></div>
            <div class="info-item"><label>性别</label><span>{{ detail.gender === "female" ? "女" : detail.gender === "male" ? "男" : "-" }}</span></div>
            <div class="info-item"><label>年龄</label><span>{{ detail.age || "-" }}</span></div>
            <div class="info-item"><label>从业年限</label><span>{{ detail.experience_years || 0 }} 年</span></div>
            <div class="info-item"><label>可驾驶</label><span>{{ detail.can_drive ? "是" : "否" }}</span></div>
            <div class="info-item"><label>紧急联系人</label><span>{{ detail.emergency_contact || "-" }}</span></div>
            <div class="info-item"><label>紧急联系电话</label><span>{{ detail.emergency_phone || "-" }}</span></div>
            <div class="info-item"><label>当前状态</label><el-tag :type="statusTypeMap[detail.current_status] || 'info'">{{ detail.current_status_text }}</el-tag></div>
            <div class="info-item"><label>可接单</label><el-tag :type="detail.is_available ? 'success' : 'info'">{{ detail.is_available ? "可接单" : "不可接单" }}</el-tag></div>
            <div class="info-item"><label>推荐状态</label><el-tag :type="detail.is_recommended ? 'warning' : 'info'">{{ detail.is_recommended ? "已推荐" : "未推荐" }}</el-tag></div>
            <div class="info-item"><label>时薪</label><span>{{ detail.hourly_rate ? `${detail.hourly_rate} 元/小时` : "-" }}</span></div>
            <div class="info-item"><label>期望薪资</label><span>{{ detail.expected_salary ? `${detail.expected_salary} 元` : "-" }}</span></div>
            <div class="info-item"><label>评分</label><span>{{ detail.rating ?? "-" }}</span></div>
            <div class="info-item"><label>总订单数</label><span>{{ detail.total_orders ?? 0 }}</span></div>
            <div class="info-item"><label>完成订单数</label><span>{{ detail.completed_orders ?? 0 }}</span></div>
            <div class="info-item"><label>最近跟进</label><span>{{ detail.latest_follow_up_at || "-" }}</span></div>
          </div>

          <div class="single-line"><label>居住地址</label><span>{{ detail.address || "-" }}</span></div>
          <div class="single-line"><label>个人介绍</label><span>{{ detail.introduction || "-" }}</span></div>
          <div class="single-line"><label>内部备注</label><span>{{ detail.internal_remark || "-" }}</span></div>
        </div>

        <div class="card section-card">
          <div class="section-title">服务信息</div>
          <div class="tag-block">
            <label>服务类型</label>
            <div class="tag-list">
              <el-tag v-for="jobType in detail.job_types || []" :key="jobType">{{ jobType }}</el-tag>
              <span v-if="!(detail.job_types || []).length" class="empty-text">暂无</span>
            </div>
          </div>
          <div class="tag-block">
            <label>专业技能</label>
            <div class="tag-list">
              <el-tag v-for="skill in detail.skills || []" :key="skill" effect="plain">{{ skill }}</el-tag>
              <span v-if="!(detail.skills || []).length" class="empty-text">暂无</span>
            </div>
          </div>
          <div class="tag-block">
            <label>服务区域</label>
            <div class="tag-list">
              <el-tag v-for="area in detail.service_areas || []" :key="area" type="success" effect="plain">{{ area }}</el-tag>
              <span v-if="!(detail.service_areas || []).length" class="empty-text">暂无</span>
            </div>
          </div>
          <div class="tag-block">
            <label>服务项目</label>
            <div class="service-list" v-if="(detail.services || []).length">
              <div v-for="service in detail.services" :key="service.id" class="service-item">
                <strong>{{ service.name }}</strong>
                <span>{{ service.price ? `${service.price} 元` : "-" }}</span>
              </div>
            </div>
            <span v-else class="empty-text">暂无</span>
          </div>
        </div>
      </div>

      <div class="card section-card">
        <div class="section-title">证件资料</div>
        <div class="certificate-grid">
          <div v-for="item in certificateItems" :key="item.label" class="certificate-item">
            <div class="certificate-label">{{ item.label }}</div>
            <el-image
              v-if="item.url"
              :src="item.url"
              fit="cover"
              class="certificate-image"
              :preview-src-list="previewImages"
              preview-teleported
            />
            <div v-else class="certificate-empty">未上传</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getWorkerDetailApi } from "@/api/modules/business";

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const detail = ref<Record<string, any> | null>(null);

const statusTextMap: Record<string, string> = {
  available: "可接单",
  on_job: "在岗中",
  paused: "暂停接单",
  blacklisted: "黑名单",
  inactive: "停用"
};

const statusTypeMap: Record<string, "info" | "warning" | "success" | "danger"> = {
  available: "success",
  on_job: "warning",
  paused: "info",
  blacklisted: "danger",
  inactive: "info"
};

const certificateItems = computed(() => {
  const data = detail.value || {};
  const otherCertificates = Array.isArray(data.other_certificates) ? data.other_certificates : [];
  return [
    { label: "身份证人像面", url: data.id_card_front },
    { label: "身份证国徽面", url: data.id_card_back },
    { label: "健康证", url: data.health_certificate },
    { label: "体检报告", url: data.health_report },
    { label: "上岗证", url: data.practice_certificate },
    ...otherCertificates.map((url: string, index: number) => ({ label: `其他证书${index + 1}`, url }))
  ];
});

const previewImages = computed(() => certificateItems.value.map(item => item.url).filter(Boolean));

const loadDetail = async () => {
  const workerId = String(route.params.workerId || "");
  if (!workerId) return;
  loading.value = true;
  try {
    const response = (await getWorkerDetailApi(workerId)) as any;
    const data = response?.data ?? response ?? null;
    if (data) {
      data.current_status_text = statusTextMap[data.current_status] || data.current_status || "-";
    }
    detail.value = data;
  } catch {
    detail.value = null;
    ElMessage.error("获取阿姨详情失败");
  } finally {
    loading.value = false;
  }
};

watch(() => [route.params.workerId, route.query.refresh], loadDetail);
onMounted(loadDetail);
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.grid.two {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.header-card,
.section-card {
  padding: 20px;
}

.header-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.section-title {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 700;
}

.profile-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.profile-top-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.profile-top-text strong {
  font-size: 20px;
}

.profile-top-text span {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 18px;
}

.info-item,
.single-line,
.tag-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label,
.single-line label,
.tag-block label,
.certificate-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.single-line {
  margin-top: 16px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.service-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.service-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f7f9fb;
}

.certificate-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.certificate-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.certificate-image,
.certificate-empty {
  width: 100%;
  height: 180px;
  border-radius: 14px;
  border: 1px solid var(--el-border-color-light);
  background: #f7f9fb;
}

.certificate-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
}

.empty-text {
  color: var(--el-text-color-secondary);
}

@media (max-width: 1200px) {
  .grid.two,
  .certificate-grid,
  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-card,
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
