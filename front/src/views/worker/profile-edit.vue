<script setup lang="ts">
import { showToast, showLoadingToast, closeToast } from 'vant'
import { areaList } from '@vant/area-data'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'worker-profile-edit',
  meta: {
    title: '编辑资料',
  },
})

const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const profile = ref<any>(null)

// 表单数据
const formData = ref({
  phone: '',
  address: '',
  skills: [] as string[],
  introduction: '',
  service_areas: [] as string[], // 存储格式: ["北京市/北京市/朝阳区", ...]
  hourly_rate: 0,
})

// 可选技能列表
const availableSkills = [
  '保洁', '月嫂', '育儿', '护理', '烹饪', '陪护', '维修', '洗衣',
  '收纳整理', '开荒保洁', '深度保洁', '家电清洗', '擦玻璃',
]

const showSkillPicker = ref(false)
const showAreaPicker = ref(false)

// 获取数据
async function fetchData() {
  loading.value = true
  try {
    const res: any = await apiWorker.getMyProfile()
    if (res.code === 200) {
      profile.value = res.data
      // 填充表单
      formData.value = {
        phone: res.data.phone || '',
        address: res.data.address || '',
        skills: res.data.skills || [],
        introduction: res.data.introduction || '',
        service_areas: res.data.service_areas || [],
        hourly_rate: res.data.hourly_rate || 0,
      }
    }
  }
  catch (error: any) {
    console.error('获取档案失败:', error)
    if (error.response?.status === 403 || error.response?.status === 404) {
      showToast('您不是家政阿姨')
      router.back()
    }
  }
  finally {
    loading.value = false
  }
}

// 切换技能
function toggleSkill(skill: string) {
  const index = formData.value.skills.indexOf(skill)
  if (index > -1) {
    formData.value.skills.splice(index, 1)
  }
  else {
    formData.value.skills.push(skill)
  }
}

// 省市区选择确认
function onAreaConfirm({ selectedOptions }: { selectedOptions: any[] }) {
  if (selectedOptions && selectedOptions.length === 3) {
    const areaText = selectedOptions.map(opt => opt.text).join('/')
    // 避免重复添加
    if (!formData.value.service_areas.includes(areaText)) {
      formData.value.service_areas.push(areaText)
    }
    else {
      showToast('该区域已添加')
    }
  }
  showAreaPicker.value = false
}

// 移除区域
function removeArea(area: string) {
  const index = formData.value.service_areas.indexOf(area)
  if (index > -1) {
    formData.value.service_areas.splice(index, 1)
  }
}

// 保存
async function saveProfile() {
  if (!formData.value.phone) {
    showToast('请输入联系电话')
    return
  }
  if (formData.value.skills.length === 0) {
    showToast('请至少选择一个技能')
    return
  }

  saving.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })

  try {
    const res: any = await apiWorker.updateMyProfile({
      phone: formData.value.phone,
      address: formData.value.address,
      skills: formData.value.skills,
      introduction: formData.value.introduction,
      service_areas: formData.value.service_areas,
      hourly_rate: formData.value.hourly_rate,
    })

    closeToast()

    if (res.code === 200) {
      showToast('保存成功')
      router.back()
    }
    else {
      showToast(res.message || '保存失败')
    }
  }
  catch (error) {
    closeToast()
    showToast('保存失败')
  }
  finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="profile-edit-page">
    <!-- 顶部导航 -->
    <van-nav-bar
      title="编辑资料"
      left-arrow
      @click-left="router.back()"
    />

    <van-loading v-if="loading" class="page-loading" />

    <template v-else>
      <!-- 基本信息（只读） -->
      <van-cell-group inset title="基本信息">
        <van-cell title="姓名" :value="profile?.real_name" />
        <van-cell title="性别" :value="profile?.gender === 'female' ? '女' : '男'" />
        <van-cell title="年龄" :value="`${profile?.age}岁`" />
        <van-cell title="工作年限" :value="`${profile?.experience_years}年`" />
      </van-cell-group>

      <!-- 联系方式 -->
      <van-cell-group inset title="联系方式">
        <van-field
          v-model="formData.phone"
          label="联系电话"
          placeholder="请输入联系电话"
          maxlength="11"
          type="tel"
        />
        <van-field
          v-model="formData.address"
          label="居住地址"
          placeholder="请输入居住地址"
          maxlength="100"
        />
      </van-cell-group>

      <!-- 技能标签 -->
      <van-cell-group inset title="技能标签">
        <div class="tags-section">
          <div class="selected-tags">
            <van-tag
              v-for="skill in formData.skills"
              :key="skill"
              closeable
              type="primary"
              size="medium"
              @close="toggleSkill(skill)"
            >
              {{ skill }}
            </van-tag>
            <van-tag
              v-if="formData.skills.length === 0"
              plain
              type="default"
            >
              请选择技能
            </van-tag>
          </div>
          <van-button
            size="small"
            plain
            icon="plus"
            @click="showSkillPicker = true"
          >
            添加技能
          </van-button>
        </div>
      </van-cell-group>

      <!-- 服务区域 -->
      <van-cell-group inset title="服务区域">
        <div class="tags-section">
          <div class="selected-tags">
            <van-tag
              v-for="area in formData.service_areas"
              :key="area"
              closeable
              type="success"
              size="medium"
              @close="removeArea(area)"
            >
              {{ area }}
            </van-tag>
            <van-tag
              v-if="formData.service_areas.length === 0"
              plain
              type="default"
            >
              请选择服务区域
            </van-tag>
          </div>
          <van-button
            size="small"
            plain
            icon="plus"
            @click="showAreaPicker = true"
          >
            添加区域
          </van-button>
        </div>
      </van-cell-group>

      <!-- 时薪设置 -->
      <van-cell-group inset title="收费标准">
        <van-field
          v-model.number="formData.hourly_rate"
          label="时薪"
          placeholder="请输入时薪"
          type="number"
        >
          <template #button>
            <span class="unit">元/小时</span>
          </template>
        </van-field>
      </van-cell-group>

      <!-- 个人简介 -->
      <van-cell-group inset title="个人简介">
        <van-field
          v-model="formData.introduction"
          type="textarea"
          placeholder="介绍一下您的工作经验和服务特点..."
          rows="4"
          maxlength="500"
          show-word-limit
        />
      </van-cell-group>

      <!-- 保存按钮 -->
      <div class="save-bar">
        <van-button
          type="primary"
          block
          round
          :loading="saving"
          color="#FF9F43"
          @click="saveProfile"
        >
          保存修改
        </van-button>
      </div>
    </template>

    <!-- 技能选择弹窗 -->
    <van-popup
      v-model:show="showSkillPicker"
      position="bottom"
      round
    >
      <div class="picker-popup">
        <div class="popup-header">
          <span class="title">选择技能</span>
          <van-icon name="cross" @click="showSkillPicker = false" />
        </div>
        <div class="picker-grid">
          <div
            v-for="skill in availableSkills"
            :key="skill"
            class="picker-item"
            :class="{ selected: formData.skills.includes(skill) }"
            @click="toggleSkill(skill)"
          >
            {{ skill }}
            <van-icon v-if="formData.skills.includes(skill)" name="success" class="check" />
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 省市区三级联动选择器 -->
    <van-popup
      v-model:show="showAreaPicker"
      position="bottom"
      round
    >
      <van-area
        title="选择服务区域"
        :area-list="areaList"
        @confirm="onAreaConfirm"
        @cancel="showAreaPicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped lang="scss">
.profile-edit-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 80px;
}

.page-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.tags-section {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

.unit {
  color: #999;
  font-size: 14px;
}

.save-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.picker-popup {
  padding: 16px;
  max-height: 60vh;
  overflow-y: auto;

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .title {
      font-size: 16px;
      font-weight: bold;
    }
  }

  .picker-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;

    .picker-item {
      position: relative;
      padding: 12px;
      text-align: center;
      background: #f5f5f5;
      border-radius: 8px;
      font-size: 14px;
      cursor: pointer;
      border: 2px solid transparent;

      &.selected {
        background: rgba(255, 159, 67, 0.1);
        border-color: #FF9F43;
        color: #FF9F43;
      }

      .check {
        position: absolute;
        top: 2px;
        right: 2px;
        font-size: 12px;
        color: #FF9F43;
      }
    }
  }
}
</style>
