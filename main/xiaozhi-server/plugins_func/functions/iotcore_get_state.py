import asyncio
import uuid

import requests

from config.logger import setup_logging
from plugins_func.functions.iotcore_init import initialize_iotcore_get_handler
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

iotcore_get_state_function_desc = {
    "type": "function",
    "function": {
        "name": "iotcore_get_state",
        "description": "如果没有真实的描述请不要用这个工具",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "需要查询的设备deviceId",
                },
            },
            "required": ["device_id"],
        },
    },
}


@register_function("iotcore_get_state", iotcore_get_state_function_desc, ToolType.SYSTEM_CTL)
def iotcore_get_state(conn, device_id=""):
    try:
        ha_response = handle_iotcore_get_state(conn, device_id)
        return ActionResponse(Action.REQLLM, ha_response, None)
    except asyncio.TimeoutError:
        logger.bind(tag=TAG).error("获取IOT状态超时")
        return ActionResponse(Action.ERROR, "请求超时", None)
    except Exception as e:
        error_msg = f"执行IOT操作失败"
        logger.bind(tag=TAG).error(error_msg)
        return ActionResponse(Action.ERROR, error_msg, None)


def handle_iotcore_get_state(conn, device_id):
    iot_config = initialize_iotcore_get_handler(conn)
    api_key = iot_config.get("api_key")
    base_url = iot_config.get("base_url")

    data = {
        "RequestId": str(uuid.uuid4().hex),
        "Action": "AppGetDeviceDataList",
        "DeviceIds": [device_id],
    }
    url = f"{base_url}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data, timeout=5)  # 设置5秒超时
    logger.bind(tag=TAG).info(
        f"查询结束,url:{url},return_code:{response.status_code}"
    )
    if response.status_code == 200:
        logger.bind(tag=TAG).info(f"api返回内容: {response.json()}")
        result = response.json()["data"]
        devices = result["Data"]
        for device in devices:
            if device_id == device["DeviceId"]:
                state = device["Data"]
                logger.bind(tag=TAG).info(f"设备状态: {state}")
                return f"查询到的设备状态为: {state}"
        return f"查询失败"

    else:
        return f"查询失败，错误码: {response.status_code}"
