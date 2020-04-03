import os

from hummingbot.core.utils.async_utils import safe_ensure_future
from hummingbot.client.config.config_helpers import (
    update_strategy_config_map_from_file,
    short_strategy_name,
    format_config_file_name
)
from hummingbot.client.settings import CONF_FILE_PATH, CONF_PREFIX
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hummingbot.client.hummingbot_application import HummingbotApplication


class ImportCommand:

    def import_command(self,  # type: HummingbotApplication
                       file_name):
        if file_name is not None:
            file_name = format_config_file_name(file_name)
        self.app.clear_input()
        self.placeholder_mode = True
        self.app.toggle_hide_input()
        safe_ensure_future(self.import_config_file(file_name))

    async def import_config_file(self,  # type: HummingbotApplication
                                 file_name):
        if file_name is None:
            file_name = await self.prompt_a_file_name()
        strategy_path = os.path.join(CONF_FILE_PATH, file_name)
        strategy = update_strategy_config_map_from_file(strategy_path)
        self.strategy_file_name = file_name
        self.strategy_name = strategy
        self._notify(f"Configuration from {self.strategy_file_name} file is imported.")
        self.placeholder_mode = False
        self.app.change_prompt(prompt=">>> ")
        if not await self.notify_missing_configs():
            self._notify("Enter \"start\" to start market making.")
            self.app.set_text("start")

    async def prompt_a_file_name(self  # type: HummingbotApplication
                                 ):
        example = f"{CONF_PREFIX}{short_strategy_name('pure_market_making')}_{1}.yml"
        file_name = await self.app.prompt(prompt=f'Enter path to your strategy file (e.g. "{example}") >>> ')
        file_path = os.path.join(CONF_FILE_PATH, file_name)
        if not os.path.exists(file_path):
            self._notify(f"{file_name} does not  exists, please enter a valid file name.")
            await self.prompt_a_file_name()
        else:
            return file_name
