# 安全配置说明

## 手动生成接口控制

为了防止手动生成语录接口被滥用（特别是在生产环境中），系统提供了环境变量来控制该接口的访问权限。

### 配置方法

在 `.env` 文件中设置以下环境变量：

```bash
# 安全配置
# 是否启用手动生成语录接口 (True=启用, False=禁用)
# 建议在生产环境中设置为False，避免接口被滥用
ENABLE_MANUAL_GENERATION=True
```

### 配置选项

- `ENABLE_MANUAL_GENERATION=True`：启用手动生成接口
- `ENABLE_MANUAL_GENERATION=False`：禁用手动生成接口

### 使用建议

1. **开发环境**：设置为 `True`，方便测试和调试
2. **生产环境**：设置为 `False`，防止接口被恶意调用
3. **公开API**：如果你的API需要公开访问，强烈建议设置为 `False`

### 接口行为

当 `ENABLE_MANUAL_GENERATION=False` 时：

- 调用 `/admin/generate` 接口会返回错误信息
- 定时任务仍然正常工作，不受影响
- 获取语录的接口（`/api/quote`）不受影响

### 错误响应示例

```json
{
  "success": false,
  "message": "手动生成功能已被禁用。如需启用，请在.env文件中设置ENABLE_MANUAL_GENERATION=True"
}
```

### CORS跨域配置

系统根据DEBUG环境变量自动配置CORS策略：

### 开发环境 (DEBUG=True)
- ✅ 启用CORS跨域支持
- ✅ 允许所有来源访问
- ✅ 支持前端开发调试

### 生产环境 (DEBUG=False)
- 🔒 禁用CORS跨域支持
- 🔒 提高安全性
- 🔒 防止未授权的跨域访问

### 配置方法

在 `.env` 文件中设置：

```bash
# 开发环境
DEBUG=True

# 生产环境
DEBUG=False
```

### 生产环境CORS建议

如果生产环境需要跨域访问，建议：

1. **使用nginx代理**（推荐）：
   ```nginx
   location /api/ {
       proxy_pass http://backend:8000;
   }
   ```

2. **配置特定域名**：
   ```python
   # 修改main.py，添加特定域名
   allow_origins=["https://yourdomain.com"]
   ```

## 注意事项

- 修改环境变量后需要重启应用才能生效
- 该设置不影响系统的定时生成功能
- 该设置不影响语录查询相关的API接口
- 生产环境建议使用nginx代理而不是直接暴露CORS
