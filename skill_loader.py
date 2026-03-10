import os
import json
import re
import importlib.util
from pathlib import Path

class SkillLoader:
    ALLOWED_SKILL_PATTERN = re.compile(r'^[a-z0-9_]+$')

    def __init__(self, skills_dir="skills"):
        self.skills_dir = Path(skills_dir).resolve()
        self.skills = {}
        self.handlers = {}

    def _validate_skill_name(self, skill_name):
        """验证技能名称安全性"""
        if not self.ALLOWED_SKILL_PATTERN.match(skill_name):
            raise ValueError(f"Invalid skill name: {skill_name}")
        return True

    def _validate_skill_path(self, skill_path):
        """验证路径在 skills 目录内，防止路径遍历"""
        resolved_path = Path(skill_path).resolve()
        if not str(resolved_path).startswith(str(self.skills_dir)):
            raise ValueError(f"Path traversal detected: {skill_path}")
        return True

    def load_skill_metadata(self):
        """加载所有技能的元数据"""
        for skill_name in os.listdir(self.skills_dir):
            if not self.ALLOWED_SKILL_PATTERN.match(skill_name):
                continue

            skill_path = self.skills_dir / skill_name
            if not skill_path.is_dir():
                continue

            self._validate_skill_path(skill_path)

            skill_md = skill_path / "skill.md"
            if not skill_md.exists():
                continue

            metadata = self._parse_skill_md(skill_md)
            if metadata:
                self.skills[metadata["name"]] = {
                    "path": str(skill_path),
                    "metadata": metadata
                }

    def _parse_skill_md(self, md_path):
        """解析 skill.md 文件"""
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        metadata = {}
        current_section = None
        section_content = []

        for line in lines:
            if line.startswith('## name'):
                current_section = 'name'
                section_content = []
            elif line.startswith('## description'):
                if current_section == 'name':
                    metadata['name'] = '\n'.join(section_content).strip()
                current_section = 'description'
                section_content = []
            elif line.startswith('## parameters'):
                if current_section == 'description':
                    metadata['description'] = '\n'.join(section_content).strip()
                current_section = 'parameters'
                section_content = []
            elif current_section:
                section_content.append(line)

        if current_section == 'parameters':
            params_text = '\n'.join(section_content).strip()
            if params_text and params_text != '无参数':
                params_text = params_text.replace('```json', '').replace('```', '').strip()
                try:
                    metadata['parameters'] = json.loads(params_text)
                except:
                    pass

        return metadata if 'name' in metadata else None

    def load_skill_agent(self, skill_name):
        """动态加载技能的 agent"""
        self._validate_skill_name(skill_name)

        if skill_name not in self.skills:
            raise ValueError(f"Skill not registered: {skill_name}")

        agent_path = os.path.join(self.skills[skill_name]["path"], "agent.py")
        if not os.path.exists(agent_path):
            return None

        self._validate_skill_path(agent_path)

        spec = importlib.util.spec_from_file_location(f"{skill_name}_agent", agent_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def load_handler(self, skill_name):
        """动态加载技能的处理器"""
        if skill_name in self.handlers:
            return self.handlers[skill_name]

        self._validate_skill_name(skill_name)

        if skill_name not in self.skills:
            raise ValueError(f"Skill not registered: {skill_name}")

        handler_path = os.path.join(self.skills[skill_name]["path"], "handler.py")
        if not os.path.exists(handler_path):
            return None

        self._validate_skill_path(handler_path)

        spec = importlib.util.spec_from_file_location(skill_name, handler_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.handlers[skill_name] = module
        return module

    def get_tools_definition(self):
        """获取所有技能的工具定义"""
        tools = []
        for skill_name, skill_info in self.skills.items():
            metadata = skill_info["metadata"]
            tool = {
                "type": "function",
                "function": {
                    "name": metadata["name"],
                    "description": metadata["description"]
                }
            }
            if "parameters" in metadata:
                tool["function"]["parameters"] = metadata["parameters"]
            tools.append(tool)
        return tools
