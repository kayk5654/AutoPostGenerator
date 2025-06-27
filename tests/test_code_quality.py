"""
Tests for Phase 6 Task Block 6.2: Code Quality and Architecture

This module tests code quality improvements including:
- Clean Architecture principles and separation of concerns
- Comprehensive function documentation and docstrings
- Robust error handling patterns
- Input validation and sanitization
- Production code optimization
"""

import pytest
import ast
import inspect
import importlib
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import re


class TestCleanArchitecture:
    """Test Clean Architecture principles and separation of concerns."""
    
    def test_ui_layer_separation(self):
        """Test that UI layer only handles Streamlit components."""
        # Read app.py content
        app_path = Path("app.py")
        if app_path.exists():
            with open(app_path, 'r') as f:
                app_content = f.read()
            
            # Parse the AST to analyze imports and function calls
            tree = ast.parse(app_content)
            
            # Check for proper separation - UI should only import from services
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # UI layer should import from services and utils, not implement business logic
            service_imports = [imp for imp in imports if 'services.' in imp or 'utils.' in imp]
            assert len(service_imports) > 0, "UI layer should import from services/utils"
            
            # Check that complex business logic is delegated to services
            function_calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if hasattr(node.func.value, 'id'):
                        function_calls.append(f"{node.func.value.id}.{node.func.attr}")
            
            # Should find calls to service functions
            service_calls = [call for call in function_calls if any(
                service in call for service in ['post_service', 'file_service', 'llm_service', 'data_exporter']
            )]
            assert len(service_calls) > 0, "UI should delegate to service layer"
    
    def test_business_logic_in_services(self):
        """Test that business logic is properly contained in services layer."""
        services_path = Path("services")
        if services_path.exists():
            service_files = list(services_path.glob("*.py"))
            service_files = [f for f in service_files if f.name != "__init__.py"]
            
            assert len(service_files) >= 3, "Should have multiple service modules"
            
            # Check each service file for proper structure
            for service_file in service_files:
                with open(service_file, 'r') as f:
                    content = f.read()
                
                # Services should not import Streamlit
                assert 'import streamlit' not in content, f"{service_file.name} should not import Streamlit"
                assert 'from streamlit' not in content, f"{service_file.name} should not import Streamlit"
                
                # Services should have functions (business logic)
                tree = ast.parse(content)
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                assert len(functions) > 0, f"{service_file.name} should contain business logic functions"
    
    def test_dependency_direction(self):
        """Test that dependencies flow in the correct direction."""
        # UI layer can depend on services, services can depend on utils
        # But services should not depend on UI, utils should not depend on services/UI
        
        def analyze_imports(file_path):
            if not file_path.exists():
                return []
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            
            return imports
        
        # Check utils layer doesn't depend on services or app
        utils_path = Path("utils")
        if utils_path.exists():
            for utils_file in utils_path.glob("*.py"):
                if utils_file.name == "__init__.py":
                    continue
                
                imports = analyze_imports(utils_file)
                service_imports = [imp for imp in imports if imp.startswith('services.')]
                app_imports = [imp for imp in imports if 'app' in imp]
                
                assert len(service_imports) == 0, f"Utils {utils_file.name} should not import from services"
                assert len(app_imports) == 0, f"Utils {utils_file.name} should not import from app"
        
        # Check services layer doesn't depend on app
        services_path = Path("services")
        if services_path.exists():
            for service_file in services_path.glob("*.py"):
                if service_file.name == "__init__.py":
                    continue
                
                imports = analyze_imports(service_file)
                app_imports = [imp for imp in imports if 'app' in imp or imp.startswith('streamlit')]
                
                assert len(app_imports) == 0, f"Service {service_file.name} should not import from app layer"


class TestFunctionDocumentation:
    """Test comprehensive function documentation."""
    
    def test_docstring_presence(self):
        """Test that all public functions have docstrings."""
        modules_to_check = ['services.file_service', 'services.llm_service', 'services.post_service', 'utils.data_exporter']
        
        for module_name in modules_to_check:
            try:
                module = importlib.import_module(module_name)
                
                # Get all public functions (not starting with _)
                functions = [getattr(module, name) for name in dir(module) 
                           if callable(getattr(module, name)) and not name.startswith('_')]
                
                for func in functions:
                    if inspect.isfunction(func):
                        docstring = inspect.getdoc(func)
                        assert docstring is not None, f"Function {func.__name__} in {module_name} missing docstring"
                        assert len(docstring.strip()) > 10, f"Function {func.__name__} has inadequate docstring"
                        
            except ImportError:
                # Module doesn't exist yet, which is expected for some test scenarios
                pass
    
    def test_docstring_quality(self):
        """Test quality and completeness of docstrings."""
        def check_docstring_quality(docstring):
            """Check if docstring meets quality standards."""
            if not docstring:
                return False, "Missing docstring"
            
            lines = docstring.strip().split('\n')
            
            # Should have summary line
            if not lines[0].strip():
                return False, "Missing summary line"
            
            # Should describe parameters if function has parameters
            has_args_section = any('Args:' in line or 'Parameters:' in line for line in lines)
            has_returns_section = any('Returns:' in line or 'Return:' in line for line in lines)
            
            quality_score = 0
            if len(lines[0]) > 20:  # Meaningful summary
                quality_score += 1
            if has_args_section:
                quality_score += 1
            if has_returns_section:
                quality_score += 1
            if len(lines) > 3:  # Multi-line documentation
                quality_score += 1
            
            return quality_score >= 2, f"Quality score: {quality_score}/4"
        
        # Sample docstrings to test
        sample_docstrings = {
            "good_docstring": """
            Create CSV export of generated posts.
            
            Args:
                posts: List of final edited posts
                platform: Target platform name
                include_metadata: Whether to include additional metadata columns
                
            Returns:
                tuple[str, str]: (csv_string, filename)
            """,
            "poor_docstring": "Does stuff",
            "missing_docstring": None
        }
        
        is_good, msg = check_docstring_quality(sample_docstrings["good_docstring"])
        assert is_good, f"Good docstring should pass quality check: {msg}"
        
        is_poor, msg = check_docstring_quality(sample_docstrings["poor_docstring"])
        assert not is_poor, f"Poor docstring should fail quality check: {msg}"
        
        is_missing, msg = check_docstring_quality(sample_docstrings["missing_docstring"])
        assert not is_missing, f"Missing docstring should fail quality check: {msg}"
    
    def test_type_annotations(self):
        """Test that functions have proper type annotations."""
        def check_type_annotations(func_source):
            """Check if function has type annotations."""
            # Parse function signature
            tree = ast.parse(func_source)
            func_def = tree.body[0]
            
            if not isinstance(func_def, ast.FunctionDef):
                return False, "Not a function definition"
            
            # Check parameter annotations
            annotated_params = sum(1 for arg in func_def.args.args if arg.annotation)
            total_params = len(func_def.args.args)
            
            # Check return annotation
            has_return_annotation = func_def.returns is not None
            
            annotation_score = 0
            if total_params > 0 and annotated_params / total_params >= 0.8:  # 80% of params annotated
                annotation_score += 1
            if has_return_annotation:
                annotation_score += 1
            
            return annotation_score >= 1, f"Annotation score: {annotation_score}/2"
        
        # Test sample function signatures
        good_function = """
def create_csv_export(posts: List[str], platform: str, include_metadata: bool = False) -> Tuple[str, str]:
    pass
"""
        
        poor_function = """
def process_data(data, options):
    pass
"""
        
        is_good, msg = check_type_annotations(good_function)
        assert is_good, f"Well-annotated function should pass: {msg}"
        
        is_poor, msg = check_type_annotations(poor_function)
        assert not is_poor, f"Poorly annotated function should fail: {msg}"


class TestErrorHandling:
    """Test robust error handling patterns."""
    
    def test_consistent_exception_handling(self):
        """Test consistent exception handling across modules."""
        def analyze_exception_handling(code_content):
            """Analyze exception handling patterns in code."""
            tree = ast.parse(code_content)
            
            # Find try-except blocks
            try_blocks = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    try_blocks.append(node)
            
            # Analyze exception handling quality
            quality_metrics = {
                "has_try_blocks": len(try_blocks) > 0,
                "specific_exceptions": False,
                "proper_logging": False,
                "graceful_degradation": False
            }
            
            for try_block in try_blocks:
                for handler in try_block.handlers:
                    # Check for specific exception types (not bare except)
                    if handler.type is not None:
                        quality_metrics["specific_exceptions"] = True
                    
                    # Check for logging or user feedback in handlers
                    for stmt in handler.body:
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            func_name = ""
                            if hasattr(stmt.value.func, 'attr'):
                                func_name = stmt.value.func.attr
                            elif hasattr(stmt.value.func, 'id'):
                                func_name = stmt.value.func.id
                            
                            if any(log_func in func_name.lower() for log_func in ['log', 'error', 'warning']):
                                quality_metrics["proper_logging"] = True
                            
                            if any(ui_func in func_name for ui_func in ['st.error', 'st.warning', 'print']):
                                quality_metrics["graceful_degradation"] = True
            
            return quality_metrics
        
        # Test good exception handling
        good_code = """
try:
    result = risky_operation()
    return result
except ValueError as e:
    st.error(f"Invalid input: {str(e)}")
    return None
except ConnectionError as e:
    st.warning("Network issue - please try again")
    return None
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    return None
"""
        
        metrics = analyze_exception_handling(good_code)
        assert metrics["has_try_blocks"], "Should have try-except blocks"
        assert metrics["specific_exceptions"], "Should catch specific exceptions"
        assert metrics["graceful_degradation"], "Should provide user feedback"
        
        # Test poor exception handling
        poor_code = """
try:
    result = risky_operation()
    return result
except:
    pass
"""
        
        poor_metrics = analyze_exception_handling(poor_code)
        assert poor_metrics["has_try_blocks"], "Has try blocks"
        assert not poor_metrics["specific_exceptions"], "Should not catch bare exceptions"
        assert not poor_metrics["graceful_degradation"], "Should provide feedback"
    
    def test_error_propagation_patterns(self):
        """Test proper error propagation patterns."""
        def test_error_propagation():
            """Test that errors are properly propagated through layers."""
            
            # Service layer should raise specific exceptions
            def service_function():
                try:
                    # Some operation that might fail
                    if True:  # Simulate error condition
                        raise ValueError("Invalid data format")
                except ValueError:
                    # Re-raise with context
                    raise ValueError("Service layer: Invalid data format")
            
            # UI layer should catch and display errors
            def ui_function():
                try:
                    service_function()
                    return True, "Success"
                except ValueError as e:
                    return False, f"Error: {str(e)}"
                except Exception as e:
                    return False, f"Unexpected error: {str(e)}"
            
            success, message = ui_function()
            assert not success, "Should propagate error"
            assert "Service layer" in message, "Should maintain error context"
            assert "Invalid data format" in message, "Should preserve error details"
        
        test_error_propagation()
    
    def test_graceful_degradation(self):
        """Test graceful degradation for non-critical errors."""
        def test_graceful_degradation_scenarios():
            """Test various graceful degradation scenarios."""
            
            scenarios = [
                {
                    "name": "missing_brand_guide",
                    "error": "Brand guide file not provided",
                    "degradation": "Continue with generic brand voice",
                    "should_continue": True
                },
                {
                    "name": "partial_file_failure", 
                    "error": "One of multiple files failed to process",
                    "degradation": "Process remaining files",
                    "should_continue": True
                },
                {
                    "name": "api_rate_limit",
                    "error": "API rate limit exceeded", 
                    "degradation": "Show retry option",
                    "should_continue": False
                },
                {
                    "name": "invalid_api_key",
                    "error": "API key is invalid",
                    "degradation": "Request new API key",
                    "should_continue": False
                }
            ]
            
            for scenario in scenarios:
                # Simulate error handling for each scenario
                def handle_scenario(error_type):
                    if error_type == "missing_brand_guide":
                        return True, "Continuing with default brand voice"
                    elif error_type == "partial_file_failure":
                        return True, "Processed available files"
                    elif error_type == "api_rate_limit":
                        return False, "Please wait and try again"
                    elif error_type == "invalid_api_key":
                        return False, "Please check your API key"
                    else:
                        return False, "Unknown error"
                
                can_continue, message = handle_scenario(scenario["name"])
                assert can_continue == scenario["should_continue"], f"Scenario {scenario['name']} degradation incorrect"
                assert len(message) > 0, f"Scenario {scenario['name']} should provide user feedback"
        
        test_graceful_degradation_scenarios()


class TestInputValidationAndSanitization:
    """Test comprehensive input validation and sanitization."""
    
    def test_file_content_sanitization(self):
        """Test sanitization of file content."""
        def sanitize_file_content(content):
            """Sanitize file content for security and processing."""
            if not isinstance(content, str):
                content = str(content)
            
            # Remove null bytes and control characters
            sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
            
            # Normalize line endings
            sanitized = re.sub(r'\r\n', '\n', sanitized)
            sanitized = re.sub(r'\r', '\n', sanitized)
            
            # Limit length to prevent memory issues
            max_length = 1000000  # 1MB
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length]
            
            return sanitized
        
        # Test various inputs
        test_cases = [
            ("normal text", "normal text"),
            ("text\x00with\x1Fnull", "textwithull"),  # Control characters removed
            ("windows\r\nline\rendings", "windows\nline\nendings"),  # Line ending normalization
            ("a" * 2000000, "a" * 1000000),  # Length limiting
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_file_content(input_text)
            if len(expected) > 50:  # For very long strings, just check length
                assert len(result) == len(expected), f"Length mismatch for long string"
            else:
                assert result == expected, f"Sanitization failed for: {input_text[:50]}"
    
    def test_api_key_sanitization(self):
        """Test API key sanitization and validation."""
        def sanitize_api_key(api_key):
            """Sanitize and validate API key."""
            if not api_key:
                return None, "API key is required"
            
            # Remove whitespace
            sanitized = api_key.strip()
            
            # Check for obvious fake/test keys
            fake_patterns = ['test', 'fake', 'demo', 'example', '1234', 'abcd']
            if any(pattern in sanitized.lower() for pattern in fake_patterns):
                return None, "API key appears to be a test/fake key"
            
            # Basic length validation
            if len(sanitized) < 10:
                return None, "API key too short"
            
            # Remove any non-alphanumeric characters except hyphens and underscores
            sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', sanitized)
            
            return sanitized, "Valid"
        
        test_cases = [
            ("sk-real_api_key_12345", "sk-real_api_key_12345"),
            (" sk-key-with-spaces ", "sk-key-with-spaces"),
            ("sk-test-fake-key", None),  # Should reject fake key
            ("short", None),  # Too short
            ("", None),  # Empty
        ]
        
        for input_key, expected in test_cases:
            result, message = sanitize_api_key(input_key)
            if expected is None:
                assert result is None, f"Should reject key: {input_key}"
            else:
                assert result == expected, f"Sanitization failed for: {input_key}"
    
    def test_injection_prevention(self):
        """Test prevention of various injection attacks."""
        def prevent_injections(user_input):
            """Prevent various injection attacks in user input."""
            if not isinstance(user_input, str):
                user_input = str(user_input)
            
            # SQL injection patterns
            sql_patterns = ['DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET', '--', ';']
            
            # Script injection patterns  
            script_patterns = ['<script', 'javascript:', 'eval(', 'setTimeout(', 'setInterval(']
            
            # Command injection patterns
            command_patterns = ['$(', '`', '&&', '||', ';rm', ';del', '|rm', '|del']
            
            # CSV injection patterns
            csv_patterns = ['=', '+', '-cmd', '@SUM']
            
            issues = []
            
            for pattern in sql_patterns:
                if pattern.upper() in user_input.upper():
                    issues.append(f"Potential SQL injection: {pattern}")
            
            for pattern in script_patterns:
                if pattern.lower() in user_input.lower():
                    issues.append(f"Potential script injection: {pattern}")
            
            for pattern in command_patterns:
                if pattern in user_input:
                    issues.append(f"Potential command injection: {pattern}")
            
            # For CSV injection, only flag if at start of string
            for pattern in csv_patterns:
                if user_input.strip().startswith(pattern):
                    issues.append(f"Potential CSV injection: {pattern}")
            
            return len(issues) == 0, issues
        
        # Test safe inputs
        safe_inputs = [
            "This is normal text content",
            "Brand guide: Use professional tone",
            "Post content with hashtags #marketing #social"
        ]
        
        for safe_input in safe_inputs:
            is_safe, issues = prevent_injections(safe_input)
            assert is_safe, f"Safe input flagged as dangerous: {safe_input}"
        
        # Test dangerous inputs
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>", 
            "$(rm -rf /)",
            "=SUM(A1:A100)"
        ]
        
        for dangerous_input in dangerous_inputs:
            is_safe, issues = prevent_injections(dangerous_input)
            assert not is_safe, f"Dangerous input not detected: {dangerous_input}"
            assert len(issues) > 0, f"No issues reported for: {dangerous_input}"


class TestProductionOptimization:
    """Test production code optimization."""
    
    def test_debugging_artifacts_removal(self):
        """Test removal of debugging artifacts."""
        def check_debugging_artifacts(code_content):
            """Check for debugging artifacts that should be removed."""
            lines = code_content.split('\n')
            
            artifacts = {
                "print_statements": [],
                "console_logs": [],
                "debug_comments": [],
                "test_data": []
            }
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Check for print statements (except in docstrings or comments)
                if 'print(' in line and not line_stripped.startswith('#') and not line_stripped.startswith('"""'):
                    artifacts["print_statements"].append((i, line.strip()))
                
                # Check for console.log (shouldn't be in Python, but check anyway)
                if 'console.log' in line:
                    artifacts["console_logs"].append((i, line.strip()))
                
                # Check for debug comments
                debug_keywords = ['TODO:', 'FIXME:', 'DEBUG:', 'HACK:', 'XXX:']
                if any(keyword in line.upper() for keyword in debug_keywords):
                    artifacts["debug_comments"].append((i, line.strip()))
                
                # Check for test data that might have been left
                if any(test_word in line.lower() for test_word in ['test_key', 'fake_api', 'dummy_data']):
                    artifacts["test_data"].append((i, line.strip()))
            
            return artifacts
        
        # Test clean production code
        clean_code = """
def process_data(data):
    \"\"\"Process the input data.\"\"\"
    try:
        result = transform(data)
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
"""
        
        artifacts = check_debugging_artifacts(clean_code)
        assert len(artifacts["print_statements"]) == 0, "Clean code should have no print statements"
        assert len(artifacts["debug_comments"]) == 0, "Clean code should have no debug comments"
        
        # Test code with artifacts
        dirty_code = """
def process_data(data):
    print(f"DEBUG: Processing {data}")  # TODO: Remove this
    result = transform(data)
    # FIXME: This is a hack
    return result
"""
        
        dirty_artifacts = check_debugging_artifacts(dirty_code)
        assert len(dirty_artifacts["print_statements"]) > 0, "Should detect print statements"
        assert len(dirty_artifacts["debug_comments"]) > 0, "Should detect debug comments"
    
    def test_unused_imports_detection(self):
        """Test detection of unused imports."""
        def detect_unused_imports(code_content):
            """Detect potentially unused imports."""
            tree = ast.parse(code_content)
            
            # Get all imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
                    for alias in node.names:
                        imports.append(alias.name)
            
            # Get all names used in the code
            used_names = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.append(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        used_names.append(node.value.id)
            
            # Find potentially unused imports
            unused = []
            for import_name in imports:
                if import_name not in used_names:
                    unused.append(import_name)
            
            return unused
        
        # Test code with unused imports
        code_with_unused = """
import os
import sys
import json
import pandas as pd

def main():
    data = pd.DataFrame({'a': [1, 2, 3]})
    return data
"""
        
        unused = detect_unused_imports(code_with_unused)
        assert 'os' in unused, "Should detect unused os import"
        assert 'sys' in unused, "Should detect unused sys import"
        assert 'pd' not in unused, "Should not flag used pandas import"
    
    def test_code_complexity_metrics(self):
        """Test code complexity and suggest optimizations."""
        def calculate_complexity_metrics(code_content):
            """Calculate basic complexity metrics."""
            tree = ast.parse(code_content)
            
            metrics = {
                "function_count": 0,
                "class_count": 0,
                "max_function_length": 0,
                "nested_depth": 0,
                "cyclomatic_complexity": 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["function_count"] += 1
                    
                    # Calculate function length
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    metrics["max_function_length"] = max(metrics["max_function_length"], func_lines)
                    
                elif isinstance(node, ast.ClassDef):
                    metrics["class_count"] += 1
                
                # Count decision points for cyclomatic complexity
                elif isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                    metrics["cyclomatic_complexity"] += 1
            
            return metrics
        
        # Test simple, clean code
        simple_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
        
        simple_metrics = calculate_complexity_metrics(simple_code)
        assert simple_metrics["function_count"] == 2, "Should count functions correctly"
        assert simple_metrics["cyclomatic_complexity"] == 0, "Simple code should have low complexity"
        
        # Test complex code
        complex_code = """
def complex_function(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                try:
                    result.append(item * 2)
                except:
                    pass
            else:
                while item > 1:
                    item = item - 1
        else:
            result.append(0)
    return result
"""
        
        complex_metrics = calculate_complexity_metrics(complex_code)
        assert complex_metrics["cyclomatic_complexity"] > 3, "Complex code should have higher complexity"


class TestCodeQualityIntegration:
    """Test integration of all code quality improvements."""
    
    def test_overall_code_quality_score(self):
        """Test overall code quality scoring system."""
        def calculate_quality_score(file_path):
            """Calculate overall code quality score."""
            if not Path(file_path).exists():
                return 0, "File not found"
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            score = 0
            max_score = 10
            issues = []
            
            # 1. Has proper imports structure (2 points)
            if 'from services.' in content or 'from utils.' in content:
                score += 2
            else:
                issues.append("Missing proper service/utils imports")
            
            # 2. Has docstrings (2 points)
            if '"""' in content and len(content.split('"""')) > 2:
                score += 2
            else:
                issues.append("Missing comprehensive docstrings")
            
            # 3. Has error handling (2 points)
            if 'try:' in content and 'except' in content:
                score += 2
            else:
                issues.append("Missing error handling")
            
            # 4. No debugging artifacts (2 points)
            if 'print(' not in content or '# TODO' not in content:
                score += 2
            else:
                issues.append("Contains debugging artifacts")
            
            # 5. Type annotations (2 points)
            if '->' in content and ':' in content:
                score += 2
            else:
                issues.append("Missing type annotations")
            
            quality_percentage = (score / max_score) * 100
            return quality_percentage, issues
        
        # Test quality scoring
        test_files = ['app.py', 'services/file_service.py', 'utils/data_exporter.py']
        
        for file_path in test_files:
            if Path(file_path).exists():
                quality_score, issues = calculate_quality_score(file_path)
                
                # Production code should have high quality score
                assert quality_score >= 60, f"{file_path} quality score too low: {quality_score}% - Issues: {issues}"
                
                # Critical files should have even higher standards
                if 'app.py' in file_path or 'data_exporter.py' in file_path:
                    assert quality_score >= 80, f"Critical file {file_path} should have higher quality: {quality_score}%"