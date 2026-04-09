#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文件上传API"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.utils.oss_client import oss_client
from app.core.security import get_current_user_id
from app.schemas.response import StandardResponse
from typing import List
import io
from PIL import Image

router = APIRouter()

# 允许的图片格式
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/image", summary="上传单张图片")
async def upload_image(
    file: UploadFile = File(..., description="图片文件"),
    folder: str = "housekeeping",
    user_id: str = Depends(get_current_user_id)
):
    """
    上传图片到OSS
    
    支持格式：JPG、PNG、WEBP、GIF
    文件大小：不超过10MB
    
    Args:
        file: 图片文件
        folder: 存储文件夹（默认housekeeping，可选：avatars, certificates, services等）
    
    Returns:
        {
            "url": "https://xxx.oss-cn-shanghai.aliyuncs.com/housekeeping/20240101/xxx.jpg",
            "key": "housekeeping/20240101/xxx.jpg",
            "size": 12345
        }
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。仅支持: JPG, PNG, WEBP, GIF"
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 验证文件大小
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # 验证是否为有效图片
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="无效的图片文件"
        )
    
    # 上传到OSS
    try:
        result = oss_client.upload_file(
            file_content=contents,
            filename=file.filename,
            folder=folder
        )
        
        return StandardResponse(
            code=200,
            message="上传成功",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/avatar", summary="上传用户头像")
async def upload_avatar(
    file: UploadFile = File(..., description="头像图片"),
    user_id: str = Depends(get_current_user_id)
):
    """
    上传用户头像（专用接口）
    
    支持格式：JPG、PNG、WEBP
    文件大小：不超过5MB
    建议尺寸：200x200 或更大
    
    Returns:
        {
            "url": "https://xxx.oss-cn-shanghai.aliyuncs.com/avatars/20240101/xxx.jpg",
            "key": "avatars/20240101/xxx.jpg",
            "size": 12345
        }
    """
    # 验证文件类型
    if file.content_type not in {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}:
        raise HTTPException(
            status_code=400,
            detail="头像仅支持 JPG、PNG、WEBP 格式"
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 头像文件大小限制为5MB
    max_avatar_size = 5 * 1024 * 1024
    if len(contents) > max_avatar_size:
        raise HTTPException(
            status_code=400,
            detail="头像文件过大，最大支持 5MB"
        )
    
    # 验证是否为有效图片
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
        
        # 重新打开图片以获取尺寸
        image = Image.open(io.BytesIO(contents))
        width, height = image.size
        
        # 建议尺寸检查（仅警告）
        if width < 100 or height < 100:
            print(f"警告: 头像尺寸较小 ({width}x{height})，建议至少 200x200")
    
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="无效的图片文件"
        )
    
    # 上传到OSS的avatars文件夹
    try:
        result = oss_client.upload_file(
            file_content=contents,
            filename=file.filename,
            folder="avatars"
        )
        
        return StandardResponse(
            code=200,
            message="头像上传成功",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/batch", summary="批量上传图片")
async def upload_images_batch(
    files: List[UploadFile] = File(..., description="图片文件列表"),
    folder: str = "housekeeping",
    user_id: str = Depends(get_current_user_id)
):
    """
    批量上传图片（最多10张）
    
    适用场景：
    - 家政阿姨申请时上传多张证书
    - 服务项目上传多张展示图
    
    Args:
        files: 图片文件列表
        folder: 存储文件夹
    
    Returns:
        {
            "success": [{"url": "...", "key": "...", "filename": "..."}],
            "failed": [{"filename": "...", "error": "..."}]
        }
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="最多同时上传10张图片"
        )
    
    success_list = []
    failed_list = []
    
    for file in files:
        try:
            # 验证文件类型
            if file.content_type not in ALLOWED_IMAGE_TYPES:
                failed_list.append({
                    "filename": file.filename,
                    "error": "不支持的文件类型"
                })
                continue
            
            # 读取文件
            contents = await file.read()
            
            # 验证大小
            if len(contents) > MAX_FILE_SIZE:
                failed_list.append({
                    "filename": file.filename,
                    "error": "文件过大"
                })
                continue
            
            # 验证是否为有效图片
            try:
                image = Image.open(io.BytesIO(contents))
                image.verify()
            except Exception:
                failed_list.append({
                    "filename": file.filename,
                    "error": "无效的图片文件"
                })
                continue
            
            # 上传
            result = oss_client.upload_file(
                file_content=contents,
                filename=file.filename,
                folder=folder
            )
            
            success_list.append({
                **result,
                "filename": file.filename
            })
        
        except Exception as e:
            failed_list.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return StandardResponse(
        code=200,
        message=f"上传完成: 成功{len(success_list)}个，失败{len(failed_list)}个",
        data={
            "success": success_list,
            "failed": failed_list,
            "total": len(files),
            "success_count": len(success_list),
            "failed_count": len(failed_list)
        }
    )


@router.delete("/image", summary="删除图片")
async def delete_image(
    key: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    删除OSS上的图片
    
    Args:
        key: OSS对象键（如 'housekeeping/20240101/xxx.jpg'）
    
    注意：删除操作不可恢复，请谨慎使用
    """
    try:
        success = oss_client.delete_file(key)
        
        if success:
            return StandardResponse(
                code=200,
                message="删除成功"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="删除失败"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除失败: {str(e)}"
        )


@router.post("/file", summary="上传通用文件")
async def upload_file(
    file: UploadFile = File(..., description="文件"),
    folder: str = "files",
    user_id: str = Depends(get_current_user_id)
):
    """
    上传通用文件（非图片）
    
    支持格式：PDF、DOC、DOCX、XLS、XLSX等
    文件大小：不超过20MB
    
    适用场景：
    - 上传合同文件
    - 上传证明材料
    
    Returns:
        {
            "url": "https://xxx.oss-cn-shanghai.aliyuncs.com/files/20240101/xxx.pdf",
            "key": "files/20240101/xxx.pdf",
            "size": 12345
        }
    """
    # 允许的文件类型
    allowed_types = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型。仅支持: PDF, DOC, DOCX, XLS, XLSX"
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 文件大小限制20MB
    max_file_size = 20 * 1024 * 1024
    if len(contents) > max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {max_file_size // 1024 // 1024}MB"
        )
    
    # 上传到OSS
    try:
        result = oss_client.upload_file(
            file_content=contents,
            filename=file.filename,
            folder=folder
        )
        
        return StandardResponse(
            code=200,
            message="上传成功",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )
