# nanobanana_tool

这是一个放在项目根目录下的独立 Python 工具，用来复刻 `nanobanana` 开源项目的主要功能，但不依赖 Gemini CLI 扩展机制。

它的目标不是“包装原来的 MCP 服务”，而是直接用 Python 标准库调用 Gemini 图像接口，实现一套本地可执行的脚本。

## 功能范围

- `generate`：文本生成图片
- `edit`：编辑现有图片
- `restore`：修复或增强现有图片
- `icon`：生成图标、favicon、UI 图标
- `pattern`：生成图案、纹理、壁纸
- `story`：生成连续步骤图、分镜、教程图
- `diagram`：生成流程图、架构图、数据库图等
- `nanobanana`：自然语言入口，自动判断要调用哪类命令

现在所有会返回图片的命令都支持 Gemini 官方 `generationConfig.imageConfig` 的硬控制参数：

- `--aspect`
  控制输出宽高比
- `--image-size`
  控制输出尺寸档位

## 文件说明

- `cli.py`
  负责命令行参数解析、参数校验、结果输出。
- `service.py`
  负责核心业务逻辑，包括 prompt 组装、批量生成、自然语言路由、预览打开。
- `gemini_client.py`
  负责直接请求 Gemini `generateContent` 接口。
- `file_handler.py`
  负责输入文件搜索、输出目录创建、文件名生成、base64 编解码。
- `command_specs.py`
  负责读取 `nanobanana/commands/*.toml` 的描述信息，供帮助文案复用。

## 环境要求

- Python 3.11+
- 可用的 Gemini API Key

支持以下环境变量，按顺序查找：

1. `NANOBANANA_API_KEY`
2. `NANOBANANA_GEMINI_API_KEY`
3. `NANOBANANA_GOOGLE_API_KEY`
4. `GEMINI_API_KEY`
5. `GOOGLE_API_KEY`

可选模型变量：

- `NANOBANANA_MODEL`
  默认值是 `gemini-3.1-flash-image-preview`

仓库里提供了环境变量模板文件：

```bash
nanobanana_tool/.env.example
```

建议复制为 `.env` 后再执行：

```bash
cp nanobanana_tool/.env.example nanobanana_tool/.env
source nanobanana_tool/.env
```

如果你需要走代理或自建网关，可以设置：

- `NANOBANANA_API_BASE_URL`
- `NANOBANANA_PROXY_ENDPOINT`
- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`

其中 `NANOBANANA_API_BASE_URL` 只需要填 base URL，例如：

```bash
export NANOBANANA_API_BASE_URL="https://your-proxy.example.com/v1beta"
```

代码会自动拼接后面的：

```text
/models/{model}:generateContent?key={api_key}
```

只有在你的代理地址不是这种标准结构时，才需要改用 `NANOBANANA_PROXY_ENDPOINT` 填完整模板。

## 用法

入口放在包内，直接这样运行：

```bash
python -m nanobanana_tool --help
```

### 1. 文生图

```bash
python -m nanobanana_tool generate "a watercolor fox in snow" --count=3 --styles=watercolor,sketch
python -m nanobanana_tool generate "anime portrait" --reference /tmp/ref.png --output-dir /tmp/out --output-name portrait
python -m nanobanana_tool generate "anime portrait" --aspect 9:16 --image-size 2K
```

### 2. 编辑图片

```bash
python -m nanobanana_tool edit input.png "add sunglasses to the character" --preview
python -m nanobanana_tool edit /data/in.png "add sunglasses" --output-dir /data/out --output-name in_edited
python -m nanobanana_tool edit input.png "convert this into a wide banner" --aspect 16:9 --image-size 2K
```

### 3. 修复图片

```bash
python -m nanobanana_tool restore old_photo.jpg "remove scratches and improve clarity"
python -m nanobanana_tool restore old_photo.jpg "remove scratches and improve clarity" --aspect 4:5 --image-size 1K
```

### 4. 生成图标

```bash
python -m nanobanana_tool icon "coffee shop logo" --type=favicon --sizes=16,32,64
python -m nanobanana_tool icon "coffee shop logo" --type=app-icon --aspect 1:1 --image-size 1K
```

### 5. 生成图案 / 纹理

```bash
python -m nanobanana_tool pattern "retro geometric wallpaper" --size 512x512 --image-size 2K
```

注意：

- `pattern --size` 是纹理的 tile 逻辑尺寸，会写入 prompt
- `--image-size` 是 Gemini API 的硬控制输出尺寸
- 两者不是一回事，可以同时使用

### 6. 自然语言入口

```bash
python -m nanobanana_tool nanobanana "给我做一个咖啡店 app 图标"
python -m nanobanana_tool nanobanana "把 game/assets/hero.png 改成惊讶表情" --preview
python -m nanobanana_tool nanobanana "画一个用户登录流程图"
python -m nanobanana_tool nanobanana "做一张海报" --reference /tmp/ref.png --output-dir /tmp/out --output-name poster
python -m nanobanana_tool nanobanana "做一张角色海报" --aspect 3:4 --image-size 2K
```

也兼容斜杠命令风格：

```bash
python -m nanobanana_tool /generate "sunset over mountains"
python -m nanobanana_tool /diagram "microservices architecture"
```

## 自然语言路由说明

`nanobanana` 子命令会按原项目 `commands/nanobanana.toml` 的职责，在已有命令之间做选择：

- 命中“图标 / favicon / logo / ui element”等关键词时，走 `icon`
- 命中“图案 / 纹理 / seamless / wallpaper”等关键词时，走 `pattern`
- 命中“流程图 / 架构图 / diagram / database / sequence”等关键词时，走 `diagram`
- 命中“故事 / 分镜 / 教程 / timeline / step-by-step”等关键词时，走 `story`
- 如果显式传了 `--file`，并且命中“修复 / restore / enhance”等关键词，走 `restore`
- 如果显式传了 `--file`，默认走 `edit`
- 其他情况默认走 `generate`

这里的“增强”只体现在关键词覆盖更完整，支持中英混合描述；不会额外自动推断数量、步骤数、文件路径或子类型参数。

## 输出目录

生成结果默认写到项目根目录下的：

```text
nanobanana-output/
```

这个目录已经加入 `.gitignore`。

现在也支持手动指定：

- `--reference`
  为生成类命令提供参考图路径
- `--output-dir`
  指定生成结果保存目录
- `--output-name`
  指定输出文件基名；如果一次生成多张，后续文件会自动追加编号
- `--aspect`
  使用 Gemini 的 `generationConfig.imageConfig.aspectRatio` 硬控制输出比例
- `--image-size`
  使用 Gemini 的 `generationConfig.imageConfig.imageSize` 硬控制输出尺寸档位

## 当前实现边界

- 这套实现复刻的是原项目的主要能力，不是完整逐行移植
- `grid`、`storyboard` 这类参数目前保留接口，但没有额外做后处理拼图
- 自然语言路由只负责在原项目已有命令之间选路，不会额外脑补新功能
- 如果 Gemini 返回的响应结构变化，可能需要同步调整 `service.py` 的图片提取逻辑
- `--image-size` 目前按 Gemini 官方枚举限制为 `512`、`1K`、`2K`、`4K`
- `--aspect` 目前按 Gemini 官方枚举限制为 `1:1`、`1:4`、`4:1`、`1:8`、`8:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`
- 并不是所有模型都支持全部尺寸档位；默认模型 `gemini-3.1-flash-image-preview` 支持硬控制，若切到其他模型需以该模型能力为准
