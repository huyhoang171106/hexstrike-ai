"""
CTF Hard Challenge Solver - Core Solver Classes

This module provides functionality to check the availability of various CTF tools
across different categories (pwn, crypto, forensics, re, web, osint, stego, misc).
It handles both system commands and Python modules used in Capture The Flag competitions.

Classes:
- ToolAvailabilityChecker: Check availability of CTF tools
- HardChallengeAnalyzer: AI-powered analysis of CTF challenge files
- ProgressiveHintSystem: Progressive hint system for challenges
- AutoSolverEngine: Auto-solver with parallel technique execution
- TechniquePatternLibrary: Pattern library for hard challenge techniques
"""

import shutil
import importlib
import sys
import os
import subprocess
from typing import Dict, Any, List, Optional


# Tool categories mapping tool names to their respective categories
TOOL_CATEGORIES: Dict[str, List[str]] = {
    "pwn": ["pwntools", "checksec", "ROPgadget", "one_gadget", "pwninit"],
    "crypto": ["openssl", "python3", "sage"],
    "forensics": ["volatility", "foremost", "photorec", "steghide", "zsteg"],
    "re": ["ghidra", "radare2", "objdump", "strings", "file"],
    "web": ["python3", "curl", "jq"],
    "osint": ["theHarvester", "subfinder"],
    "stego": ["steghide", "zsteg", "foremost", "exiftool"],
    "misc": ["strings", "xxd", "hexdump", "base64"]
}

# Python modules that need special import checking
PYTHON_MODULES: set = {"pwntools", "z3", "angr"}


class ToolAvailabilityChecker:
    """
    A class to check the availability of CTF tools on the system.

    Supports checking:
    - System commands (via shutil.which())
    - Python modules (via importlib)

    Categories: pwn, crypto, forensics, re, web, osint, stego, misc
    """

    def __init__(self) -> None:
        """Initialize the ToolAvailabilityChecker."""
        self.tool_categories = TOOL_CATEGORIES

    def check_tool(self, tool_name: str) -> Dict[str, Any]:
        """
        Check if a specific tool is available on the system.

        Args:
            tool_name: Name of the tool to check (can be system command or Python module)

        Returns:
            Dictionary containing:
                - available: bool indicating if tool is available
                - tool: str the tool name
                - message: str describing the availability status
        """
        # Handle Python modules specially
        if tool_name in PYTHON_MODULES:
            return self._check_python_module(tool_name)

        # Check for system command
        tool_path = shutil.which(tool_name)

        if tool_path:
            return {
                "available": True,
                "tool": tool_name,
                "message": f"Found: {tool_path}"
            }
        else:
            return {
                "available": False,
                "tool": tool_name,
                "message": f"Tool '{tool_name}' not found. Install it with: apt install {tool_name} or pip install {tool_name}"
            }

    def _check_python_module(self, module_name: str) -> Dict[str, Any]:
        """
        Check if a Python module is importable.

        Args:
            module_name: Name of the Python module to check

        Returns:
            Dictionary with availability status
        """
        try:
            # Handle special case for z3 (it's actually importable as z3)
            if module_name == "z3":
                importlib.import_module("z3")
            else:
                importlib.import_module(module_name)

            return {
                "available": True,
                "tool": module_name,
                "message": f"Python module '{module_name}' is installed and importable"
            }
        except ImportError:
            return {
                "available": False,
                "tool": module_name,
                "message": f"Python module '{module_name}' not found. Install it with: pip install {module_name}"
            }

    def get_category_tools(self, category: str) -> List[str]:
        """
        Return list of tools for a specific category.

        Args:
            category: The category name (case-insensitive)

        Returns:
            List of tool names for the category, empty list if category not found
        """
        # Handle case-insensitive category names
        category_lower = category.lower()

        if category_lower in self.tool_categories:
            return self.tool_categories[category_lower]

        return []

    def check_category(self, category: str) -> Dict[str, Any]:
        """
        Check availability of all tools in a category.

        Args:
            category: The category name to check (case-insensitive)

        Returns:
            Dictionary containing:
                - category: str the category name
                - available_tools: List of available tool names
                - missing_tools: List of missing tool names
                - all_available: bool True if all tools are available
                - details: Dict mapping tool names to their check results
        """
        category_lower = category.lower()

        if category_lower not in self.tool_categories:
            return {
                "category": category,
                "available_tools": [],
                "missing_tools": [],
                "all_available": False,
                "details": {},
                "error": f"Unknown category: {category}"
            }

        tools = self.tool_categories[category_lower]
        available_tools = []
        missing_tools = []
        details = {}

        for tool in tools:
            result = self.check_tool(tool)
            details[tool] = result

            if result["available"]:
                available_tools.append(tool)
            else:
                missing_tools.append(tool)

        return {
            "category": category,
            "available_tools": available_tools,
            "missing_tools": missing_tools,
            "all_available": len(missing_tools) == 0,
            "details": details
        }


class HardChallengeAnalyzer:
    """AI-powered analysis of CTF challenge files"""

    CATEGORY_PATTERNS = {
        "pwn": {
            "keywords": ["binary", "executable", "elf", "buffer", "overflow", "rop", "libc"],
            "file_extensions": [""],  # ELF has no extension usually
            "tools": ["file", "checksec", "strings"]
        },
        "crypto": {
            "keywords": ["encrypt", "decrypt", "cipher", "key", "rsa", "aes", "xor", "flag"],
            "file_extensions": [".txt", ".enc", ".py"],
            "tools": ["openssl"]
        },
        "forensics": {
            "keywords": ["memory", "disk", "image", "dump", "carve"],
            "file_extensions": [".mem", ".raw", ".dd", ".img", ".zip"],
            "tools": ["foremost", "volatility"]
        },
        "re": {
            "keywords": ["reverse", "binary", "disassemble"],
            "file_extensions": [".exe", ".dll", ".so", ".apk"],
            "tools": ["ghidra", "radare2", "objdump"]
        },
        "web": {
            "keywords": ["http", "web", "api", "sql", "xss"],
            "file_extensions": [".php", ".js", ".html", ".txt"],
            "tools": ["curl"]
        },
        "stego": {
            "keywords": ["image", "png", "jpg", "hidden", "steganography"],
            "file_extensions": [".png", ".jpg", ".jpeg", ".bmp", ".wav"],
            "tools": ["steghide", "zsteg", "exiftool"]
        }
    }

    TECHNIQUE_RECOMMENDATIONS = {
        "pwn": {
            "low": ["buffer_overflow", "ret2libc", "ret2win"],
            "medium": ["rop_chain", "format_string", "partial_overwrite"],
            "high": ["heap_exploitation", "house_of_spirit", "house_of_lore", "format_plunder"]
        },
        "crypto": {
            "low": ["frequency_analysis", "xor_breaking"],
            "medium": ["rsa_attacks", "ecb_mode"],
            "high": ["lattice_attacks", "Bleichenbacher", "padding_oracle"]
        }
    }

    def __init__(self):
        """Initialize the HardChallengeAnalyzer."""
        self.tool_checker = ToolAvailabilityChecker()

    def analyze_binary(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a binary challenge.

        Args:
            file_path: Path to the binary file
            metadata: Dictionary containing strings, imports, protections, etc.

        Returns:
            Dictionary with category, difficulty, protections, suggested_techniques, recommended_tools
        """
        category = self._detect_category(metadata.get("strings", []), metadata.get("imports", []))

        # Check protections
        protections = metadata.get("protections", {})
        difficulty = self._estimate_difficulty(protections)

        # Get available techniques
        available_techniques = self._get_available_techniques(category, difficulty)

        return {
            "category": category,
            "difficulty": difficulty,
            "protections": protections,
            "suggested_techniques": available_techniques,
            "recommended_tools": self.tool_checker.check_category(category)
        }

    def analyze_file_type(self, file_path: str) -> Dict[str, Any]:
        """
        Detect file type and suggest category.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file_type and suggested_category
        """
        if not os.path.exists(file_path):
            # For remote challenges, use filename hints
            basename = os.path.basename(file_path)
            for category, patterns in self.CATEGORY_PATTERNS.items():
                if any(kw in basename.lower() for kw in patterns["keywords"]):
                    return {"file_type": "unknown", "suggested_category": category, "filename_hint": True}

            return {"file_type": "unknown", "suggested_category": "misc"}

        # Run file command
        try:
            result = subprocess.run(["file", file_path], capture_output=True, text=True, timeout=5)
            file_output = result.stdout.lower()
        except:
            file_output = ""

        # Detect type
        file_type = "binary"
        if "png" in file_output or "jpeg" in file_output or "image" in file_output:
            file_type = "image"
        elif "zip" in file_output or "gzip" in file_output:
            file_type = "archive"
        elif "text" in file_output:
            file_type = "text"

        # Suggest category
        suggested_category = "misc"
        for category, patterns in self.CATEGORY_PATTERNS.items():
            if any(kw in file_output for kw in patterns["keywords"]):
                suggested_category = category
                break

        return {"file_type": file_type, "suggested_category": suggested_category}

    def _detect_category(self, strings: List[str], imports: List[str]) -> str:
        """Detect challenge category from strings/imports"""
        text = " ".join(strings + imports).lower()

        scores = {}
        for category, patterns in self.CATEGORY_PATTERNS.items():
            score = sum(1 for kw in patterns["keywords"] if kw in text)
            scores[category] = score

        if not scores or max(scores.values()) == 0:
            return "misc"

        return max(scores, key=scores.get)

    def _estimate_difficulty(self, protections: Dict[str, Any]) -> str:
        """Estimate challenge difficulty from protections"""
        # Hard if PIE + NX + canary are all enabled
        if protections.get("pie") and protections.get("nx") and protections.get("canary"):
            return "high"
        elif protections.get("pie") or protections.get("nx"):
            return "medium"
        return "low"

    def _get_available_techniques(self, category: str, difficulty: str) -> List[str]:
        """Get techniques available for category/difficulty"""
        category_techniques = self.TECHNIQUE_RECOMMENDATIONS.get(category, {})
        all_techniques = []

        # Include techniques up to difficulty level
        difficulty_order = ["low", "medium", "high"]
        max_level = difficulty_order.index(difficulty) + 1

        for level in difficulty_order[:max_level]:
            techniques = category_techniques.get(level, [])
            all_techniques.extend(techniques)

        return all_techniques


class ProgressiveHintSystem:
    """Progressive hint system for CTF challenges with 3-level hints."""

    HINT_DATABASE = {
        "pwn": {
            1: [  # Direction hints
                "Try analyzing the binary protections first",
                "Check for buffer overflow vulnerabilities",
                "Look for format string opportunities",
                "Consider heap exploitation if heap-related functions exist"
            ],
            2: [  # Method hints
                "Use ROP chain with libc gadgets (ret2libc)",
                "Try overwriting GOT entries",
                "Format string: %n to write arbitrary values",
                "Heap: Try house of spirit technique"
            ],
            3: [  # Technique hints
                "Overflow the buffer at offset 64, then overwrite saved RBP with pop rdi; ret gadget",
                "Use fmtstr_payload to write address of system@got",
                "Create fake chunk in .bss, then fastbin attack"
            ]
        },
        "crypto": {
            1: [
                "Check for classical cipher techniques",
                "Look for XOR with repeating key",
                "Check if RSA parameters are weak"
            ],
            2: [
                "Try frequency analysis for substitution ciphers",
                "Check for common RSA attacks: Wiener's, Boneh-Durfee",
                "Look for ECB mode oracle"
            ],
            3: [
                "Lattice attack on small RSA e",
                "Padding oracle attack on AES-CBC",
                "Bleichenbacher attack on RSA PKCS#1 v1.5"
            ]
        },
        "forensics": {
            1: [
                "Check file headers and magic bytes",
                "Run strings to find hidden data",
                "Check for steganography in images"
            ],
            2: [
                "Extract embedded files with binwalk",
                "Analyze memory dump with volatility",
                "Check for hidden partitions"
            ],
            3: [
                "Carve files from raw disk image",
                "Reconstruct deleted files from memory",
                "Analyze encrypted containers"
            ]
        },
        "re": {
            1: [
                "Identify the file type and architecture",
                "Look for interesting strings",
                "Check for encoded/encrypted sections"
            ],
            2: [
                "Graph the control flow in Ghidra",
                "Identify encryption algorithms used",
                "Find the decryption routine"
            ],
            3: [
                "Unpack packed malware manually",
                "Reconstruct algorithms from assembly",
                "Bypass anti-debugging checks"
            ]
        },
        "stego": {
            1: [
                "Check file metadata with exiftool",
                "Try steghide with empty password",
                "Examine least significant bits"
            ],
            2: [
                "Use zsteg for PNG/BMP analysis",
                "Check for multiple images stacked",
                "Audio steganography: spectrogram analysis"
            ],
            3: [
                "Advanced: OutGuess for JPEG",
                "LSB matching analysis",
                "Deep dive into compression artifacts"
            ]
        },
        "web": {
            1: [
                "Check for SQL injection points",
                "Look for XSS vulnerabilities",
                "Test for IDOR"
            ],
            2: [
                "Time-based blind SQL injection",
                "DOM-based XSS exploitation",
                "SSRF to internal services"
            ],
            3: [
                "HTTP desync attacks",
                "JWT algorithm confusion",
                "Prototype pollution exploitation"
            ]
        }
    }

    def __init__(self):
        """Initialize the ProgressiveHintSystem."""
        self.progress: Dict[str, Dict[str, Any]] = {}

    def get_hint(self, category: str, level: int, techniques_tried: List[str]) -> Dict[str, Any]:
        """
        Get a hint at the specified level.

        Args:
            category: CTF category (pwn, crypto, forensics, etc.)
            level: Hint level (1=direction, 2=method, 3=technique)
            techniques_tried: List of techniques already attempted

        Returns:
            Dictionary with hint details
        """
        category_hints = self.HINT_DATABASE.get(category.lower(), self.HINT_DATABASE["pwn"])

        # Get hints at requested level
        hints = category_hints.get(level, [])

        if not hints:
            # Fallback to level 1
            hints = category_hints.get(1, ["Keep analyzing the challenge"])

        # Select hint based on techniques tried (avoid repeating)
        hint = hints[len(techniques_tried) % len(hints)] if hints else "Keep trying"

        hint_type = {1: "direction", 2: "method", 3: "technique"}.get(level, "direction")

        return {
            "level": level,
            "hint_type": hint_type,
            "hint": hint,
            "techniques_tried": techniques_tried,
            "next_suggestion": self._get_next_suggestion(category, level, techniques_tried)
        }

    def record_attempt(self, challenge_id: str, technique: str, result: str):
        """
        Record an attempt on a challenge.

        Args:
            challenge_id: Unique identifier for the challenge
            technique: Technique that was attempted
            result: Result of the attempt (success/failed/partial)
        """
        if challenge_id not in self.progress:
            self.progress[challenge_id] = {
                "attempts": 0,
                "techniques_tried": [],
                "results": [],
                "hints_requested": 0
            }

        self.progress[challenge_id]["attempts"] += 1
        self.progress[challenge_id]["techniques_tried"].append(technique)
        self.progress[challenge_id]["results"].append(result)

    def get_progress(self, challenge_id: str) -> Dict[str, Any]:
        """
        Get progress for a challenge.

        Args:
            challenge_id: Unique identifier for the challenge

        Returns:
            Dictionary with progress details
        """
        if challenge_id not in self.progress:
            return {
                "challenge_id": challenge_id,
                "attempts": 0,
                "techniques_tried": [],
                "results": [],
                "hints_requested": 0
            }

        return self.progress[challenge_id]

    def _get_next_suggestion(self, category: str, level: int, techniques_tried: List[str]) -> str:
        """Get next suggestion based on current state."""
        if level < 3:
            return f"Request level {level + 1} hint when ready"
        return "Consider trying different techniques or asking for analysis"


class AutoSolverEngine:
    """Auto-solver for CTF challenges with parallel technique execution."""

    TECHNIQUE_COMMANDS = {
        "pwn": {
            "ret2libc": [
                "ROPgadget --binary {target} | grep 'pop rdi'",
                "objdump -d {target} | grep system"
            ],
            "rop_chain": [
                "python3 -c 'from pwn import *; p = process(\"{target}\")'"
            ],
            "format_string": [
                "python3 -c 'from pwn import *; p = process(\"{target}\"); p.sendline(payload)'"
            ]
        },
        "crypto": {
            "frequency_analysis": [
                "python3 -c \"import string; text = open('{target}').read(); print(sorted(((c, text.count(c)) for c in string.ascii_letters), key=lambda x: -x[1]))\""
            ],
            "xor_breaking": [
                "python3 -c 'from pwn import *; from Crypto.Util.number import *'"
            ]
        },
        "forensics": {
            "file_extraction": [
                "foremost -v {target}",
                "binwalk -e {target}"
            ],
            "memory_analysis": [
                "volatility -f {target} imageinfo",
                "volatility -f {target} pslist"
            ]
        },
        "stego": {
            "steghide_extract": [
                "steghide extract -sf {target} -p ''",
                "steghide extract -sf {target} -p '{password}'"
            ],
            "zsteg_analysis": [
                "zsteg -a {target}",
                "zsteg -E {target}"
            ]
        }
    }

    def __init__(self, analyzer: HardChallengeAnalyzer, tool_checker: ToolAvailabilityChecker):
        """Initialize the AutoSolverEngine."""
        self.analyzer = analyzer
        self.tool_checker = tool_checker
        self.timeout = 120  # seconds per technique
        self.max_parallel = 4

    def auto_solve(self, challenge_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to automatically solve a challenge.

        Args:
            challenge_info: Dictionary with category, target, difficulty

        Returns:
            Dictionary with status, flag, techniques_tried, results
        """
        category = challenge_info.get("category", "misc")
        target = challenge_info.get("target", "")
        difficulty = challenge_info.get("difficulty", "medium")

        # Get techniques to try
        techniques = self._get_techniques_for_category(category, difficulty)

        # Check tool availability for each technique
        available_techniques = []
        for tech in techniques:
            if self._check_technique_tools(tech):
                available_techniques.append(tech)
            else:
                print(f"Skipping {tech} - required tools not available")

        if not available_techniques:
            return {
                "status": "failed",
                "reason": "No techniques available - required tools missing",
                "flag_found": False
            }

        # Try techniques in parallel
        results = self._try_techniques_parallel(available_techniques, target)

        # Check for flag in results
        flag = self._extract_flag_from_results(results)

        return {
            "status": "success" if flag else "incomplete",
            "flag_found": flag is not None,
            "flag": flag,
            "techniques_tried": available_techniques,
            "results": results
        }

    def get_technique_commands(self, category: str, technique: str) -> List[str]:
        """Get command lines for a specific technique."""
        tech_commands = self.TECHNIQUE_COMMANDS.get(category.lower(), {})
        return tech_commands.get(technique, [])

    def _get_techniques_for_category(self, category: str, difficulty: str) -> List[str]:
        """Get techniques to try for category/difficulty."""
        recommendations = self.analyzer.TECHNIQUE_RECOMMENDATIONS.get(category.lower(), {})

        techniques = []
        difficulty_order = ["low", "medium", "high"]
        max_level = difficulty_order.index(difficulty) + 1

        for level in difficulty_order[:max_level]:
            techniques.extend(recommendations.get(level, []))

        return techniques

    def _check_technique_tools(self, technique: str) -> bool:
        """Check if tools required for technique are available."""
        # Map technique to required tools
        technique_tools = {
            "ret2libc": ["ROPgadget", "objdump", "pwntools"],
            "rop_chain": ["pwntools"],
            "format_string": ["pwntools"],
            "frequency_analysis": ["python3"],
            "xor_breaking": ["python3"],
            "file_extraction": ["foremost", "binwalk"],
            "memory_analysis": ["volatility"],
            "steghide_extract": ["steghide"],
            "zsteg_analysis": ["zsteg"]
        }

        required = technique_tools.get(technique, [])

        for tool in required:
            if not self.tool_checker.check_tool(tool)["available"]:
                return False

        return True

    def _try_techniques_parallel(self, techniques: List[str], target: str) -> Dict[str, Any]:
        """Try multiple techniques in parallel."""
        results = {}

        def try_technique(tech):
            try:
                # Get commands for this technique from pwn category (simplified)
                commands = self.get_technique_commands("pwn", tech)
                if not commands:
                    commands = self.get_technique_commands(tech, tech)
                outputs = []
                for cmd in commands:
                    try:
                        cmd_formatted = cmd.format(target=target)
                        result = subprocess.run(
                            cmd_formatted,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=self.timeout
                        )
                        outputs.append({
                            "command": cmd_formatted,
                            "stdout": result.stdout[:1000],  # Limit output
                            "stderr": result.stderr[:500],
                            "returncode": result.returncode
                        })
                    except subprocess.TimeoutExpired:
                        outputs.append({"command": cmd, "error": "timeout"})
                    except Exception as e:
                        outputs.append({"command": cmd, "error": str(e)})
                return tech, outputs
            except Exception as e:
                return tech, [{"error": str(e)}]

        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
                futures = {executor.submit(try_technique, tech): tech for tech in techniques}

                for future in as_completed(futures, timeout=self.timeout + 10):
                    try:
                        tech, output = future.result()
                        results[tech] = output
                    except Exception as e:
                        pass  # Technique failed
        except ImportError:
            # Fallback to sequential if ThreadPoolExecutor not available
            for tech in techniques:
                tech, output = try_technique(tech)
                results[tech] = output

        return results

    def _extract_flag_from_results(self, results: Dict[str, Any]) -> Optional[str]:
        """Extract flag from technique results."""
        import re

        flag_patterns = [
            r"flag\{[^}]+\}",
            r"FLAG\{[^}]+\}",
            r"ctf\{[^}]+\}",
            r"CTF\{[^}]+\}"
        ]

        for tech, outputs in results.items():
            if isinstance(outputs, list):
                for output in outputs:
                    if isinstance(output, dict):
                        text = output.get("stdout", "") + output.get("stderr", "")
                        for pattern in flag_patterns:
                            match = re.search(pattern, text)
                            if match:
                                return match.group(0)

        return None


class TechniquePatternLibrary:
    """Pattern library for hard CTF challenge techniques."""

    PATTERNS = {
        "pwn": {
            "ret2libc": {
                "name": "Return-to-libc",
                "description": "Overflow buffer to redirect execution to libc functions",
                "difficulty": "medium",
                "prerequisites": ["NX enabled", "know libc offset"],
                "steps": [
                    "1. Find buffer overflow offset with pattern create",
                    "2. Locate ROP gadgets (pop rdi; ret, etc.)",
                    "3. Find system() in libc",
                    "4. Find /bin/sh string in libc",
                    "5. Construct ROP chain: offset + pop_rdi + /bin/sh + system + exit"
                ],
                "tools": ["ROPgadget", "pwntools", "checksec"],
                "keywords": ["buffer overflow", "nx", "rop", "libc"]
            },
            "ret2win": {
                "name": "Return-to-win",
                "description": "Redirect to internal win function",
                "difficulty": "easy",
                "prerequisites": ["Win function exists in binary"],
                "steps": [
                    "1. Find offset to overwrite return address",
                    "2. Locate win function address with objdump",
                    "3. Overflow and jump to win"
                ],
                "tools": ["objdump", "pwntools"],
                "keywords": ["buffer overflow", "win function"]
            },
            "format_string": {
                "name": "Format String Exploitation",
                "description": "Use format string to read/write arbitrary memory",
                "difficulty": "medium",
                "prerequisites": ["Binary uses printf(user_input)"],
                "steps": [
                    "1. Test for format string vuln with %p %p %p",
                    "2. Find offset to user input on stack",
                    "3. Use %n to write to arbitrary addresses",
                    "4. Overwrite GOT entry or return address"
                ],
                "tools": ["pwntools"],
                "keywords": ["format string", "got", "printf"]
            },
            "heap_exploitation": {
                "name": "Heap Exploitation",
                "description": "Advanced heap manipulation techniques",
                "difficulty": "high",
                "prerequisites": ["Dynamic memory allocation", "No heap hardening"],
                "variants": ["house_of_spirit", "house_of_lore", "house_of_einherjar", "fastbin_attack"],
                "steps": [
                    "1. Understand heap allocator (ptmalloc2)",
                    "2. Create fake chunks",
                    "3. Trigger consolidation or fastbin attack",
                    "4. Overwrite __free_hook or __malloc_hook"
                ],
                "tools": ["pwntools", "glibc-all-in-one"],
                "keywords": ["heap", "malloc", "free hook", "chunk"]
            },
            "fastbin_attack": {
                "name": "Fastbin Attack",
                "description": "Target fastbin freelist for arbitrary allocation",
                "difficulty": "high",
                "prerequisites": ["Fastbin-sized allocations", "No fastbin consolidation"],
                "steps": [
                    "1. Allocate chunks and free them to fastbins",
                    "2. Create fake chunk in target region",
                    "3. Overwrite fd pointer in fastbin",
                    "4. Allocate to write primitive"
                ],
                "tools": ["pwntools", "gdb-gef"],
                "keywords": ["fastbin", "heap", "allocation"]
            }
        },
        "crypto": {
            "rsa_wiener": {
                "name": "Wiener's RSA Attack",
                "description": "Low d attack on RSA with small private exponent",
                "difficulty": "medium",
                "prerequisites": ["Small d (d < N^0.25)"],
                "steps": [
                    "1. Compute continued fraction expansion of e/n",
                    "2. Find convergent with k/d < 0.25",
                    "3. Recover d from convergent",
                    "4. Decrypt ciphertext"
                ],
                "tools": ["python3", "sage"],
                "keywords": ["rsa", "wiener", "continued fraction"]
            },
            "ecb_oracle": {
                "name": "ECB Oracle Attack",
                "description": "Block-level chosen plaintext attack on ECB mode",
                "difficulty": "medium",
                "prerequisites": ["ECB mode encryption", "Oracle that reveals info"],
                "steps": [
                    "1. Identify ECB mode (deterministic encryption)",
                    "2. Craft payloads to leak blocks",
                    "3. Byte-at-a-time decryption if needed"
                ],
                "tools": ["python3"],
                "keywords": ["aes", "ecb", "oracle", "block cipher"]
            }
        },
        "forensics": {
            "memory_dump": {
                "name": "Memory Forensics",
                "description": "Analyze memory dumps for secrets",
                "difficulty": "high",
                "prerequisites": ["Memory dump file"],
                "steps": [
                    "1. Identify OS profile with imageinfo",
                    "2. List processes with pslist",
                    "3. Scan for strings and passwords",
                    "4. Extract hidden data"
                ],
                "tools": ["volatility"],
                "keywords": ["memory", "forensics", "dump"]
            }
        }
    }

    def get_patterns(self, category: str) -> List[Dict[str, Any]]:
        """Get all patterns for a category."""
        return [
            {
                "name": data["name"],
                "difficulty": data["difficulty"],
                "description": data["description"],
                "keywords": data.get("keywords", [])
            }
            for name, data in self.PATTERNS.get(category.lower(), {}).items()
        ]

    def get_pattern_details(self, category: str, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a pattern."""
        return self.PATTERNS.get(category.lower(), {}).get(pattern_name)

    def search_patterns(self, keyword: str) -> List[Dict[str, Any]]:
        """Search patterns by keyword."""
        results = []
        for category, patterns in self.PATTERNS.items():
            for name, data in patterns.items():
                if keyword.lower() in " ".join(data.get("keywords", [])).lower():
                    results.append({
                        "category": category,
                        "name": name,
                        "difficulty": data.get("difficulty"),
                        "description": data.get("description")
                    })
        return results


if __name__ == "__main__":
    # Quick demonstration
    checker = ToolAvailabilityChecker()

    print("=== CTF Tool Availability Checker ===\n")

    # Test individual tool check
    print("Testing check_tool('python3'):")
    print(checker.check_tool("python3"))
    print()

    print("Testing check_tool('nonexistent_tool'):")
    print(checker.check_tool("nonexistent_tool_xyz"))
    print()

    # Test get_category_tools
    print("Testing get_category_tools('pwn'):")
    print(checker.get_category_tools("pwn"))
    print()

    # Test check_category
    print("Testing check_category('web'):")
    result = checker.check_category("web")
    print(f"Category: {result['category']}")
    print(f"Available: {result['available_tools']}")
    print(f"Missing: {result['missing_tools']}")
    print(f"All Available: {result['all_available']}")
