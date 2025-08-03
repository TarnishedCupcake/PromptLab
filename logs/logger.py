import streamlit as st
import datetime
from typing import Optional, Dict, Any

class PromptLabLogger:
    """
    Centralized logging system for Prompt Lab
    Routes all log messages to Streamlit session state for display in Live Logs tab
    """
    
    def __init__(self, module_name: Optional[str] = None):
        self.module_name = module_name or "System"
        self._initialize_logs()
    
    def _initialize_logs(self):
        """Initialize the logs list in session state if it doesn't exist"""
        if 'logs' not in st.session_state:
            st.session_state.logs = []
    
    def log(self, message: str, level: str = "INFO", module: Optional[str] = None):
        """
        Add a log entry to the session state logs
        
        Args:
            message: The log message
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
            module: Module name (overrides default if provided)
        """
        self._initialize_logs()
        
        log_entry = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'module': module or self.module_name,
            'level': level.upper(),
            'message': message
        }
        
        # Add to session state logs
        st.session_state.logs.append(log_entry)
        
        # Keep only last 100 logs to prevent memory issues
        if len(st.session_state.logs) > 100:
            st.session_state.logs = st.session_state.logs[-100:]
    
    def info(self, message: str, module: Optional[str] = None):
        """Log an info message"""
        self.log(message, "INFO", module)
    
    def warning(self, message: str, module: Optional[str] = None):
        """Log a warning message"""
        self.log(message, "WARNING", module)
    
    def error(self, message: str, module: Optional[str] = None):
        """Log an error message"""
        self.log(message, "ERROR", module)
    
    def success(self, message: str, module: Optional[str] = None):
        """Log a success message"""
        self.log(message, "SUCCESS", module)
    
    def debug(self, message: str, module: Optional[str] = None):
        """Log a debug message"""
        self.log(message, "DEBUG", module)
    
    def get_logs(self, level_filter: Optional[str] = None, module_filter: Optional[str] = None) -> list:
        """
        Retrieve logs with optional filtering
        
        Args:
            level_filter: Filter by log level (INFO, WARNING, ERROR, SUCCESS, DEBUG)
            module_filter: Filter by module name
        
        Returns:
            List of filtered log entries
        """
        self._initialize_logs()
        
        logs = st.session_state.logs
        
        if level_filter:
            logs = [log for log in logs if log['level'] == level_filter.upper()]
        
        if module_filter:
            logs = [log for log in logs if log['module'] == module_filter]
        
        return logs
    
    def clear_logs(self):
        """Clear all logs from session state"""
        st.session_state.logs = []
        self.log("Logs cleared", "INFO", "Logger")
    
    def get_log_summary(self) -> Dict[str, Any]:
        """
        Get a summary of log statistics
        
        Returns:
            Dictionary with log statistics
        """
        self._initialize_logs()
        
        logs = st.session_state.logs
        
        summary = {
            'total_logs': len(logs),
            'by_level': {},
            'by_module': {},
            'recent_activity': []
        }
        
        # Count by level
        for log in logs:
            level = log['level']
            summary['by_level'][level] = summary['by_level'].get(level, 0) + 1
        
        # Count by module
        for log in logs:
            module = log['module']
            summary['by_module'][module] = summary['by_module'].get(module, 0) + 1
        
        # Get recent activity (last 10 logs)
        summary['recent_activity'] = logs[-10:] if logs else []
        
        return summary
    
    def export_logs(self, format_type: str = "json") -> str:
        """
        Export logs in specified format
        
        Args:
            format_type: Export format ("json", "csv", "txt")
        
        Returns:
            Formatted log data as string
        """
        self._initialize_logs()
        
        logs = st.session_state.logs
        
        if format_type.lower() == "json":
            import json
            return json.dumps(logs, indent=2, default=str)
        
        elif format_type.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=['timestamp', 'module', 'level', 'message'])
            writer.writeheader()
            writer.writerows(logs)
            
            return output.getvalue()
        
        elif format_type.lower() == "txt":
            text_lines = []
            for log in logs:
                line = f"[{log['timestamp']}] {log['level']} ({log['module']}): {log['message']}"
                text_lines.append(line)
            
            return '\n'.join(text_lines)
        
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def log_operation_start(self, operation: str, details: Optional[str] = None):
        """Log the start of an operation"""
        message = f"Starting operation: {operation}"
        if details:
            message += f" - {details}"
        self.log(message, "INFO")
    
    def log_operation_end(self, operation: str, success: bool = True, details: Optional[str] = None):
        """Log the end of an operation"""
        status = "completed successfully" if success else "failed"
        message = f"Operation {operation} {status}"
        if details:
            message += f" - {details}"
        
        level = "SUCCESS" if success else "ERROR"
        self.log(message, level)
    
    def log_user_action(self, action: str, details: Optional[str] = None):
        """Log a user action"""
        message = f"User action: {action}"
        if details:
            message += f" - {details}"
        self.log(message, "INFO")
    
    def log_system_event(self, event: str, details: Optional[str] = None):
        """Log a system event"""
        message = f"System event: {event}"
        if details:
            message += f" - {details}"
        self.log(message, "INFO")
    
    def log_performance_metric(self, metric_name: str, value: Any, unit: Optional[str] = None):
        """Log a performance metric"""
        message = f"Performance metric - {metric_name}: {value}"
        if unit:
            message += f" {unit}"
        self.log(message, "INFO")
    
    @staticmethod
    def get_module_logger(module_name: str) -> 'PromptLabLogger':
        """
        Factory method to create a logger for a specific module
        
        Args:
            module_name: Name of the module
        
        Returns:
            PromptLabLogger instance configured for the module
        """
        return PromptLabLogger(module_name)

# Convenience functions for quick logging
def log_info(message: str, module: str = "System"):
    """Quick info log"""
    logger = PromptLabLogger(module)
    logger.info(message)

def log_warning(message: str, module: str = "System"):
    """Quick warning log"""
    logger = PromptLabLogger(module)
    logger.warning(message)

def log_error(message: str, module: str = "System"):
    """Quick error log"""
    logger = PromptLabLogger(module)
    logger.error(message)

def log_success(message: str, module: str = "System"):
    """Quick success log"""
    logger = PromptLabLogger(module)
    logger.success(message)

# Module-specific logger instances
prompt_creator_logger = PromptLabLogger("Prompt Creator")
mutation_logger = PromptLabLogger("Mutation Lab")
simulator_logger = PromptLabLogger("Simulator")
analyzer_logger = PromptLabLogger("Analyzer")
red_team_logger = PromptLabLogger("Red Team")
