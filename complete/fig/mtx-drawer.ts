const completionSpec: Fig.Spec = {
    "name": "mtx-drawer",
    "description": "mtx-drawer",
    "subcommands": [
        {
            "name": "complete",
            "description": "获取补全列表",
            "args": [],
            "options": [
                {
                    "name": "--team",
                    "description": "团队名",
                    "isOptional": true,
                    "args": {
                        "name": "team",
                        "description": "团队名"
                    }
                },
                {
                    "name": "--token",
                    "description": "团队token",
                    "isOptional": true,
                    "args": {
                        "name": "token",
                        "description": "团队token"
                    }
                },
                {
                    "name": "--is-script",
                    "description": "是否为脚本"
                }
            ]
        },
        {
            "name": "draw-one",
            "description": "单个文件处理",
            "args": [
                {
                    "name": "filepath",
                    "description": "文件路径",
                    "template": [
                        "filepaths",
                        "folders"
                    ]
                }
            ],
            "options": [
                {
                    "name": "-ops",
                    "description": "操作列表",
                    "args": {
                        "name": "ops",
                        "description": "操作列表",
                        "isVariadic": true,
                        "isRequired": true,
                        "suggestions": [
                            "abs",
                            "log",
                            "aver",
                            "real"
                        ]
                    }
                },
                {
                    "name": "--force",
                    "description": "是否强制更新"
                },
                {
                    "name": "--log-times",
                    "description": "取log次数",
                    "isOptional": true,
                    "args": {
                        "name": "log-times",
                        "description": "取log次数"
                    }
                },
                {
                    "name": "--mat-size",
                    "description": "缩略图尺寸",
                    "isOptional": true,
                    "args": {
                        "name": "mat-size",
                        "description": "缩略图尺寸"
                    }
                },
                {
                    "name": "--block-size",
                    "description": "设置块大小（此参数设置后将覆盖mat_size）",
                    "isOptional": true,
                    "args": {
                        "name": "block-size",
                        "description": "设置块大小（此参数设置后将覆盖mat_size）"
                    }
                },
                {
                    "name": "--tick-step",
                    "description": "<tick-step>",
                    "isOptional": true,
                    "args": {
                        "name": "tick-step",
                        "description": "<tick-step>"
                    }
                },
                {
                    "name": "--img-format",
                    "description": "图片格式",
                    "isOptional": true,
                    "args": {
                        "name": "img-format",
                        "description": "图片格式"
                    }
                },
                {
                    "name": "--font-color",
                    "description": "字体颜色",
                    "isOptional": true,
                    "args": {
                        "name": "font-color",
                        "description": "字体颜色"
                    }
                },
                {
                    "name": "--show-in-console",
                    "description": "是否在控制台显示图像, 如果为True则不会保存图像"
                }
            ]
        },
        {
            "name": "draw",
            "description": "多个文件处理",
            "args": [],
            "options": [
                {
                    "name": "-ops",
                    "description": "操作列表",
                    "args": {
                        "name": "ops",
                        "description": "操作列表",
                        "isVariadic": true,
                        "isRequired": true,
                        "suggestions": [
                            "abs",
                            "log",
                            "aver",
                            "real"
                        ]
                    }
                },
                {
                    "name": "--force",
                    "description": "是否强制更新"
                },
                {
                    "name": "--log-times",
                    "description": "取log次数",
                    "isOptional": true,
                    "args": {
                        "name": "log-times",
                        "description": "取log次数"
                    }
                },
                {
                    "name": "--mat-size",
                    "description": "缩略图尺寸",
                    "isOptional": true,
                    "args": {
                        "name": "mat-size",
                        "description": "缩略图尺寸"
                    }
                },
                {
                    "name": "--block-size",
                    "description": "设置块大小（此参数设置后将覆盖mat_size）",
                    "isOptional": true,
                    "args": {
                        "name": "block-size",
                        "description": "设置块大小（此参数设置后将覆盖mat_size）"
                    }
                },
                {
                    "name": "--tick-step",
                    "description": "<tick-step>",
                    "isOptional": true,
                    "args": {
                        "name": "tick-step",
                        "description": "<tick-step>"
                    }
                },
                {
                    "name": "--img-format",
                    "description": "<img-format>",
                    "isOptional": true,
                    "args": {
                        "name": "img-format",
                        "description": "<img-format>"
                    }
                },
                {
                    "name": "--font-color",
                    "description": "<font-color>",
                    "isOptional": true,
                    "args": {
                        "name": "font-color",
                        "description": "<font-color>"
                    }
                }
            ]
        },
        {
            "name": "update",
            "description": "更新",
            "args": [],
            "options": []
        }
    ]
};
export default completionSpec;
