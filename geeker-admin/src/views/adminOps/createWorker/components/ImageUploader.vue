<template>
  <div class="image-uploader">
    <el-upload
      action="#"
      :show-file-list="false"
      :http-request="handleUpload"
      :before-upload="beforeUpload"
      :disabled="loading || disabled"
      class="uploader"
    >
      <div v-if="modelValue" class="preview">
        <img :src="modelValue" alt="图片预览" class="preview-image" />
        <div class="mask">
          <span>点击更换</span>
        </div>
      </div>
      <div v-else class="empty">
        <el-icon class="empty-icon"><Plus /></el-icon>
        <span>{{ loading ? "上传中..." : "点击上传" }}</span>
      </div>
    </el-upload>
    <div class="actions" v-if="modelValue">
      <el-button text type="primary" @click="previewVisible = true">预览</el-button>
      <el-button text type="danger" @click="clearImage">删除</el-button>
    </div>
    <div class="tip">{{ tip }}</div>
    <el-image-viewer v-if="previewVisible" :url-list="[modelValue]" @close="previewVisible = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElImageViewer, ElMessage } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import type { UploadProps, UploadRequestOptions } from "element-plus";
import { uploadBusinessImageApi } from "@/api/modules/business";

const props = withDefaults(
  defineProps<{
    modelValue: string;
    folder?: string;
    tip?: string;
    disabled?: boolean;
  }>(),
  {
    modelValue: "",
    folder: "employee-certificates",
    tip: "支持 JPG、PNG、WEBP、GIF，大小不超过 10MB",
    disabled: false
  }
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const loading = ref(false);
const previewVisible = ref(false);

const beforeUpload: UploadProps["beforeUpload"] = file => {
  const isImage = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"].includes(file.type);
  const isValidSize = file.size / 1024 / 1024 < 10;

  if (!isImage) {
    ElMessage.warning("请上传 JPG、PNG、WEBP 或 GIF 图片");
    return false;
  }

  if (!isValidSize) {
    ElMessage.warning("图片大小不能超过 10MB");
    return false;
  }

  return true;
};

const handleUpload = async (options: UploadRequestOptions) => {
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", options.file);
    const response = (await uploadBusinessImageApi(formData, props.folder)) as any;
    emit("update:modelValue", response.data.url);
    ElMessage.success("图片上传成功");
  } catch (error) {
    options.onError(error as any);
  } finally {
    loading.value = false;
  }
};

const clearImage = () => {
  emit("update:modelValue", "");
};
</script>

<style scoped lang="scss">
.image-uploader {
  width: 100%;
}

.uploader {
  width: 100%;
}

.uploader :deep(.el-upload) {
  width: 100%;
}

.preview,
.empty {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 120px;
  overflow: hidden;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.2s ease;
}

.preview:hover,
.empty:hover {
  border-color: var(--el-color-primary);
  background: #f5f7ff;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mask {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  background: rgba(0, 0, 0, 0.4);
  transition: opacity 0.2s ease;
}

.preview:hover .mask {
  opacity: 1;
}

.empty {
  flex-direction: column;
  gap: 10px;
  color: var(--el-text-color-secondary);
}

.empty-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  justify-content: center;
}

.tip {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 11px;
  line-height: 1.4;
  text-align: center;
}
</style>
