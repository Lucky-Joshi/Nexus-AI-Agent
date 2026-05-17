import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, List
from core.base_agent import BaseAgent, AgentStatus
from core.logger import Logger
from core.config import Config


class CodingAgent(BaseAgent):
    """
    Coding agent for NEXUS.
    Handles code generation, bug analysis, file editing, git operations, and repo analysis.
    """

    def __init__(self):
        super().__init__("coding_agent", "Code generation, analysis, and git operations")
        self.logger = Logger().get_logger("CodingAgent")
        self.config = Config()
        self._workspace = self.config.get("agents.coding_agent.workspace_path", str(Path.home()))
        self._default_lang = self.config.get("agents.coding_agent.default_language", "python")
        self._use_llm = self.config.get("llm.use_in_agents", True)
        self._llm = None
        if self._use_llm:
            try:
                from core.llm_provider import LLMProvider
                self._llm = LLMProvider(self.config)
            except Exception as e:
                self.logger.warning(f"LLM not available for coding: {e}")
                self._use_llm = False

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        try:
            cmd = command.lower()

            if any(kw in cmd for kw in ["generate", "write", "create"]) and any(kw in cmd for kw in ["code", "function", "class", "script"]):
                return self._handle_generate(command)
            elif any(kw in cmd for kw in ["explain", "what does"]):
                return self._handle_explain(command)
            elif any(kw in cmd for kw in ["debug", "fix", "error", "bug"]):
                return self._handle_debug(command)
            elif any(kw in cmd for kw in ["git"]):
                return self._handle_git(command)
            elif any(kw in cmd for kw in ["edit", "modify", "change"]) and any(kw in cmd for kw in ["file", "code"]):
                return self._handle_edit_file(command)
            elif any(kw in cmd for kw in ["analyze", "repository", "repo", "codebase"]):
                return self._handle_analyze(command)
            elif any(kw in cmd for kw in ["run", "execute", "test"]):
                return self._handle_run_command(command)
            else:
                return self._handle_generate(command)

        except Exception as e:
            self.logger.error(f"CodingAgent error: {e}")
            return {
                "success": False,
                "response": f"Coding error: {str(e)}",
                "error": str(e),
            }
        finally:
            self.status = AgentStatus.IDLE

    def get_capabilities(self) -> list:
        return [
            "generate_code",
            "explain_code",
            "debug_code",
            "edit_file",
            "git_command",
            "analyze_repository",
            "run_command",
            "read_file",
            "list_files",
        ]

    def _handle_generate(self, command: str) -> Dict[str, Any]:
        description = command
        prefixes = ["generate code for ", "write code for ", "create code for ",
                     "generate code ", "write code ", "create code ",
                     "generate ", "write ", "create "]
        for prefix in prefixes:
            if description.lower().startswith(prefix):
                description = description[len(prefix):]
                break

        lang = self._detect_language(description)

        if self._use_llm and self._llm and self._llm.is_available():
            code = self._generate_code_llm(description, lang)
        else:
            code = self._generate_code_stub(description, lang)

        return {
            "success": True,
            "response": f"Generated {lang} code for: {description}\n\n```{lang}\n{code}\n```",
            "data": {"language": lang, "code": code, "description": description},
        }

    def _handle_explain(self, command: str) -> Dict[str, Any]:
        code = command
        for prefix in ["explain ", "explain code: ", "explain this code: ", "what does "]:
            code = code[len(prefix):]

        code = code.strip()
        if not code:
            return {"success": False, "response": "Please provide code to explain."}

        if self._use_llm and self._llm and self._llm.is_available():
            explanation = self._explain_code_llm(code)
        else:
            explanation = self._explain_code(code)
        return {
            "success": True,
            "response": f"Code explanation:\n\n{explanation}",
            "data": {"code": code, "explanation": explanation},
        }

    def _handle_debug(self, command: str) -> Dict[str, Any]:
        code = command
        for prefix in ["debug ", "fix ", "fix code: ", "debug code: "]:
            code = code[len(prefix):]

        code = code.strip()
        if not code:
            return {"success": False, "response": "Please provide code to debug."}

        if self._use_llm and self._llm and self._llm.is_available():
            issues = self._analyze_issues_llm(code)
        else:
            issues = self._analyze_issues(code)
        return {
            "success": True,
            "response": f"Code analysis:\n\n{issues}",
            "data": {"code": code, "issues": issues},
        }

    def _handle_git(self, command: str) -> Dict[str, Any]:
        git_cmd = command.lower().replace("git", "").strip()
        if not git_cmd:
            return {"success": False, "response": "Please provide a git command. Example: 'git status'"}

        return self._run_git_command(git_cmd)

    def _handle_edit_file(self, command: str) -> Dict[str, Any]:
        file_path = self._extract_file_path(command)
        if not file_path:
            return {"success": False, "response": "Please specify a file path."}

        target = Path(file_path)
        if not target.exists():
            return {"success": False, "response": f"File not found: {file_path}"}

        if "read" in command.lower() or "show" in command.lower() or "display" in command.lower():
            content = target.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            numbered = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines[:100]))
            return {
                "success": True,
                "response": f"Contents of {file_path} ({len(lines)} lines):\n\n{numbered}",
                "data": {"path": file_path, "lines": len(lines)},
            }

        return {
            "success": True,
            "response": f"File ready for editing: {file_path}\nUse your editor to make changes.",
            "data": {"path": file_path},
        }

    def _handle_analyze(self, command: str) -> Dict[str, Any]:
        repo_path = self._extract_path(command) or self._workspace
        target = Path(repo_path)

        if not target.exists():
            return {"success": False, "response": f"Path not found: {repo_path}"}

        stats = self._analyze_directory(target)
        return {
            "success": True,
            "response": stats,
            "data": {"path": str(target)},
        }

    def _handle_run_command(self, command: str) -> Dict[str, Any]:
        cmd = command
        for prefix in ["run ", "execute ", "test "]:
            cmd = cmd[len(prefix):].strip()

        if not cmd:
            return {"success": False, "response": "Please provide a command to run."}

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self._workspace,
            )
            output = result.stdout.strip()
            error = result.stderr.strip()

            response = f"Command: {cmd}\n"
            response += f"Exit code: {result.returncode}\n"
            if output:
                response += f"\nOutput:\n{output[:2000]}"
            if error:
                response += f"\nError:\n{error[:1000]}"

            return {
                "success": result.returncode == 0,
                "response": response,
                "data": {"command": cmd, "returncode": result.returncode},
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "response": f"Command timed out after 30s: {cmd}"}
        except Exception as e:
            return {"success": False, "response": f"Command failed: {str(e)}", "error": str(e)}

    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code for a given description."""
        if self._use_llm and self._llm and self._llm.is_available():
            return self._generate_code_llm(description, language)
        return self._generate_code_stub(description, language)

    def explain_code(self, code: str) -> str:
        """Provide explanation for code."""
        if self._use_llm and self._llm and self._llm.is_available():
            return self._explain_code_llm(code)
        return self._explain_code(code)

    def edit_file(self, file_path: str, content: str):
        """Write content to a file."""
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def read_file(self, file_path: str) -> str:
        """Read file contents."""
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")

    def git_command(self, command: str) -> Dict[str, Any]:
        """Run a git command."""
        return self._run_git_command(command)

    def _generate_code_llm(self, description: str, language: str) -> str:
        """Generate code using LLM."""
        system_prompt = (
            f"You are an expert {language} developer. "
            "Write clean, well-structured code with comments. "
            "Return ONLY the code, no explanations outside the code block. "
            "Include a brief docstring/comment at the top."
        )
        prompt = f"Write {language} code for: {description}"
        try:
            response = self._llm.generate(prompt, system_prompt=system_prompt)
            code = self._extract_code_block(response)
            return code if code else response
        except Exception as e:
            self.logger.warning(f"LLM code generation failed, falling back: {e}")
            return self._generate_code_stub(description, language)

    def _explain_code_llm(self, code: str) -> str:
        """Explain code using LLM."""
        system_prompt = "You are a patient code explainer. Explain what the code does, line by line if needed."
        prompt = f"Explain this code clearly:\n\n```{self._detect_language_from_code(code) or 'code'}\n{code}\n```"
        try:
            return self._llm.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            self.logger.warning(f"LLM explanation failed, falling back: {e}")
            return self._explain_code(code)

    def _analyze_issues_llm(self, code: str) -> str:
        """Analyze code for issues using LLM."""
        system_prompt = (
            "You are a code reviewer. Identify bugs, security issues, performance problems, "
            "and style violations. Provide specific fixes."
        )
        prompt = f"Review this code and list all issues:\n\n```{self._detect_language_from_code(code) or 'code'}\n{code}\n```"
        try:
            return self._llm.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            self.logger.warning(f"LLM analysis failed, falling back: {e}")
            return self._analyze_issues(code)

    def _extract_code_block(self, text: str) -> str:
        """Extract code from markdown code blocks."""
        match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _detect_language_from_code(self, code: str) -> Optional[str]:
        """Detect programming language from code content."""
        if re.search(r"\bdef\s+\w+|import\s+\w+|from\s+\w+\s+import", code):
            return "python"
        if re.search(r"\bfunction\s+\w+|const\s+\w+\s*=|=>", code):
            return "javascript"
        if re.search(r"<html|<!DOCTYPE", code):
            return "html"
        return None

    def _generate_code_stub(self, description: str, language: str) -> str:
        """Generate a basic code stub based on description."""
        if language == "python":
            return self._generate_python_stub(description)
        elif language in ("javascript", "js", "typescript", "ts"):
            return self._generate_js_stub(description)
        elif language == "html":
            return self._generate_html_stub(description)
        else:
            return f"# {language} code stub for: {description}\n# TODO: Implement"

    def _generate_python_stub(self, description: str) -> str:
        desc_lower = description.lower()

        if "function" in desc_lower or "calculate" in desc_lower:
            return f'''def {self._slugify(description)}():
    """{description}"""
    # TODO: Implement
    pass


if __name__ == "__main__":
    result = {self._slugify(description)}()
    print(result)'''

        elif "class" in desc_lower:
            class_name = self._camel_case(description)
            return f'''class {class_name}:
    """{description}"""

    def __init__(self):
        # TODO: Initialize
        pass

    def process(self):
        """Process the main logic."""
        # TODO: Implement
        pass


if __name__ == "__main__":
    obj = {class_name}()
    obj.process()'''

        else:
            return f'''"""
{description}
"""


def main():
    """Main entry point."""
    # TODO: Implement {description}
    print("Running: {description}")


if __name__ == "__main__":
    main()'''

    def _generate_js_stub(self, description: str) -> str:
        return f'''/**
 * {description}
 */

function {self._camel_case(description)}() {{
    // TODO: Implement
    console.log("{description}");
}}

// Export module
module.exports = {{ {self._camel_case(description)} }};'''

    def _generate_html_stub(self, description: str) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description}</title>
</head>
<body>
    <h1>{description}</h1>
    <!-- TODO: Implement -->
</body>
</html>'''

    def _explain_code(self, code: str) -> str:
        """Provide basic code explanation."""
        lines = code.strip().split("\n")
        explanation_parts = []

        explanation_parts.append(f"Code structure ({len(lines)} lines):")

        has_function = any(kw in code for kw in ["def ", "function ", "fn "])
        has_class = any(kw in code for kw in ["class ", "class "])
        has_loop = any(kw in code for kw in ["for ", "while ", "forEach", ".map("])
        has_condition = any(kw in code for kw in ["if ", "else", "switch", "case"])
        has_import = any(kw in code for kw in ["import ", "from ", "require("])

        if has_import:
            explanation_parts.append("- Imports/dependencies detected")
        if has_class:
            explanation_parts.append("- Contains class definition(s)")
        if has_function:
            explanation_parts.append("- Contains function(s)")
        if has_loop:
            explanation_parts.append("- Contains loop(s)")
        if has_condition:
            explanation_parts.append("- Contains conditional logic")

        imports = [l.strip() for l in lines if l.strip().startswith(("import ", "from ", "require("))]
        if imports:
            explanation_parts.append("\nImports:")
            for imp in imports:
                explanation_parts.append(f"  {imp}")

        functions = re.findall(r"(?:def |function\s+)(\w+)", code)
        if functions:
            explanation_parts.append(f"\nFunctions: {', '.join(functions)}")

        classes = re.findall(r"class\s+(\w+)", code)
        if classes:
            explanation_parts.append(f"\nClasses: {', '.join(classes)}")

        return "\n".join(explanation_parts)

    def _analyze_issues(self, code: str) -> str:
        """Analyze code for common issues."""
        issues = []

        if "eval(" in code:
            issues.append("[WARNING] Use of eval() is a security risk")
        if "exec(" in code:
            issues.append("[WARNING] Use of exec() is a security risk")
        if "import os" in code and "subprocess" not in code:
            issues.append("[INFO] Consider using subprocess instead of os.system")
        if "except:" in code:
            issues.append("[WARNING] Bare except clause - use 'except Exception:' instead")
        if "global " in code:
            issues.append("[INFO] Use of global variables - consider refactoring")
        if len(code.split("\n")) > 100:
            issues.append("[INFO] Long function/file - consider splitting")

        for line_num, line in enumerate(code.split("\n"), 1):
            if len(line) > 120:
                issues.append(f"[STYLE] Line {line_num} exceeds 120 characters")

        if not issues:
            return "No obvious issues detected. Code looks clean."

        return "\n".join(issues)

    def _run_git_command(self, command: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self._workspace,
            )
            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode == 0:
                return {
                    "success": True,
                    "response": f"Git {command}:\n\n{output}" if output else f"Git {command}: completed successfully",
                }
            else:
                return {
                    "success": False,
                    "response": f"Git {command} failed:\n{error}",
                }
        except FileNotFoundError:
            return {"success": False, "response": "Git is not installed or not in PATH."}
        except Exception as e:
            return {"success": False, "response": f"Git command failed: {str(e)}", "error": str(e)}

    def _analyze_directory(self, path: Path) -> str:
        """Analyze a directory for code statistics."""
        file_extensions = {}
        total_files = 0
        total_size = 0

        for root, dirs, files in os.walk(path):
            if any(skip in root for skip in [".git", "node_modules", "__pycache__", ".venv", "venv"]):
                continue
            for f in files:
                ext = os.path.splitext(f)[1] or "no extension"
                file_extensions[ext] = file_extensions.get(ext, 0) + 1
                total_files += 1
                try:
                    total_size += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass

        size_str = f"{total_size / 1024:.1f}KB" if total_size < 1024 * 1024 else f"{total_size / (1024 * 1024):.1f}MB"

        lines = [f"Repository analysis: {path}", "", f"Total files: {total_files}", f"Total size: {size_str}", ""]
        lines.append("File types:")
        for ext, count in sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"  {ext}: {count} files")

        return "\n".join(lines)

    def _detect_language(self, description: str) -> str:
        desc_lower = description.lower()
        if "python" in desc_lower:
            return "python"
        elif "javascript" in desc_lower or "js" in desc_lower:
            return "javascript"
        elif "typescript" in desc_lower or "ts" in desc_lower:
            return "typescript"
        elif "html" in desc_lower:
            return "html"
        elif "css" in desc_lower:
            return "css"
        return self._default_lang

    def _extract_file_path(self, command: str) -> Optional[str]:
        match = re.search(r"([a-zA-Z]:\\[\w\\.\-]+|/[\w/.\\-]+|[\w.\-/]+\\?\.\w+)", command)
        return match.group(1) if match else None

    def _extract_path(self, command: str) -> Optional[str]:
        match = re.search(r"([a-zA-Z]:\\[\w\\.\-]+|/[\w/.\\-]+)", command)
        return match.group(1) if match else None

    def _slugify(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

    def _camel_case(self, text: str) -> str:
        words = re.findall(r"[a-z0-9]+", text.lower())
        return "".join(w.capitalize() for w in words) if words else "Item"
