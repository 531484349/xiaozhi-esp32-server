from config.logger import setup_logging
from config.config_loader import get_project_dir
from config.config_loader import read_config

TAG = __name__
logger = setup_logging()


def initialize_iotcore_get_handler(conn):
    iot_config = {}
    if not conn.load_function_plugin:
        return iot_config

    # 确定配置来源
    config_source = (
        "iotcore_get_state"
    )
    if not conn.config["plugins"].get(config_source):
        return iot_config

    # 统一获取配置
    plugin_config = conn.config["plugins"][config_source]
    iot_config["base_url"] = plugin_config.get("base_url")
    iot_config["api_key"] = plugin_config.get("api_key")

    custom_config_path = get_project_dir() + "data/.config.yaml"
    custom_config = read_config(custom_config_path)
    manager_api_config = custom_config.get("manager-api", {})

    if not iot_config["api_key"]:
        iot_config["api_key"] = manager_api_config["secret"]

    return iot_config


def initialize_iotcore_set_handler(conn):
    iot_config = {}
    if not conn.load_function_plugin:
        return iot_config

    # 确定配置来源
    config_source = (
        "iotcore_set_state"
    )
    if not conn.config["plugins"].get(config_source):
        return iot_config

    # 统一获取配置
    plugin_config = conn.config["plugins"][config_source]
    iot_config["base_url"] = plugin_config.get("base_url")
    iot_config["api_key"] = plugin_config.get("api_key")

    custom_config_path = get_project_dir() + "data/.config.yaml"
    custom_config = read_config(custom_config_path)
    manager_api_config = custom_config.get("manager-api", {})

    if not iot_config["api_key"]:
        iot_config["api_key"] = manager_api_config["secret"]

    return iot_config
