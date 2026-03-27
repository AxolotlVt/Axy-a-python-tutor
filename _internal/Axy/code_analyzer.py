"""
Code Analysis and Execution Module for Axy
Provides safe Python code analysis, execution, and correction capabilities.
"""
# ==============================================================================
# Copyright (c) 2026 Axo. All rights reserved.
# 
# This software is proprietary and confidential.
# Unauthorized copying, distribution, modification, or use of this file,
# via any medium, is strictly prohibited without the express written 
# consent of the developer.
# 
# AXY - Local Python Mentor
# ==============================================================================

import ast
import subprocess
import sys
import tempfile
import os
import logging
import signal
import psutil
from typing import Dict, List, Optional, Tuple, Any
import traceback
import io
import contextlib

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes Python code for syntax, structure, and potential issues."""

    def __init__(self):
        self.issues = []

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code and return detailed feedback."""
        self.issues = []

        try:
            # Parse the AST
            tree = ast.parse(code)
            self._analyze_ast(tree)

            # Check for common issues
            self._check_common_issues(code, tree)

            return {
                "valid": True,
                "issues": self.issues,
                "complexity": self._calculate_complexity(tree),
                "structure": self._analyze_structure(tree)
            }

        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax Error: {e.msg} at line {e.lineno}",
                "issues": [{"type": "syntax", "message": str(e), "line": e.lineno}]
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Analysis Error: {str(e)}",
                "issues": [{"type": "analysis", "message": str(e)}]
            }

    def _analyze_ast(self, tree: ast.AST) -> None:
        """Analyze the AST for code quality issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) == 0:
                    self.issues.append({
                        "type": "warning",
                        "message": f"Function '{node.name}' is empty",
                        "line": node.lineno
                    })

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'sys']:
                        self.issues.append({
                            "type": "security",
                            "message": f"Potentially unsafe import: {alias.name}",
                            "line": node.lineno
                        })

            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load) and node.id == '__builtins__':
                    self.issues.append({
                        "type": "warning",
                        "message": "Accessing __builtins__ may be unsafe",
                        "line": getattr(node, 'lineno', 'unknown')
                    })

    def _check_common_issues(self, code: str, tree: ast.AST) -> None:
        """Check for common Python coding issues."""
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for print statements without parentheses (Python 2 style)
            if 'print ' in line and 'print(' not in line:
                self.issues.append({
                    "type": "compatibility",
                    "message": "Print statement without parentheses (use print() for Python 3)",
                    "line": i
                })

            # Check for very long lines
            if len(line) > 100:
                self.issues.append({
                    "type": "style",
                    "message": f"Line too long ({len(line)} characters)",
                    "line": i
                })

            # Check for potentially dangerous patterns
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in ['while true', 'for _ in iter', 'memory', 'fork']):
                if 'while true' in line_lower and 'break' not in line_lower:
                    self.issues.append({
                        "type": "warning",
                        "message": "Potential infinite loop detected",
                        "line": i
                    })
                elif 'fork' in line_lower:
                    self.issues.append({
                        "type": "security",
                        "message": "Process forking is not allowed",
                        "line": i
                    })

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate code complexity metrics."""
        functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        loops = len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))])
        conditionals = len([node for node in ast.walk(tree) if isinstance(node, ast.If)])

        return {
            "functions": functions,
            "classes": classes,
            "loops": loops,
            "conditionals": conditionals
        }

    def _analyze_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code structure."""
        return {
            "has_main": any(isinstance(node, ast.If) and
                          isinstance(node.test, ast.Compare) and
                          len(node.test.comparators) == 1 and
                          isinstance(node.test.comparators[0], ast.Name) and
                          node.test.comparators[0].id == "__name__"
                          for node in ast.walk(tree)),
            "imports": [node.names[0].name for node in ast.walk(tree)
                       if isinstance(node, ast.Import) for alias in node.names],
            "functions": [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        }


class CodeExecutor:
    """Safely executes Python code with timeout and restrictions."""

    def __init__(self, timeout: int = 10, memory_limit_mb: int = 50, recursion_limit: int = 100):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.recursion_limit = recursion_limit
        self.allowed_modules = {
            'math', 'random', 'datetime', 'collections', 'itertools',
            'functools', 'operator', 'string', 're', 'json', 'typing'
        }

    def execute_code(self, code: str) -> Dict[str, Any]:
        """Execute Python code safely and return results."""
        process = None
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(self._add_safety_wrapper(code))
                temp_file = f.name

            try:
                # Execute with timeout and resource monitoring
                process = subprocess.Popen(
                    [sys.executable, temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(temp_file),
                    preexec_fn=self._set_process_limits if os.name != 'nt' else None
                )

                try:
                    # Monitor memory usage and enforce timeout
                    stdout, stderr = self._monitor_execution(process)

                    return {
                        "success": process.returncode == 0,
                        "stdout": stdout,
                        "stderr": stderr,
                        "returncode": process.returncode,
                        "timeout": False
                    }

                except subprocess.TimeoutExpired:
                    # Kill the process and any children
                    self._kill_process_tree(process.pid)
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": f"Code execution timed out after {self.timeout} seconds",
                        "returncode": -1,
                        "timeout": True
                    }

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass

        except Exception as e:
            # Kill process if it exists
            if process:
                try:
                    self._kill_process_tree(process.pid)
                except:
                    pass
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution setup error: {str(e)}",
                "returncode": -1,
                "timeout": False
            }

    def _set_process_limits(self):
        """Set resource limits for Unix-like systems."""
        try:
            import resource

            # Set memory limit (in bytes)
            memory_limit_bytes = self.memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))

            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))

            # Set recursion limit
            sys.setrecursionlimit(self.recursion_limit)

        except ImportError:
            # resource module not available on Windows
            pass
        except Exception as e:
            logger.warning(f"Could not set process limits: {e}")

    def _monitor_execution(self, process):
        """Monitor process execution with memory and timeout checks."""
        import time

        start_time = time.time()
        stdout_chunks = []
        stderr_chunks = []

        while True:
            # Check if process is still running
            if process.poll() is not None:
                break

            # Check timeout
            if time.time() - start_time > self.timeout:
                raise subprocess.TimeoutExpired(process.args, self.timeout)

            # Check memory usage (if psutil available)
            try:
                proc = psutil.Process(process.pid)
                memory_mb = proc.memory_info().rss / 1024 / 1024
                if memory_mb > self.memory_limit_mb:
                    logger.warning(f"Process {process.pid} exceeded memory limit ({memory_mb:.1f}MB)")
                    self._kill_process_tree(process.pid)
                    raise subprocess.TimeoutExpired(process.args, self.timeout)
            except ImportError:
                # psutil not available
                pass
            except Exception:
                # Process might have ended
                pass

            time.sleep(0.1)  # Small delay to avoid busy waiting

        # Get final output
        stdout, stderr = process.communicate(timeout=5)
        return stdout, stderr

    def _kill_process_tree(self, pid):
        """Kill a process and all its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            parent.kill()
        except psutil.NoSuchProcess:
            pass
        except ImportError:
            # psutil not available, fallback to basic kill
            try:
                os.kill(pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                pass

    def _add_safety_wrapper(self, code: str) -> str:
        """Add safety restrictions to the code."""
        safety_wrapper = f'''
import sys
import builtins

# Set recursion limit to prevent stack overflow
sys.setrecursionlimit({self.recursion_limit})

# Create a list of dangerous operations to block
blocked_operations = [
    'exec', 'eval', 'compile', '__import__', 'open', 'input',
    'subprocess', 'os.system', 'os.popen', 'sys.exit', 'fork'
]

# Override dangerous builtins with safe versions
def safe_exec(*args, **kwargs):
    raise RuntimeError("exec() is not allowed for security reasons")

def safe_eval(*args, **kwargs):
    raise RuntimeError("eval() is not allowed for security reasons")

def safe_compile(*args, **kwargs):
    raise RuntimeError("compile() is not allowed for security reasons")

def safe_import(name, *args, **kwargs):
    allowed_modules = {{
        'math', 'random', 'datetime', 'collections', 'itertools',
        'functools', 'operator', 'string', 're', 'json', 'typing'
    }}
    if name in allowed_modules:
        return __import__(name, *args, **kwargs)
    raise ImportError(f"Import of '{{name}}' is not allowed for security reasons")

def safe_open(*args, **kwargs):
    raise RuntimeError("File operations are not allowed for security reasons")

def safe_fork(*args, **kwargs):
    raise RuntimeError("Process forking is not allowed for security reasons")

# Replace dangerous functions
builtins.exec = safe_exec
builtins.eval = safe_eval
builtins.compile = safe_compile
builtins.__import__ = safe_import
builtins.open = safe_open
builtins.fork = safe_fork

# Block subprocess and os system calls
try:
    import subprocess
    subprocess.call = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("subprocess not allowed"))
    subprocess.run = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("subprocess not allowed"))
    subprocess.Popen = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("subprocess not allowed"))
except:
    pass

try:
    import os
    os.system = lambda *args: (_ for _ in ()).throw(RuntimeError("system calls not allowed"))
    os.popen = lambda *args: (_ for _ in ()).throw(RuntimeError("system calls not allowed"))
    os.execv = lambda *args: (_ for _ in ()).throw(RuntimeError("system calls not allowed"))
    os.execve = lambda *args: (_ for _ in ()).throw(RuntimeError("system calls not allowed"))
    os.spawnv = lambda *args: (_ for _ in ()).throw(RuntimeError("system calls not allowed"))
    os.fork = lambda *args: (_ for _ in ()).throw(RuntimeError("fork not allowed"))
except:
    pass

# Prevent infinite loops by limiting iterations
_loop_counter = 0
_original_range = builtins.range
def safe_range(*args):
    global _loop_counter
    _loop_counter += 1
    if _loop_counter > 10000:  # Prevent infinite loops
        raise RuntimeError("Loop iteration limit exceeded")
    return _original_range(*args)
builtins.range = safe_range

'''

        return safety_wrapper + "\n" + code


class CodeCorrector:
    """Provides intelligent code corrections based on analysis and execution results."""

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.executor = CodeExecutor()

    def analyze_and_correct(self, code: str) -> Dict[str, Any]:
        """Complete analysis, execution, and correction pipeline."""
        # First analyze the code
        analysis = self.analyzer.analyze_code(code)

        if not analysis["valid"]:
            return {
                "original_code": code,
                "analysis": analysis,
                "execution": None,
                "corrections": self._generate_syntax_corrections(analysis),
                "can_execute": False
            }

        # If code is valid, try to execute it
        execution = self.executor.execute_code(code)

        corrections = []
        if not execution["success"]:
            corrections.extend(self._generate_runtime_corrections(execution))

        corrections.extend(self._generate_improvement_suggestions(analysis))

        return {
            "original_code": code,
            "analysis": analysis,
            "execution": execution,
            "corrections": corrections,
            "can_execute": True
        }

    def _generate_syntax_corrections(self, analysis: Dict) -> List[Dict]:
        """Generate corrections for syntax errors."""
        corrections = []

        for issue in analysis.get("issues", []):
            if issue["type"] == "syntax":
                if "print" in issue["message"].lower():
                    corrections.append({
                        "type": "syntax_fix",
                        "description": "Convert print statement to function call",
                        "example": "Change: print 'hello' → print('hello')"
                    })

        return corrections

    def _generate_runtime_corrections(self, execution: Dict) -> List[Dict]:
        """Generate corrections for runtime errors."""
        corrections = []

        stderr = execution.get("stderr", "").lower()

        if "nameerror" in stderr:
            corrections.append({
                "type": "runtime_fix",
                "description": "Variable or function not defined - check spelling and scope",
                "suggestion": "Make sure all variables are defined before use"
            })

        elif "typeerror" in stderr:
            corrections.append({
                "type": "runtime_fix",
                "description": "Type mismatch - check data types",
                "suggestion": "Verify you're using compatible types for operations"
            })

        elif "indentationerror" in stderr:
            corrections.append({
                "type": "runtime_fix",
                "description": "Indentation problem - Python uses indentation for code blocks",
                "suggestion": "Use consistent indentation (4 spaces recommended)"
            })

        elif "zerodivisionerror" in stderr:
            corrections.append({
                "type": "runtime_fix",
                "description": "Division by zero",
                "suggestion": "Add check: if denominator != 0: ..."
            })

        return corrections

    def _generate_improvement_suggestions(self, analysis: Dict) -> List[Dict]:
        """Generate general improvement suggestions."""
        suggestions = []

        complexity = analysis.get("complexity", {})
        if complexity.get("functions", 0) == 0 and len(analysis.get("issues", [])) == 0:
            suggestions.append({
                "type": "improvement",
                "description": "Consider breaking code into functions for better organization",
                "suggestion": "Functions make code reusable and easier to test"
            })

        if complexity.get("loops", 0) > 3:
            suggestions.append({
                "type": "improvement",
                "description": "Many loops detected - consider using list comprehensions",
                "suggestion": "List comprehensions are often more readable: [x*2 for x in items]"
            })

        return suggestions


class PerformanceAnalyzer:
    """Analyzes code for performance characteristics and provides optimization suggestions."""

    def __init__(self):
        self.complexity_patterns = {
            # O(1) - Constant time
            'constant': ['dict[key]', 'list[index]', 'set.add', 'len()'],

            # O(log n) - Logarithmic
            'logarithmic': ['binary search', 'balanced tree'],

            # O(n) - Linear
            'linear': ['for _ in range', 'for item in list', 'while loop', 'list comprehension'],

            # O(n log n) - Linearithmic
            'linearithmic': ['sorted()', 'sort()', 'heapq', 'merge sort'],

            # O(n^2) - Quadratic
            'quadratic': ['nested for loops', 'bubble sort', 'insertion sort'],

            # O(2^n) - Exponential
            'exponential': ['fibonacci recursive', 'subset generation', 'towers of hanoi']
        }

    def analyze_performance(self, code: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code performance characteristics."""
        try:
            tree = ast.parse(code)
            complexity = self._estimate_complexity(tree, code)
            memory_usage = self._estimate_memory_usage(tree, code)
            suggestions = self._generate_performance_suggestions(tree, code, complexity)

            return {
                "complexity": complexity,
                "memory_estimate": memory_usage,
                "suggestions": suggestions,
                "bottlenecks": self._identify_bottlenecks(tree, code)
            }
        except Exception as e:
            return {
                "error": f"Performance analysis failed: {str(e)}",
                "complexity": {"estimated": "Unknown"},
                "memory_estimate": {"estimated_mb": 0},
                "suggestions": [],
                "bottlenecks": []
            }

    def _estimate_complexity(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Estimate algorithmic complexity using static analysis."""
        code_lower = code.lower()

        # Count nested loops (strong indicator of complexity)
        nested_loops = self._count_nested_loops(tree)
        total_loops = len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))])

        # Check for common patterns
        has_sorting = any(pattern in code_lower for pattern in ['sort(', 'sorted(', 'heapq'])
        has_search = any(pattern in code_lower for pattern in ['binary', 'search'])
        has_recursion = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and
                           any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and
                               n.func.id == node.name for n in ast.walk(node))]) > 0

        # Estimate complexity based on patterns
        if nested_loops >= 2:
            estimated = "O(n²) - Quadratic"
            explanation = f"Found {nested_loops} levels of nested loops"
        elif has_recursion and 'fibonacci' in code_lower:
            estimated = "O(2ⁿ) - Exponential"
            explanation = "Recursive Fibonacci suggests exponential complexity"
        elif has_sorting:
            estimated = "O(n log n) - Linearithmic"
            explanation = "Sorting algorithms are typically O(n log n)"
        elif has_search and 'binary' in code_lower:
            estimated = "O(log n) - Logarithmic"
            explanation = "Binary search is logarithmic"
        elif total_loops > 0:
            estimated = "O(n) - Linear"
            explanation = f"Found {total_loops} loop(s) suggesting linear complexity"
        else:
            estimated = "O(1) - Constant"
            explanation = "No loops found, likely constant time"

        return {
            "estimated": estimated,
            "explanation": explanation,
            "nested_loops": nested_loops,
            "total_loops": total_loops,
            "has_recursion": has_recursion,
            "has_sorting": has_sorting
        }

    def _count_nested_loops(self, tree: ast.AST) -> int:
        """Count the maximum nesting level of loops."""
        max_nesting = 0

        def count_nesting(node: ast.AST, current_depth: int = 0) -> None:
            nonlocal max_nesting

            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_nesting = max(max_nesting, current_depth)

            for child in ast.iter_child_nodes(node):
                count_nesting(child, current_depth)

        count_nesting(tree)
        return max_nesting

    def _estimate_memory_usage(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Estimate memory usage based on data structures and operations."""
        # Count data structure allocations
        lists = len([node for node in ast.walk(tree) if isinstance(node, ast.List)])
        dicts = len([node for node in ast.walk(tree) if isinstance(node, ast.Dict)])
        sets = len([node for node in ast.walk(tree) if isinstance(node, ast.Set)])

        # Estimate based on typical Python object sizes
        estimated_mb = (lists * 0.1 + dicts * 0.2 + sets * 0.15)  # Rough estimates

        # Check for large data structures
        large_structures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                # Check if list has many literals
                literals = [n for n in ast.walk(node) if isinstance(n, (ast.Num, ast.Str, ast.NameConstant))]
                if len(literals) > 10:
                    large_structures.append("Large list with many elements")
            elif isinstance(node, ast.Dict):
                keys_vals = [n for n in ast.walk(node) if isinstance(n, (ast.Num, ast.Str, ast.NameConstant))]
                if len(keys_vals) > 20:
                    large_structures.append("Large dictionary")

        return {
            "estimated_mb": round(estimated_mb, 2),
            "data_structures": {
                "lists": lists,
                "dicts": dicts,
                "sets": sets
            },
            "large_structures": large_structures
        }

    def _generate_performance_suggestions(self, tree: ast.AST, code: str, complexity: Dict) -> List[Dict]:
        """Generate performance improvement suggestions."""
        suggestions = []

        # Complexity-based suggestions
        if complexity.get("nested_loops", 0) >= 2:
            suggestions.append({
                "type": "optimization",
                "priority": "high",
                "title": "Consider reducing nested loops",
                "description": "Nested loops can create O(n²) or worse complexity",
                "suggestion": "Use more efficient algorithms like sorting first, or use data structures like sets/dicts for O(1) lookups"
            })

        if complexity.get("has_recursion", False):
            suggestions.append({
                "type": "optimization",
                "priority": "medium",
                "title": "Consider iterative solutions",
                "description": "Recursive functions can cause stack overflow and be slower",
                "suggestion": "Convert to iterative approach using loops and stacks"
            })

        # Code pattern suggestions
        code_lower = code.lower()
        if 'for _ in range(len(' in code_lower and 'for item in ' in code_lower:
            suggestions.append({
                "type": "optimization",
                "priority": "low",
                "title": "Use enumerate instead of range(len())",
                "description": "range(len()) is less Pythonic and can be error-prone",
                "suggestion": "Use: for i, item in enumerate(my_list):"
            })

        if 'list.append' in code_lower and 'for ' in code_lower:
            suggestions.append({
                "type": "optimization",
                "priority": "low",
                "title": "Consider list comprehensions",
                "description": "List comprehensions are often faster and more readable",
                "suggestion": "Change: result = []\nfor x in items:\n    result.append(x*2)\nTo: result = [x*2 for x in items]"
            })

        # Memory suggestions
        memory_info = self._estimate_memory_usage(tree, code)
        if memory_info["estimated_mb"] > 10:
            suggestions.append({
                "type": "memory",
                "priority": "medium",
                "title": "High memory usage detected",
                "description": f"Estimated memory usage: {memory_info['estimated_mb']}MB",
                "suggestion": "Consider processing data in chunks or using generators for large datasets"
            })

        return suggestions

    def _identify_bottlenecks(self, tree: ast.AST, code: str) -> List[Dict]:
        """Identify potential performance bottlenecks."""
        bottlenecks = []

        # Look for inefficient patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for nested loops
                has_nested = any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node))
                if has_nested:
                    bottlenecks.append({
                        "type": "nested_loops",
                        "line": getattr(node, 'lineno', 'unknown'),
                        "description": "Nested loop detected - potential O(n²) complexity"
                    })

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ['sorted', 'sort', 'list.sort']:
                        bottlenecks.append({
                            "type": "sorting",
                            "line": getattr(node, 'lineno', 'unknown'),
                            "description": "Sorting operation - O(n log n) complexity"
                        })

        return bottlenecks


# Global instances
code_analyzer = CodeAnalyzer()
code_executor = CodeExecutor(timeout=10, memory_limit_mb=50, recursion_limit=100)
code_corrector = CodeCorrector()
performance_analyzer = PerformanceAnalyzer()


def analyze_code_performance(code: str) -> Dict[str, Any]:
    """Convenience function to analyze code performance."""
    # First do basic analysis
    basic_analysis = code_analyzer.analyze_code(code)

    # Then add performance analysis
    performance_analysis = performance_analyzer.analyze_performance(code, basic_analysis)

    return {
        "basic_analysis": basic_analysis,
        "performance_analysis": performance_analysis
    }


def analyze_python_code(code: str) -> Dict[str, Any]:
    """Convenience function to analyze Python code."""
    return code_analyzer.analyze_code(code)


def execute_python_code(code: str) -> Dict[str, Any]:
    """Convenience function to execute Python code safely."""
    return code_executor.execute_code(code)


def analyze_and_correct_code(code: str) -> Dict[str, Any]:
    """Complete code analysis, execution, and correction."""
    return code_corrector.analyze_and_correct(code)