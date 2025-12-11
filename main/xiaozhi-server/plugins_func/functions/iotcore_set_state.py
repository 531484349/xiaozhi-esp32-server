import uuid

from plugins_func.register import register_function, ToolType, ActionResponse, Action
from plugins_func.functions.iotcore_init import initialize_iotcore_set_handler
from config.logger import setup_logging
import asyncio
import requests

TAG = __name__
logger = setup_logging()

iotcore_set_state_function_desc = {
    "type": "function",
    "function": {
        "name": "iotcore_set_state",
        "description": "如果没有真实的描述请不要用这个工具",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "需要操作的设备deviceId",
                },
                "command": {
                    "type": "string",
                    "description": "对设备属性的操作指令，json转义字符串, 请一定要按照属性的类型为属性赋值，enum类型、int类型、float类型等属性一定不能用字符串作为值。"
                                   "例如'{\"switch\":0}'就不能写成'{\"switch\":\"0\"}",
                },
            },
            "required": ["device_id", "command"],
        },
    },
}


@register_function("iotcore_set_state", iotcore_set_state_function_desc, ToolType.SYSTEM_CTL)
def iotcore_set_state(conn, device_id="", command=None):
    if command is None:
        command = {}
    try:
        ha_response = handle_iotcore_set_state(conn, device_id, command)
        return ActionResponse(Action.REQLLM, ha_response, None)
    except asyncio.TimeoutError:
        logger.bind(tag=TAG).error("控制IOT设备超时")
        return ActionResponse(Action.ERROR, "请求超时", None)
    except Exception as e:
        error_msg = f"执行IOT操作失败"
        logger.bind(tag=TAG).error(error_msg)
        return ActionResponse(Action.ERROR, error_msg, None)


def handle_iotcore_set_state(conn, device_id, command):
    iot_config = initialize_iotcore_set_handler(conn)
    api_key = iot_config.get("api_key")
    base_url = iot_config.get("base_url")

    split = device_id.split("/")

    data = {
        "RequestId": str(uuid.uuid4().hex),
        "Action": "AppControlDeviceData",
        "ProductId": split[0],
        "DeviceName": split[1],
        "Data": command,
    }
    url = f"{base_url}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data, timeout=5)  # 设置5秒超时
    logger.bind(tag=TAG).info(
        f"操作结束,url:{url},return_code:{response.status_code}"
    )
    if response.status_code == 200:
        return "操作结束"
    else:
        return f"设置失败，错误码: {response.status_code}"
