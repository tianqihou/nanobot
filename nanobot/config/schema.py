"""Configuration schema using Pydantic."""

from pathlib import Path
from typing import Dict

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class WhatsAppConfig(BaseModel):
    """WhatsApp channel configuration."""
    enabled: bool = False
    bridge_url: str = "ws://localhost:3001"
    allow_from: list[str] = Field(default_factory=list)  # Allowed phone numbers


class TelegramConfig(BaseModel):
    """Telegram channel configuration."""
    enabled: bool = False
    token: str = ""  # Bot token from @BotFather
    allow_from: list[str] = Field(default_factory=list)  # Allowed user IDs or usernames
    proxy: str | None = None  # HTTP/SOCKS5 proxy URL, e.g. "http://127.0.0.1:7890" or "socks5://127.0.0.1:1080"


class FeishuConfig(BaseModel):
    """Feishu/Lark channel configuration using WebSocket long connection."""
    enabled: bool = False
    app_id: str = ""  # App ID from Feishu Open Platform
    app_secret: str = ""  # App Secret from Feishu Open Platform
    encrypt_key: str = ""  # Encrypt Key for event subscription (optional)
    verification_token: str = ""  # Verification Token for event subscription (optional)
    allow_from: list[str] = Field(default_factory=list)  # Allowed user open_ids


class DiscordConfig(BaseModel):
    """Discord channel configuration."""
    enabled: bool = False
    token: str = ""  # Bot token from Discord Developer Portal
    allow_from: list[str] = Field(default_factory=list)  # Allowed user IDs
    gateway_url: str = "wss://gateway.discord.gg/?v=10&encoding=json"
    intents: int = 37377  # GUILDS + GUILD_MESSAGES + DIRECT_MESSAGES + MESSAGE_CONTENT


class ChannelsConfig(BaseModel):
    """Configuration for chat channels."""
    whatsapp: WhatsAppConfig = Field(default_factory=WhatsAppConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    feishu: FeishuConfig = Field(default_factory=FeishuConfig)


class AgentDefaults(BaseModel):
    """Default agent configuration."""
    workspace: str = "~/.nanobot/workspace"
    provider: str = "openaiCompatible"
    max_tokens: int = 8192
    temperature: float = 0.7
    max_tool_iterations: int = 20


class AgentsConfig(BaseModel):
    """Agent configuration."""
    defaults: AgentDefaults = Field(default_factory=AgentDefaults)


class ProviderConfig(BaseModel):
    """LLM provider configuration."""
    model: str = "openai/qwen"
    api_key: str = "empty"
    api_base: str | None = None

class GatewayConfig(BaseModel):
    """Gateway/server configuration."""
    host: str = "0.0.0.0"
    port: int = 18790



class ExecToolConfig(BaseModel):
    """Shell exec tool configuration."""
    timeout: int = 60


class ToolsConfig(BaseModel):
    """Tools configuration."""
    exec: ExecToolConfig = Field(default_factory=ExecToolConfig)
    restrict_to_workspace: bool = False  # If true, restrict all tool access to workspace directory


def default_providers():
    """Generate default providers configuration."""
    return {
        "openai_compatible": ProviderConfig(
            model="openai/doubao-seed-1-6-flash-250828",
            api_key="",
            api_base="https://ark.cn-beijing.volces.com/api/v3"
        ),
        "vllm":  ProviderConfig(
            model="hosted_vllm/qwen",
            api_key="empty",
            api_base="http://localhost:8080/v1"
        ),
    }

class Config(BaseSettings):
    """Root configuration for nanobot."""
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    channels: ChannelsConfig = Field(default_factory=ChannelsConfig)
    providers: Dict[str, ProviderConfig] = Field(default_factory=default_providers)
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)

    @property
    def workspace_path(self) -> Path:
        """Get expanded workspace path."""
        return Path(self.agents.defaults.workspace).expanduser()

    def get_api_key(self) -> str | None:
        """Get API key in priority order: OpenRouter > Anthropic > OpenAI > Gemini > Zhipu > Groq > vLLM."""
        return self.providers[self.agents.defaults.provider].api_key


    def get_api_base(self) -> str | None:
        """Get API base URL if using LiteLLM."""
        return self.providers[self.agents.defaults.provider].api_base

    def get_model(self) -> str | None:
        """Get model name if using LiteLLM."""
        return self.providers[self.agents.defaults.provider].model

    class Config:
        env_prefix = "NANOBOT_"
        env_nested_delimiter = "__"
