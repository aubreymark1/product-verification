# Mock 数据指南

Mock 数据只用于联调；无法核验的演示内容必须标记为 `demo_mock`，并使用 `source_url: null`。当前演示数据使用稳定 ID（如 `demo_video_001`、`gaming_mouse`、`atk_a9_ultimate`）。

前后端读取 `data/mock/` 下的 JSON；字段变更必须先同步 API 合同。证据的 `source_type` 使用 `demo_mock`，并在页面上保持演示性质说明。

