# modules/diagram_mermaid.py
from modules.schema import Process
import re


def _sanitize(text: str) -> str:
    """
    Escape characters that break Mermaid syntax.
    More comprehensive sanitization for Mermaid labels.
    """
    if not text:
        return ""
    
    # Replace problematic characters
    text = text.replace('"', "'")           # Double quotes to single
    text = text.replace("\n", " ")          # Newlines to spaces
    text = text.replace("\r", " ")          # Carriage returns to spaces
    text = text.replace("[", "(")           # Square brackets to parentheses
    text = text.replace("]", ")")
    text = text.replace("{", "(")           # Curly brackets to parentheses
    text = text.replace("}", ")")
    text = text.replace("|", "/")           # Pipe to slash
    text = text.replace(";", ",")           # Semicolon to comma
    text = text.replace(":", "-")           # Colon to hyphen
    
    # Remove any remaining special characters that could break Mermaid
    # Allow letters, numbers, spaces, and common punctuation
    text = re.sub(r'[^\w\s\-_,.()/]', '', text)
    
    # Trim and normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def _generate_node_id(step_id: str) -> str:
    """
    Ensure node IDs are valid for Mermaid.
    Mermaid IDs should start with a letter and contain only alphanumeric, underscore, or hyphen.
    """
    # Remove any non-alphanumeric characters except hyphen and underscore
    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', step_id)
    
    # Ensure it starts with a letter (prefix if needed)
    if clean_id and not clean_id[0].isalpha():
        clean_id = 'N' + clean_id
    
    return clean_id or f"node_{step_id}"


def generate_mermaid(process: Process) -> str:
    """Generate Mermaid flowchart code from Process object."""
    lines = ["flowchart TD"]
    
    # Add title as comment (optional)
    if process.name:
        lines.append(f"%% Process: {_sanitize(process.name)}")
    
    # Track node IDs mapping
    node_map = {}
    
    # Add nodes
    for step in process.steps:
        node_id = _generate_node_id(step.id)
        node_map[step.id] = node_id
        
        label = _sanitize(step.title)
        
        # Truncate very long labels
        if len(label) > 50:
            label = label[:47] + "..."
        
        # Add actor if present
        if step.actor:
            actor = _sanitize(step.actor)
            label = f"{actor}: {label}"
        
        if step.is_decision:
            # Decision node (diamond)
            lines.append(f'    {node_id}{{{{{"  {label}  "}}}}}')
        else:
            # Regular node (rectangle with rounded corners)
            lines.append(f'    {node_id}["{label}"]')
    
    # Add edges
    if process.edges:
        lines.append("")
        for edge in process.edges:
            source_id = node_map.get(edge.source, edge.source)
            target_id = node_map.get(edge.target, edge.target)
            
            if edge.label:
                edge_label = _sanitize(edge.label)
                # Truncate very long edge labels
                if len(edge_label) > 30:
                    edge_label = edge_label[:27] + "..."
                lines.append(f'    {source_id} -->|"{edge_label}"| {target_id}')
            else:
                lines.append(f'    {source_id} --> {target_id}')
    
    return "\n".join(lines)
